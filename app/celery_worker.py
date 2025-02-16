from celery import Celery
from app.config import REDIS_URL
from app.database import SessionLocal
from app.models import EventLog, Trigger
from datetime import datetime, timedelta
import uuid
import redis
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()

celery = Celery("tasks", broker=REDIS_URL, backend=REDIS_URL)
celery.conf.update(
    task_routes={
        "app.celery_worker.execute_scheduled_trigger": {"queue": "default"}
    }
)

@celery.task
def cleanup_event_logs():
    """Cleanup event logs every 2 hours by moving logs older 
    than 2 hours to "archived" status and deleting "archived" 
    logs older than 48 hours."""
    try:
        print("Begin Cleanup")
        db = SessionLocal()
        now = datetime.utcnow()

        # Move "active" logs older than 2 hours to "archived"
        two_hours_ago = now - timedelta(hours=2)
        db.query(EventLog).filter(EventLog.status == "active", EventLog.executed_at < two_hours_ago).update(
            {"status": "archived"}
        )

        # Delete "archived" logs older than 48 hours
        forty_eight_hours_ago = now - timedelta(hours = 48)
        db.query(EventLog).filter(EventLog.status == "archived", EventLog.executed_at < forty_eight_hours_ago).delete()
        db.commit()
        db.close()
        print("Event log cleanup completed")

    except Exception as e:
        print(f"Error during event log cleanup: {e}")


@celery.task(name = "execute_scheduled_trigger")
def execute_scheduled_trigger(trigger_id: str, recurring: bool = False, interval: int = 0, payload: dict = None):
    """
    Execute a scheduled trigger task.

    Args:
        trigger_id (str): The ID of the trigger to be executed.
        recurring (bool, optional): Indicates if the task is recurring. Defaults to False.
        interval (int, optional): The time interval in seconds for recurring tasks. Defaults to 0.
        payload (dict, optional): The payload associated with the trigger execution. Defaults to None.

    The function logs an event in the database with the trigger's execution details and 
    deletes the cached "active_logs" in Redis. If the trigger is recurring and the interval 
    is greater than 0, it schedules the task to be executed again after the specified interval, 
    updating the task_id in the database.

    Raises:
        Exception: If an error occurs during execution, it logs the error message.
    """
    print('Executing either scheduled or api trigger')
    redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)

    try:

        db = SessionLocal()
        event = EventLog(
            id=uuid.uuid4(),
            trigger_id=trigger_id,
            executed_at=datetime.utcnow(),
            status="active",
            payload=payload
        )
        print(f'Adding to event_logs db event: {event}')

        db.add(event)
        db.commit()
        op = redis_client.delete("active_logs")
        # If the trigger is recurring, schedule it again
        if recurring and interval > 0:
            # Store the latest task_id in the database
            trigger = db.query(Trigger).filter(Trigger.id == trigger_id).first()
            if trigger:
                new_task = execute_scheduled_trigger.apply_async(args=[trigger_id, trigger.recurring, interval], countdown=interval)
                print(f"Rescheduled trigger {trigger_id} with new task_id: {new_task.id}")
                trigger.task_id = new_task.id
                db.commit()
        db.close()

        print(f"Executed scheduled trigger: {trigger_id}")

    except Exception as e:
        print(f"Error executing scheduled trigger: {e}")

# Schedule cleanup task to run every 30 minutes
scheduler.add_job(cleanup_event_logs, 'interval', minutes=30)
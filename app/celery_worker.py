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

# celery.conf.beat_schedule = {
#     "cleanup-event-logs": {
#         "task": "app.celery_worker.cleanup_event_logs",
#         "schedule": crontab(minute="*/30"),  # Runs every 30 minutes
#     },
# }


@celery.task
def cleanup_event_logs():
    db = SessionLocal()
    now = datetime.utcnow()

    # ✅ Move "active" logs older than 2 hours to "archived"
    two_hours_ago = now - timedelta(hours=2)
    ans = db.query(EventLog).filter(EventLog.status == "active", EventLog.executed_at < two_hours_ago).update(
        {"status": "archived"}
    )

    # ✅ Delete "archived" logs older than 48 hours
    forty_eight_hours_ago = now - timedelta(hours = 48)
    ans_2 = db.query(EventLog).filter(EventLog.status == "archived", EventLog.executed_at < forty_eight_hours_ago).delete()
    db.commit()
    db.close()
    print("✅ Event log cleanup completed")


@celery.task(name = "execute_scheduled_trigger")
def execute_scheduled_trigger(trigger_id: str, recurring: bool = False, interval: int = 0, payload: dict = None):
    print('IS THIS FUNCTION EVENT CALLED?')
    print('HELLO!')
    redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)

    try:
        print('IN EXECUTE')

        db = SessionLocal()
        print('HELLOOOOO')
        event = EventLog(
            id=uuid.uuid4(),
            trigger_id=trigger_id,
            executed_at=datetime.utcnow(),
            status="active",
            payload=payload
        )
        print(event)

        db.add(event)
        db.commit()
        op = redis_client.delete("active_logs")
        print('THIS IS OUTPUT OF REDIS CLI DELETE', op)
        # If the trigger is recurring, schedule it again
        if recurring and interval > 0:
            # ✅ Store the latest task_id in the database
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
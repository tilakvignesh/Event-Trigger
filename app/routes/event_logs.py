from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from datetime import datetime, timedelta
from app.database import SessionLocal
from app.models import EventLog
from app.config import REDIS_URL
import redis
import json

router = APIRouter()

redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_cached_logs():
    """Fetches active logs from Redis cache, if available.

    Returns:
        A list of dictionaries containing active logs, or None if cache is empty.
    """
    
    cached_data = redis_client.get("active_logs")
    if cached_data:
        return json.loads(cached_data)  # Return cached result if exists
    return None

# Store Active Logs in Redis (Expire in 60 seconds)
def cache_active_logs(data):
    """Store a list of active logs in Redis cache.

    Args:
        data (list): A list of dictionaries containing active logs.
    """
    redis_client.set("active_logs", json.dumps(data))

# Get Active Logs (Last 2 Hours)
@router.get("/")
def get_active_logs(db: Session = Depends(get_db)):
    """
    Get all active event logs from the last 2 hours.

    First checks if there is a cached version of the active logs in Redis.
    If the cache exists, it returns the cached result.
    If the cache does not exist, it fetches the active logs from the database, caches them in Redis for 60 seconds, and returns the result.

    Returns:
        A list of dictionaries containing the active logs, each with keys for the log's ID, trigger type, trigger name, trigger recurring flag, executed_at timestamp, status, and payload.

    Raises:
        HTTPException: If there is an internal server error
    """
    try:
        print('fetching active logs')
        cached_logs = get_cached_logs()
        if cached_logs:
            print(f'fetched cached logs from redis: {cached_logs}')
            return cached_logs
        
        logs = db.query(EventLog).options(joinedload(EventLog.trigger)).filter(EventLog.status == "active").all()
        # Populating trigger info in event_log reponse
        logs_dict = [
            {
                "id": str(log.id),
                "trigger": {
                "trigger_type": str(log.trigger.type),
                "trigger_name": str(log.trigger.name),
                "trigger_recurring": str(log.trigger.recurring),
                "trigger_schedule": log.trigger.schedule,
                "payload": log.trigger.payload
                },
                "executed_at": str(log.executed_at),
                "status": log.status           
            }
            for log in logs
        ]
        print(f'fetched active logs from db: {logs_dict}')
        cache_active_logs(logs_dict) # Cache updated event_logs
        return logs_dict
    except Exception as e:
        print('Exception occurred:', e)
        raise HTTPException(status_code=500, detail='Internal server error')

# Get Archived Logs (2 to 48 Hours Old)
@router.get("/archived")
def get_archived_logs( db: Session = Depends(get_db)):
    """
    Retrieve archived event logs executed between 2 and 48 hours ago.

    Args:
        db: The database session (automatically provided by FastAPI dependency injection).

    Returns:
        A list of archived event logs that were executed between 2 and 48 hours ago.

    Raises:
        HTTPException: If there is an internal server error.
    """
    try:
        print('fetching archived logs')
        now = datetime.utcnow()
        two_hours_ago = now - timedelta(hours=2)
        forty_eight_hours_ago = now - timedelta(hours=48)
        logs = db.query(EventLog).filter(
            EventLog.status == "archived",
            EventLog.executed_at < two_hours_ago,
            EventLog.executed_at >= forty_eight_hours_ago
        ).all()
        return logs
    except Exception as e:
        print('Exception occurred:', e)
        raise HTTPException(status_code=500, detail='Internal server error')

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
print(f'redis client: {redis_client}')

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_cached_logs():
    cached_data = redis_client.get("active_logs")
    if cached_data:
        return json.loads(cached_data)  # ✅ Return cached result if exists
    return None

# ✅ Store Active Logs in Redis (Expire in 60 seconds)
def cache_active_logs(data):
    redis_client.set("active_logs", json.dumps(data))

# ✅ Get Active Logs (Last 2 Hours)
@router.get("/")
def get_active_logs(db: Session = Depends(get_db)):
    print('hello')
    print('THIS IS REDIS USR', REDIS_URL)
    cached_logs = get_cached_logs()
    if cached_logs:
        print(cached_logs)
        print('DID THIS EXECUTE?')
        return cached_logs
    two_hours_ago = datetime.utcnow() - timedelta(hours=2)
    
    logs = db.query(EventLog).options(joinedload(EventLog.trigger)).filter(EventLog.status == "active").all()
    logs_dict = [
        {
            "id": str(log.id),
            "trigger_type": str(log.trigger.type),
            "trigger_name": str(log.trigger.name),
            "trigger_recurring": str(log.trigger.recurring),
            "executed_at": str(log.executed_at),
            "status": log.status,
            "payload": log.payload
        }
        for log in logs
    ]
    print(logs_dict)
    cache_active_logs(logs_dict)
    return logs

# ✅ Get Archived Logs (2 to 48 Hours Old)
@router.get("/archived")
def get_archived_logs( db: Session = Depends(get_db)):
    now = datetime.utcnow()
    two_hours_ago = now - timedelta(hours=2)
    forty_eight_hours_ago = now - timedelta(hours=48)
    logs = db.query(EventLog).filter(
        EventLog.status == "archived",
        EventLog.executed_at < two_hours_ago,
        EventLog.executed_at >= forty_eight_hours_ago
    ).all()
    return logs

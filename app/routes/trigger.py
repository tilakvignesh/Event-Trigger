from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Trigger, TriggerType
from app.schema import TriggerCreate, TriggerResponse
from app.celery_worker import execute_scheduled_trigger
from celery.result import AsyncResult

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=TriggerResponse)
def create_trigger(trigger: TriggerCreate, db: Session = Depends(get_db)):
    new_trigger = Trigger(name=trigger.name, type=trigger.type, schedule=trigger.schedule, payload=trigger.payload, recurring=trigger.recurring, test=trigger.test)
    db.add(new_trigger)
    db.commit()
    db.refresh(new_trigger)
    task_id = None
    active = True
       # Schedule Celery task if it's a scheduled trigger
    if trigger.type == "scheduled" and trigger.schedule:
        print(f"Scheduling trigger {new_trigger.id} to run in {trigger.schedule} seconds.")
        delay = int(trigger.schedule)  # Assuming input is in seconds
        print(delay)
        task = execute_scheduled_trigger.apply_async(args=[new_trigger.id, trigger.recurring, delay, None], countdown=delay)
        task_id = task.id
        if trigger.test:
            active = False


    new_trigger.task_id = task_id
    new_trigger.active = active
    db.commit()
    return new_trigger

@router.get("/", response_model=list[TriggerResponse])
def get_triggers(db: Session = Depends(get_db)):
    triggers = db.query(Trigger).filter(Trigger.active == True).all()
    return triggers

@router.post("/{trigger_id}")
def update_trigger(trigger_id: str, update_data: dict, db: Session = Depends(get_db)):
    db_trigger = db.query(Trigger).filter(Trigger.id == trigger_id.strip()).first()
    if not db_trigger:
        raise HTTPException(status_code=404, detail="Trigger not found")
    for key in update_data:
        setattr(db_trigger, key, update_data[key])
    db.commit()
    return {"message": "Trigger updated successfully"}



@router.delete("/{trigger_id}")
def delete_trigger(trigger_id: str, db: Session = Depends(get_db)):
    trigger = db.query(Trigger).filter(Trigger.id == trigger_id.strip()).first()
    if not trigger:
        raise HTTPException(status_code=404, detail="Trigger not found")

    trigger.active = False
    trigger.recurring = False
    db.commit()
    return {"message": "Trigger deleted successfully"}


@router.post("/{trigger_id}/execute")
def execute_trigger(trigger_id: str, db: Session = Depends(get_db)):
    trigger = db.query(Trigger).filter(Trigger.id == trigger_id, Trigger.type == "API").first()
    
    if not trigger:
        raise HTTPException(status_code=404, detail="Trigger not found or not of type API")

    # Send task to Celery immediately
    print(f'trigger: {trigger.payload}')
    task = execute_scheduled_trigger.apply_async(args=[trigger_id, False, 0, trigger.payload])
    if trigger.test:
        trigger.active = False
        db.commit()
    
    return {"message": "Trigger executed", "task_id": task.id}


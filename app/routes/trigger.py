from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Trigger
from app.schema import TriggerCreate, TriggerResponse, TriggerUpdate
from app.celery_worker import execute_scheduled_trigger

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=TriggerResponse)
def create_trigger(trigger: TriggerCreate, db: Session = Depends(get_db)):
    """
    Create a new trigger. NOTE: FOR SCHEDULED TRIGGERS, THE SCHEDULE IS IN SECONDS

    Args:
        trigger: The trigger to be created
        db: The database session

    Returns:
        The newly created trigger

    Raises:
        HTTPException: If there is an internal server error
    """
    print(f'Running create trigger with payload: {trigger}')
    try:
        new_trigger = Trigger(name=trigger.name, type=trigger.type, schedule=trigger.schedule, payload=trigger.payload, recurring=trigger.recurring, test=trigger.test) # Create new trigger
        db.add(new_trigger)
        db.commit()
        db.refresh(new_trigger)
        task_id = None
        active = True
        # Schedule Celery task if it's a scheduled trigger
        if trigger.type == "scheduled" and trigger.schedule:
            print(f"Scheduling trigger {new_trigger.id} to run in {trigger.schedule} seconds.")
            delay = int(trigger.schedule)  # Assuming input is in seconds
            task = execute_scheduled_trigger.apply_async(args=[new_trigger.id, trigger.recurring, delay, None], countdown=delay)
            task_id = task.id
            if trigger.test:
                active = False


        new_trigger.task_id = task_id
        new_trigger.active = active
        db.commit()
        return new_trigger
    except Exception as e:
        print('Excetion occurred:', e)
        raise HTTPException(status_code=500, detail='Internal server error')

@router.get("/", response_model=list[TriggerResponse])
def get_triggers(db: Session = Depends(get_db)):
    """
    Get all active triggers.

    Returns:
        A list of active triggers

    Raises:
        HTTPException: If there is an internal server error
    """
    
    try:
        print('Getting all active triggers')
        triggers = db.query(Trigger).filter(Trigger.active == True).all()
        return triggers
    except Exception as e:
        print('Excetion occurred:', e)
        raise HTTPException(status_code=500, detail='Internal server error')

@router.post("/{trigger_id}")
def update_trigger(trigger_id: str, update_data: TriggerUpdate, db: Session = Depends(get_db)):
    """
    Update an existing trigger with new data.

    Args:
        trigger_id: The ID of the trigger to be updated.
        update_data: A dictionary containing the fields to be updated and their new values.
        db: The database session (automatically provided by FastAPI dependency injection).

    Returns:
        A success message indicating the trigger was updated.

    Raises:
        HTTPException: If the trigger with the given ID is not found.
    """

    try:

        db_trigger = db.query(Trigger).filter(Trigger.id == trigger_id.strip()).first()
        if not db_trigger:
            raise HTTPException(status_code=404, detail="Trigger not found")
        for key, value in update_data.dict(exclude_unset=True).items():
            print('key: ', key, 'value: ', value)
            setattr(db_trigger, key, value)
        db.commit()
        return {"message": "Trigger updated successfully"}
    except Exception as e:
        print('Exception occurred:', e)
        raise HTTPException(status_code=500, detail='Internal server error')




@router.delete("/{trigger_id}")
def delete_trigger(trigger_id: str, db: Session = Depends(get_db)):
    """
    Delete a trigger.

    Args:
        trigger_id: The ID of the trigger to be deleted.
        db: The database session (automatically provided by FastAPI dependency injection).

    Returns:
        A success message indicating the trigger was deleted.

    Raises:
        HTTPException: If the trigger with the given ID is not found.
    """
    try:
        print(f'Soft deleting trigger with id: {trigger_id}')
        trigger = db.query(Trigger).filter(Trigger.id == trigger_id.strip()).first()
        if not trigger:
            raise HTTPException(status_code=404, detail="Trigger not found")

        trigger.active = False
        trigger.recurring = False
        db.commit()
        return {"message": "Trigger deleted successfully"}
    except Exception as e:
        print('Exception occurred:', e)
        raise HTTPException(status_code=500, detail='Internal server error')


@router.post("/{trigger_id}/execute")
def execute_trigger(trigger_id: str, db: Session = Depends(get_db)):
    """
    Execute a trigger of type "API" immediately.

    Args:
        trigger_id: The ID of the trigger to be executed
        db: The database session (automatically provided by FastAPI dependency injection)

    Returns:
        A dictionary containing a success message and the ID of the Celery task that was created.

    Raises:
        HTTPException: If the trigger with the given ID is not found or is not of type "API"
    """
    try:
        print(f'Executing api trigger with id: {trigger_id}')
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
    except Exception as e:
        print('Exception occurred:', e)
        raise HTTPException(status_code=500, detail='Internal server error')


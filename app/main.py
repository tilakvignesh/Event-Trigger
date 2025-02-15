from fastapi import FastAPI
from app.routes import trigger, event_logs
from app.models import init_db

app = FastAPI()
init_db()
app.include_router(trigger.router, prefix="/triggers", tags=["Triggers"])
app.include_router(event_logs.router, prefix="/event-logs", tags=["Event Logs"])

@app.get("/")
def read_root():
    return {"message": "Event Trigger API is running!"}

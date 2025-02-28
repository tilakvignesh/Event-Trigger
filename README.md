## Architecture:
![Backend Architecture](images/Architecture.png)

## Deployed Solution Link
[Here](http://13.201.189.39:8000/)

## Local Setup 

1. git clone https://github.com/tilakvignesh/Event-Trigger.git

2. Create a .env file in the root directory consisting of 
``` 
DATABASE_URL=postgresql://postgres:postgres@db/eventdb
REDIS_URL=redis://redis:6379/0
```

3. Ensure you have docker installed.

4. run ``` docker-compose up --build -d ```

5. Verify it's run properly with ``` docker ps -a ```

![Docker ps -a output screenshot](images/docker.png)

6. If everything seems fine, FastAPI should be running now at http://127.0.0.1:8000
7. You can view and interact with the same at http://127.0.0.1:8000/docs


## Endpoint Structures

- You can view the same details breakdown in http://localhost:8000/docs

### GET /triggers
- Input: None
- Output: Gets all triggers

### POST /triggers

- Input: Trigger payload.
    - Example:
        ``` 
            {
            "name": "string",
            "type": "scheduled",
            "schedule": 0,
            "payload": {
                "additionalProp1": "string",
                "additionalProp2": "string",
                "additionalProp3": "string"
            },
            "recurring": false,
            "test": false
            }
        ```
        - Field Names:
            - name: Name of the trigger
            - type: Can have type either "scheduled" or "api"
            - schedule: In seconds, for scheduled triggers
            - Payload: payload for API triggers
            - recurring: Bool, whether to re-run scheduled triggers or not
            - test: Bool, whether the trigger is a test trigger or not. 
- Output: Database response

   
### POST /triggers/<trigger_id>

- Input: trigger_id and update_dict 

- Output: Message on whether the trigger was updated

### DELETE /triggers/<trigger_id>
- Input: trigger_id
- Output: Delete confirmation message

### POST /triggers/<trigger_id>/execute

- Input: API trigger_id
- Output: Message on execution status

### GET /event-logs
- Input: None
- Output: Get all active event logs

### GET /event-logs/archived
- Input: None
- Output: Get all archived event logs
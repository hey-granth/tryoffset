# Offset Backend Exercise

This repository contains a tiny prototype of Offset's actual carbon credit ledger. It is hosted on Render and uses a PostgreSQL database hosted on Neon, on the link: 
https://tryoffset.onrender.com/


## Tech Stack 
- [FastAPI](https://fastapi.tiangolo.com/) (for building the API)
- [SQLAlchemy](https://www.sqlalchemy.org/) (ORM)
- [PostgreSQL](https://www.postgresql.org/) ([Neon](https://www.neon.com/) as the database provider)
- [Render](https://render.com/) (for hosting the API)
- [Alembic](https://alembic.sqlalchemy.org/en/latest/) (for database migrations)
- [Pydantic](https://pydantic.dev/) (for data validation and serialization)


## Features and Workflow
- small REST API (Python + FastAPI + Postgres)
- **`POST /records`** create a new carbon credit record and generates a unique deterministic ID which ensures that same input always returns the same ID. Also, it creates adds an event `'created'` to the Events list.
- **`POST /records/{id}/retire`** takes record id as path parameter and retires the record if it exists and is not already retired. It also adds an event `'retired'` to the Events list.
- **`GET /records/{id}`** takes record id as path parameter and returns the record details if it exists.

## Task Documents
Following are the documents provided for the exercise:
- [Backend-Exercise.pdf](https://github.com/hey-granth/tryoffset/blob/main/task_docs/Backend-Exercise.pdf)
- [sample-registry.json](https://github.com/hey-granth/tryoffset/blob/main/task_docs/sample-registry.json)


## API Endpoints
### POST /records
Example input:
```json
{
    "project_name": "Waste-to-Energy Gujarat",
    "registry": "VCS",
    "vintage": 2018,
    "quantity": 110,
    "serial_number": "VCS-2220"
}
```
Gives the reponse:
```json
{
    "project_name": "Waste-to-Energy Gujarat",
    "registry": "VCS",
    "vintage": 2018,
    "quantity": 110,
    "serial_number": "VCS-2220",
    "id": "d7a2cacab49120fac68ef2217eb032a6bfb30cf06d71c4cfdae5e311a80ee571",
    "events": [
      {
        "event_type": "created",
        "timestamp": "2025-09-27T20:09:24.691883"
      }
    ]
}
```

### POST /records/{id}/retire
Giving the record id generated as a path parameter gives the following response:
```json
{
    "message": "Record retired"
}
```

### GET /records/{id}
Checking the records by giving id as the path parameter returns:
```json
{
    "project_name": "Mangrove Restoration Project",
    "registry": "VCS",
    "vintage": 2023,
    "quantity": 100,
    "serial_number": "VCS-0001",
    "id": "e95d72575713f08b5aafbcd9aa9d635857d778833a04030e946d52c51b4329b1",
    "events": [
        {
            "event_type": "retired",
            "timestamp": "2025-09-27T19:53:25.667446"
        },
        {
            "event_type": "retired",
            "timestamp": "2025-09-27T19:55:46.007494"
        }
    ]
}
```

## Important Links
- Postman API Documentation - https://documenter.getpostman.com/view/47102425/2sB3QDwYWx
- Postman Collection - https://substrack.postman.co/workspace/Team-Workspace~087953ad-6b39-4302-8aa9-26db97f01c7c/collection/47102425-c0a97fe7-0887-4dc1-a988-22ba81dd0c25?action=share&creator=47102425
- OpenAPI Spec - https://tryoffset.onrender.com/openapi.json

## Setup Instructions

1. Basic set up:
    ```
    git clone git@github.com:hey-granth/tryoffset.git
    cd tryoffset
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

2. Set up the database:
    - Create a free Neon account at https://neon.com/
    - Create a new project and get the connection string
    - Set the connection string as an environment variable:
      ```
      export DATABASE_URL="your_connection_string"
      ```

3. Run the migrations to set up the database schema:
      ```
      alembic upgrade head
      ```

4. Run the FastAPI server:
      ```
      uvicorn app.main:app --reload
      ```

## Reflection Questions

### **How did you design the ID so it’s always the same for the same input?**

    `data: str = f"{record.project_name}_{record.record_registry}_{record.vintage}_{record.serial_number}"`

   I concatenated key fields (`project_name`, `registry`, `vintage`, `serial_number`) and generated a SHA256 hash. This ensures deterministic, unique IDs without collisions in normal use. If the information changes, a new ID is generated.

### **Why did you use an event log instead of updating the record directly?**

The event log ensures that nothing is ever deleted to enhance transparency within the market and the companies (that'll buy carbon credits).

### **If two people tried to retire the same credit at the same time, what would break?**

Race condition will occur, where both the requests would find for an existing 'retired' event and not find one, leading to both requests creating a 'retired' event. This is not what any sane person would want.

### **How would you fix it?**

This can be countered by applying atomic transactions, using `db.flush()` instead of `db.commit()` so that the transactions are rolled back in case of an IntegrityError and of course using unique and primary key constraints appropriately.


## Side Notes:
- The pdf mentioned the life cycle of events to be created -> sold -> retired. However, I couldn't figure out where or how to implement this while being in the boundaries of the given task. Hence, I only implemented the 'created' and 'retired' events. But the code is structured in such a way that 'sold' event can also be easily added and integrated to the code base.
- The API was just a prototype, so applying rate limiting felt like an overkill. In case needed in actual a life-sized system, it can be implemented by using slowapi and Redis. I don't actually know how to implement this but can I can learn it quickly. :)
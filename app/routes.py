from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from . import models, schema
from .database import SessionLocal
from hashlib import sha256
from datetime import datetime


router = APIRouter()


# db connection from database.py
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# POST /records → Create a record with fields {project_name,
# registry, vintage, quantity}. Must generate a unique, deterministic ID (same input → same ID).
@router.post("/records", response_model=schema.RecordResponse)
def create_record(
    record: schema.CreateRecord, db: Session = Depends(get_db)
) -> schema.RecordResponse:
    record_id: str = create_id(record)
    db_record: models.Records = models.Records(
        id=record_id,
        project_name=record.project_name,
        record_registry=record.record_registry,
        vintage=record.vintage,
        quantity=record.quantity,
        serial_number=record.serial_number,
    )
    db.add(db_record)

    try:
        db.commit()
        db.refresh(db_record)

        # Add "created" event for new records
        created_event = models.Event(
            record_id=record_id, event_type="created", timestamp=datetime.now()
        )
        db.add(created_event)
        db.commit()
        db.refresh(db_record)

    # if the record already exists, return the existing record. IntegrityError will be raised if the
    # record already exists, as record is a primary key.
    except IntegrityError:
        db.rollback()
        existing_record = (
            db.query(models.Records).filter(models.Records.id == record_id).first()
        )
        return schema.RecordResponse.from_orm_record(existing_record)

    return schema.RecordResponse.from_orm_record(db_record)


# generates a unique, deterministic id
def create_id(record: schema.CreateRecord) -> str:
    data: str = f"{record.project_name}_{record.record_registry}_{record.vintage}_{record.serial_number}"
    return sha256(data.encode()).hexdigest()


# GET /records/{id} → Return full record details + all events.
@router.get("/records/{record_id}", response_model=schema.RecordResponse)
def get_record(record_id: str, db: Session = Depends(get_db)) -> schema.RecordResponse:
    record: models.Records | None = (
        db.query(models.Records).filter(models.Records.id == record_id).first()
    )
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return schema.RecordResponse.from_orm_record(record)


# POST /records/{id}/retire → Mark a record as “retired” by adding a new event (not updating the original record).
@router.post("/records/{record_id}/retire")
def retire_record(record_id: str, db: Session = Depends(get_db)) -> dict[str, str]:
    record: models.Records | None = (
        db.query(models.Records).filter(models.Records.id == record_id).first()
    )

    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    new_event: models.Event = models.Event(record_id=record_id, event_type="retired")
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    return {"message": "Record retired"}

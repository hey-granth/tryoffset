from pydantic import BaseModel, Field
from datetime import datetime


class EventsSchema(BaseModel):
    event_type: str
    timestamp: datetime

    class Config:
        from_attributes = True  # to read data even if it's not a dict, e.g., ORM model
        populate_by_name = (
            True  # to read data using field names even if aliases are set
        )


class CreateRecord(BaseModel):
    project_name: str
    record_registry: str = Field(
        ..., alias="registry"
    )  # set up an alias because registry is a declared keyword in SQLAlchemy declarative base
    vintage: int
    quantity: int
    serial_number: str


class RecordResponse(CreateRecord):
    id: str
    project_name: str
    record_registry: str = Field(..., alias="registry")
    vintage: int
    quantity: int
    serial_number: str
    events: list[EventsSchema] = []

    class Config:
        from_attributes = True  # orm_mode is deprecated
        populate_by_name = True  # allow_population_by_field_name is deprecated

    @classmethod
    def from_orm_record(cls, record):
        return cls(
            id=record.id,
            project_name=record.project_name,
            registry=record.record_registry,  # Use the field name explicitly
            vintage=record.vintage,
            quantity=record.quantity,
            serial_number=record.serial_number,
            events=[
                EventsSchema.model_validate(event, from_attributes=True)
                for event in record.events
            ],
        )

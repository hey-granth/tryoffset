from pydantic import BaseModel, Field
from datetime import datetime


class EventsSchema(BaseModel):
    event_type: str
    timestamp: datetime

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


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
    events: list[EventsSchema]

    class Config:
        orm_mode = True
        allow_population_by_field_name = True

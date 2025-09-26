from database import Base
from sqlalchemy import Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column


class Records(Base):
    __tablename__ = "records"

    id: Mapped[str] = mapped_column(String, primary_key=True)   # unique id to ensure no duplicate entries are created
    project_name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    record_registry: Mapped[str] = mapped_column("registry", String, nullable=False)
    vintage: Mapped[int] = mapped_column(Integer, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    serial_number: Mapped[str] = mapped_column("serial_number", nullable=False, unique=True)

    events = relationship("Event", back_populates="record")


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    record_id: Mapped[str] = mapped_column(String, ForeignKey("records.id"), nullable=False)
    event_type: Mapped[str] = mapped_column(String, nullable=False)
    timestamp: Mapped[DateTime] = mapped_column(DateTime, nullable=False)

    record = relationship("Record", back_populates="events")

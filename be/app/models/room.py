from sqlalchemy import Column, Integer, String, Enum, Numeric, Text, DateTime, func
from app.database import Base

class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, autoincrement=True)
    room_number = Column(String(10), unique=True, nullable=False)
    room_type = Column(Enum("single", "double", "suite", "family", name="room_types"), nullable=False, default="single")
    floor = Column(Integer, nullable=False, default=1)
    price_per_night = Column(Numeric(8, 2), nullable=False)
    capacity = Column(Integer, nullable=False, default=1)
    description = Column(Text, nullable=True)
    status = Column(Enum("available", "occupied", "cleaning", "maintenance", name="room_statuses"), nullable=False, default="available")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
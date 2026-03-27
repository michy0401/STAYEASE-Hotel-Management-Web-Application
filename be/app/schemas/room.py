from pydantic import BaseModel
from typing import Optional
from decimal import Decimal

class RoomCreate(BaseModel):
    room_number: str
    room_type: str
    floor: int
    price_per_night: Decimal
    capacity: int
    description: Optional[str] = None
    status: Optional[str] = "available"

class RoomUpdate(BaseModel):
    room_number: Optional[str] = None
    room_type: Optional[str] = None
    floor: Optional[int] = None
    price_per_night: Optional[Decimal] = None
    capacity: Optional[int] = None
    description: Optional[str] = None
    status: Optional[str] = None

class RoomOut(BaseModel):
    id: int
    room_number: str
    room_type: str
    floor: int
    price_per_night: Decimal
    capacity: int
    description: Optional[str] = None
    status: str

    class Config:
        from_attributes = True
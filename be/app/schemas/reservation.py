from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional, Literal
from decimal import Decimal

class ReservationCreate(BaseModel):
    room_id: int
    guest_id: int
    check_in_date: date
    check_out_date: date
    notes: Optional[str] = None

class ReservationStatusUpdate(BaseModel):
    status: Literal["checked_in", "checked_out", "cancelled"]

class ReservationOut(BaseModel):
    id: int
    room_id: int
    guest_id: int
    staff_id: int
    check_in_date: date
    check_out_date: date
    nightly_rate: Decimal
    total_amount: Decimal
    status: str
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
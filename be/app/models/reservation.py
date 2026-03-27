from sqlalchemy import Column, Integer, String, Enum, Numeric, Text, DateTime, Date, ForeignKey, func
from app.database import Base

class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    room_id = Column(Integer, ForeignKey("rooms.id", ondelete="RESTRICT"), nullable=False)
    guest_id = Column(Integer, ForeignKey("guests.id", ondelete="RESTRICT"), nullable=False)
    staff_id = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    check_in_date = Column(Date, nullable=False)
    check_out_date = Column(Date, nullable=False)
    nightly_rate = Column(Numeric(8, 2), nullable=False)
    total_amount = Column(Numeric(10, 2), nullable=False, default=0.00)
    status = Column(Enum("confirmed", "checked_in", "checked_out", "cancelled", name="reservation_statuses"), nullable=False, default="confirmed")
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
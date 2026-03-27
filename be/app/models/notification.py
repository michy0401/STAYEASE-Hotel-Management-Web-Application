from sqlalchemy import Column, Integer, String, Enum, Text, Boolean, DateTime, ForeignKey, func
from app.database import Base

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    type = Column(Enum("reservation_created", "guest_checked_in", "guest_checked_out", "reservation_cancelled", "general", name="notification_types"), nullable=False, default="general")
    is_read = Column(Boolean, nullable=False, default=False)
    related_reservation_id = Column(Integer, ForeignKey("reservations.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=func.now())
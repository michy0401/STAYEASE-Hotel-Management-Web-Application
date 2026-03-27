from sqlalchemy.orm import Session
from app.models.notification import Notification

def create(db: Session, user_id: int, title: str, message: str, ntype: str, related_reservation_id: int | None = None) -> Notification:
    db_notif = Notification(
        user_id=user_id,
        title=title,
        message=message,
        type=ntype,
        related_reservation_id=related_reservation_id
    )
    db.add(db_notif)
    db.commit()
    db.refresh(db_notif)
    return db_notif

def get_for_user(db: Session, user_id: int) -> list[Notification]:
    return db.query(Notification).filter(Notification.user_id == user_id).order_by(Notification.created_at.desc()).all()

def mark_read(db: Session, notification_id: int, user_id: int):
    notif = db.query(Notification).filter(Notification.id == notification_id, Notification.user_id == user_id).first()
    if notif:
        notif.is_read = True
        db.commit()
        db.refresh(notif)
    return notif
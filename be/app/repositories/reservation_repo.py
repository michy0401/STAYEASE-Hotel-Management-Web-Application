from sqlalchemy.orm import Session
from app.models.reservation import Reservation
from datetime import date
from decimal import Decimal

def create(db: Session, room_id: int, guest_id: int, staff_id: int, check_in_date: date, check_out_date: date, nightly_rate: Decimal, notes: str | None) -> Reservation:
    # Calculamos el total de la reserva
    days = (check_out_date - check_in_date).days
    total_amount = nightly_rate * Decimal(days)

    db_reservation = Reservation(
        room_id=room_id,
        guest_id=guest_id,
        staff_id=staff_id,
        check_in_date=check_in_date,
        check_out_date=check_out_date,
        nightly_rate=nightly_rate,
        total_amount=total_amount,
        notes=notes
    )
    db.add(db_reservation)
    db.commit()
    db.refresh(db_reservation)
    return db_reservation

def get_by_staff(db: Session, staff_id: int) -> list[Reservation]:
    return db.query(Reservation).filter(Reservation.staff_id == staff_id).all()

def get_all(db: Session) -> list[Reservation]:
    return db.query(Reservation).all()

def get_by_id(db: Session, reservation_id: int) -> Reservation | None:
    return db.query(Reservation).filter(Reservation.id == reservation_id).first()

def update_status(db: Session, reservation: Reservation, new_status: str) -> Reservation:
    reservation.status = new_status
    db.commit()
    db.refresh(reservation)
    return reservation
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.reservation import ReservationCreate, ReservationOut, ReservationStatusUpdate
from app.services import reservation_service
from app.routers.deps import get_current_user

router = APIRouter(prefix="/reservations", tags=["Reservations"])

@router.post("/", response_model=ReservationOut, status_code=status.HTTP_201_CREATED)
def create_reservation(data: ReservationCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    reservation = reservation_service.create_reservation(db, current_user.id, data)
    if not reservation:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Habitación no disponible o huésped no encontrado")
    return reservation

@router.get("/mine", response_model=list[ReservationOut])
def get_my_reservations(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return reservation_service.get_my_reservations(db, current_user.id)

@router.get("/", response_model=list[ReservationOut])
def get_all_reservations(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return reservation_service.get_all_reservations(db)

@router.patch("/{reservation_id}/status", response_model=ReservationOut)
def update_reservation_status(reservation_id: int, data: ReservationStatusUpdate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    reservation = reservation_service.update_reservation_status(db, reservation_id, current_user.id, data.status)
    if not reservation:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Transición de estado inválida o reserva no encontrada")
    return reservation
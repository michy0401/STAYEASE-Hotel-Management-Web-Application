from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services import auth_service, notification_service
from app.repositories import user_repo

router = APIRouter(prefix="/ws", tags=["WebSockets"])

@router.websocket("/notifications")
async def websocket_endpoint(websocket: WebSocket, token: str, db: Session = Depends(get_db)):
    # 1. Validar el token manualmente (porque los websockets no usan headers igual que HTTP)
    try:
        token_data = auth_service.decode_token(token)
        user = user_repo.get_by_id(db, token_data.user_id)
        if not user:
            raise Exception("User not found")
    except Exception:
        await websocket.close(code=1008) # 1008 = Policy Violation (No autorizado)
        return

    # 2. Aceptar la conexión y registrar al usuario
    await websocket.accept()
    notification_service.register_ws(user.id, websocket)

    try:
        # 3. Mantener la conexión viva esperando mensajes
        while True:
            # Nuestro servidor solo empuja datos, ignora lo que envía el cliente
            _ = await websocket.receive_text()
    except WebSocketDisconnect:
        # 4. Limpiar cuando el usuario cierra la pestaña
        notification_service.unregister_ws(user.id)
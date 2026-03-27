from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, rooms, guests, reservations, ws

app = FastAPI(title="StayEase API", description="Hotel Management System")

# Permitir que nuestro Frontend en Flask (puerto 5000) pueda hablar con este Backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5000", "http://fe:5000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir todas las "Ventanillas"
app.include_router(auth.router)
app.include_router(rooms.router)
app.include_router(guests.router)
app.include_router(reservations.router)
app.include_router(ws.router)

@app.get("/health")
def health_check():
    return {"status": "ok"}
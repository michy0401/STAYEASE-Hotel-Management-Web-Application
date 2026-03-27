import os, requests
from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = "frontend_secret_key"
API = os.getenv("API_BASE_URL", "http://be:8000") # Docker conecta los contenedores con este nombre

def auth_headers():
    token = session.get("token")
    return {"Authorization": f"Bearer {token}"} if token else {}

# --- AUTENTICACIÓN ---

@app.route("/")
def index():
    return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        data = {
            "username": request.form.get("username"),
            "email": request.form.get("email"),
            "password": request.form.get("password"),
            "full_name": request.form.get("full_name")
        }
        resp = requests.post(f"{API}/auth/register", json=data)
        if resp.status_code == 201:
            flash("Registro exitoso. Por favor inicia sesión.", "success")
            return redirect(url_for("login"))
        else:
            flash(f"Error: {resp.json().get('detail', 'No se pudo registrar')}", "error")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        data = {
            "username": request.form.get("username"),
            "password": request.form.get("password")
        }
        resp = requests.post(f"{API}/auth/login", json=data)
        if resp.status_code == 200:
            session["token"] = resp.json().get("access_token")
            session["username"] = data["username"]
            return redirect(url_for("dashboard"))
        else:
            flash("Credenciales inválidas", "error")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# --- DASHBOARD ---

@app.route("/dashboard")
def dashboard():
    if "token" not in session: return redirect(url_for("login"))
    resp = requests.get(f"{API}/reservations/mine", headers=auth_headers())
    reservations = resp.json() if resp.status_code == 200 else []
    return render_template("dashboard.html", reservations=reservations)

# --- HABITACIONES (ROOMS) ---

@app.route("/rooms")
def rooms():
    if "token" not in session: return redirect(url_for("login"))
    resp = requests.get(f"{API}/rooms/", headers=auth_headers())
    rooms_data = resp.json() if resp.status_code == 200 else []
    return render_template("rooms.html", rooms=rooms_data)

@app.route("/rooms/add", methods=["GET", "POST"])
def add_room():
    if "token" not in session: return redirect(url_for("login"))
    if request.method == "POST":
        data = {
            "room_number": request.form.get("room_number"),
            "room_type": request.form.get("room_type"),
            "floor": int(request.form.get("floor", 1)),
            "price_per_night": float(request.form.get("price_per_night", 0)),
            "capacity": int(request.form.get("capacity", 1)),
            "description": request.form.get("description"),
            "status": request.form.get("status", "available")
        }
        resp = requests.post(f"{API}/rooms/", json=data, headers=auth_headers())
        if resp.status_code == 201:
            flash("Habitación agregada exitosamente", "success")
            return redirect(url_for("rooms"))
        else:
            flash(f"Error: {resp.json().get('detail')}", "error")
    return render_template("add_room.html")

@app.route("/rooms/<int:room_id>/status", methods=["POST"])
def update_room_status(room_id):
    if "token" not in session: return redirect(url_for("login"))
    status_val = request.form.get("status")
    resp = requests.patch(f"{API}/rooms/{room_id}/status", json={"status": status_val}, headers=auth_headers())
    if resp.status_code == 422:
        flash("Valor de estado inválido", "error")
    return redirect(url_for("rooms"))

# --- HUÉSPEDES (GUESTS) ---

@app.route("/guests")
def guests():
    if "token" not in session: return redirect(url_for("login"))
    resp = requests.get(f"{API}/guests/", headers=auth_headers())
    guests_data = resp.json() if resp.status_code == 200 else []
    return render_template("guests.html", guests=guests_data)

@app.route("/guests/add", methods=["GET", "POST"])
def add_guest():
    if "token" not in session: return redirect(url_for("login"))
    if request.method == "POST":
        data = {
            "full_name": request.form.get("full_name"),
            "email": request.form.get("email"),
            "phone": request.form.get("phone"),
            "document_id": request.form.get("document_id")
        }
        resp = requests.post(f"{API}/guests/", json=data, headers=auth_headers())
        if resp.status_code == 201:
            flash("Huésped agregado exitosamente", "success")
            return redirect(url_for("guests"))
        elif resp.status_code == 409:
            flash("Ya existe un huésped con ese correo electrónico", "error")
        else:
            flash("Error al agregar huésped", "error")
    return render_template("add_guest.html")

# --- RESERVAS (RESERVATIONS) ---

@app.route("/reservations")
def reservations():
    if "token" not in session: return redirect(url_for("login"))
    resp = requests.get(f"{API}/reservations/", headers=auth_headers())
    reservations_data = resp.json() if resp.status_code == 200 else []
    return render_template("reservations.html", reservations=reservations_data)

@app.route("/reservations/new", methods=["GET", "POST"])
def new_reservation():
    if "token" not in session: return redirect(url_for("login"))
    
    if request.method == "POST":
        data = {
            "room_id": int(request.form.get("room_id")),
            "guest_id": int(request.form.get("guest_id")),
            "check_in_date": request.form.get("check_in_date"),
            "check_out_date": request.form.get("check_out_date"),
            "notes": request.form.get("notes")
        }
        resp = requests.post(f"{API}/reservations/", json=data, headers=auth_headers())
        if resp.status_code == 201:
            flash("Reserva creada exitosamente", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Error: Habitación no disponible o huésped no encontrado", "error")
            
    # Cuando entra por GET: Cargar datos para los menús desplegables
    rooms_resp = requests.get(f"{API}/rooms/available", headers=auth_headers())
    guests_resp = requests.get(f"{API}/guests/", headers=auth_headers())
    
    available_rooms = rooms_resp.json() if rooms_resp.status_code == 200 else []
    all_guests = guests_resp.json() if guests_resp.status_code == 200 else []
    
    return render_template("new_reservation.html", rooms=available_rooms, guests=all_guests)

@app.route("/reservations/<int:reservation_id>/status", methods=["POST"])
def update_reservation_status(reservation_id):
    if "token" not in session: return redirect(url_for("login"))
    status_val = request.form.get("status")
    resp = requests.patch(f"{API}/reservations/{reservation_id}/status", json={"status": status_val}, headers=auth_headers())
    if resp.status_code == 422:
        flash("Transición de estado inválida", "error")
    
    # Redirigir a la página donde estábamos antes (Dashboard o Lista de reservas)
    return redirect(request.referrer or url_for("reservations"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
import os
from flask import Flask, render_template
from datetime import datetime
from flask_apscheduler import APScheduler

# Modelos y Base de Datos
from models import db, Student

# Blueprints (Rutas)
from routes.students import students_bp
from routes.devices import devices_bp
from routes.courses import courses_bp
from routes.calendar import calendar_bp
from routes.evasion import evasion_bp
from routes.evasion_notify import notify_bp
from routes.reports import reports_bp
from routes.alerts import alerts_bp
from routes.nextdns_sync import nextdns_sync_bp

# Motores de Lógica
from nextdns_client import create_profile, extract_profile_id
from evasion_engine import detect_evasions
from alerts_engine import process_pending_alerts

app = Flask(__name__)

# ======================
# CONFIGURACIÓN DE DB
# ======================
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
INSTANCE_DIR = os.path.join(BASE_DIR, "instance")
os.makedirs(INSTANCE_DIR, exist_ok=True)

DB_PATH = os.path.join(INSTANCE_DIR, "database.db")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# ======================
# CONFIGURACIÓN SCHEDULER
# ======================
scheduler = APScheduler()

def task_main_loop():
    """
    Tarea central: Se ejecuta cada 5 minutos.
    Busca evasiones y procesa el envío de alertas pendientes.
    """
    with app.app_context():
        now = datetime.now()
        print(f"⏱️ [{now.strftime('%H:%M:%S')}] Ciclo de control automático iniciado...")
        
        students = Student.query.all()
        if not students:
            print("ℹ️ No hay alumnos registrados para monitorear.")
        else:
            for student in students:
                try:
                    # Motor de detección de evasión
                    detect_evasions(student, now)
                except Exception as e:
                    print(f"❌ Error en motor de evasión ({student.apellido}): {e}")
        
        try:
            # Procesamiento de alertas pendientes
            process_pending_alerts(now)
        except Exception as e:
            print(f"❌ Error en motor de notificaciones: {e}")

app.config['SCHEDULER_API_ENABLED'] = True
scheduler.init_app(app)
scheduler.start()

if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
    scheduler.add_job(
        id='master_control_job', 
        func=task_main_loop, 
        trigger='interval', 
        minutes=5
    )
    print("🟢 Scheduler activo: Monitoreo cada 5 minutos configurado.")

# ======================
# FUNCIONES AUXILIARES NEXTDNS
# ======================
def create_device_profile(student, tipo, nombre_dispositivo):
    """
    Crea un perfil en NextDNS siguiendo el formato solicitado:
    'Nombre Apellido, Curso y Tipo de dispositivo'
    """
    # Obtenemos el nombre del curso desde la relación en el modelo
    curso_nombre = student.course.nombre if student.course else "Sin Curso"
    
    # Formateo del nombre para NextDNS
    profile_name = f"{student.nombre} {student.apellido}, {curso_nombre} ({tipo})"
    
    # Intentamos crear el perfil
    response = create_profile(profile_name)
    
    # Manejo de duplicados: si ya existe, agregamos un timestamp breve
    if isinstance(response, dict) and "errors" in response:
        if response["errors"][0].get("code") == "duplicate":
            ts = datetime.now().strftime("%H%M%S")
            profile_name = f"{profile_name} {ts}"
            response = create_profile(profile_name)

    return extract_profile_id(response)

# Inyectamos la función en la configuración para que devices.py pueda usarla
app.config["CREATE_DEVICE_PROFILE"] = create_device_profile

# ======================
# REGISTRO DE BLUEPRINTS
# ======================
app.register_blueprint(students_bp)
app.register_blueprint(devices_bp)
app.register_blueprint(courses_bp)
app.register_blueprint(calendar_bp)
app.register_blueprint(evasion_bp)
app.register_blueprint(notify_bp)
app.register_blueprint(reports_bp)
app.register_blueprint(alerts_bp)
app.register_blueprint(nextdns_sync_bp)

# ======================
# RUTAS DE INTERFAZ
# ======================
@app.route("/")
def index():
    return render_template("base.html")

@app.route("/courses-ui")
def courses_ui():
    return render_template("courses.html")

@app.route("/students-ui")
def students_ui():
    return render_template("students.html")

# ======================
# EJECUCIÓN
# ======================
if __name__ == "__main__":
    with app.app_context():
        # Crea la base de datos y todas las tablas definidas en models.py
        db.create_all()
        print("✅ Base de datos inicializada correctamente.")
        
    app.run(debug=True, port=5000)
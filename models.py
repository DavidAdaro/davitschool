from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# =========================
# CONFIGURACIÓN GLOBAL
# =========================
class GlobalConfig(db.Model):
    """
    Almacena configuraciones dinámicas para no tocar el código.
    Ej: NextDNS Base Profile ID, Email de alertas, etc.
    """
    __tablename__ = "global_config"
    key = db.Column(db.String(50), primary_key=True)
    value = db.Column(db.String(255), nullable=False)

# =========================
# CURSOS Y HORARIOS
# =========================

class Course(db.Model):
    __tablename__ = "courses"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)  # Ej: "3ro Año A"
    turno_base = db.Column(db.String(20), nullable=False) # "mañana", "tarde"

    # Relaciones
    students = db.relationship("Student", backref="course", cascade="all, delete-orphan")
    schedules = db.relationship("CourseSchedule", backref="course", cascade="all, delete-orphan")

class CourseSchedule(db.Model):
    """
    Define los bloques de tiempo donde NextDNS debe estar ACTIVO.
    Puede ser para todo el curso, o filtrado por sexo/comisión.
    """
    __tablename__ = "course_schedules"

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False)

    tipo = db.Column(db.String(20), nullable=False)     # "turno", "contraturno", "tiempo_muerto"
    dia_semana = db.Column(db.Integer, nullable=False)  # 0=Lunes, 6=Domingo
    hora_inicio = db.Column(db.String(5), nullable=False) # Formato "HH:MM"
    hora_fin = db.Column(db.String(5), nullable=False)    # Formato "HH:MM"

    # Filtros Avanzados
    sexo = db.Column(db.String(10), default="ALL")      # "ALL", "M", "F" (Para gimnasia)
    comision = db.Column(db.String(10), nullable=True)  # "A", "B", o NULL (Para talleres)

# =========================
# ALUMNOS Y DISPOSITIVOS
# =========================

class Student(db.Model):
    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False)

    nombre = db.Column(db.String(50), nullable=False)
    apellido = db.Column(db.String(50), nullable=False)
    
    # Datos para filtros de horario
    sexo = db.Column(db.String(1), nullable=False)      # "M" o "F"
    comision = db.Column(db.String(10), nullable=True)  # Opcional

    # Datos de contacto para alertas
    email_padre = db.Column(db.String(100), nullable=True)
    email_escuela = db.Column(db.String(100), nullable=True)

    devices = db.relationship("Device", backref="student", cascade="all, delete-orphan")

class Device(db.Model):
    __tablename__ = "devices"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)

    tipo = db.Column(db.String(20), nullable=False)   # "celular", "tablet", "netbook"
    nombre = db.Column(db.String(50), nullable=False) # "Samsung A52", "iPad"
    
    # ID real en la nube de NextDNS
    nextdns_profile_id = db.Column(db.String(50), nullable=False, unique=True)

# =========================
# CALENDARIO Y EXCEPCIONES
# =========================

class CalendarBlock(db.Model):
    """Feriados, jornadas, recesos. NextDNS OFF."""
    __tablename__ = "calendar_blocks"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    fecha_inicio = db.Column(db.Date, nullable=False)
    fecha_fin = db.Column(db.Date, nullable=False)
    eliminado = db.Column(db.Boolean, default=False)

class SpecialEvent(db.Model):
    """Excepciones de ENCENDIDO (Campamentos, etc). NextDNS ON."""
    __tablename__ = "special_events"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    fecha = db.Column(db.Date, nullable=False)
    hora_inicio = db.Column(db.String(5), nullable=False)
    hora_fin = db.Column(db.String(5), nullable=False)

# =========================
# EVENTOS DE EVASIÓN
# =========================

class EvasionEvent(db.Model):
    __tablename__ = "evasion_events"
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"))
    device_id = db.Column(db.Integer, db.ForeignKey("devices.id"))
    
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    motivo = db.Column(db.String(50)) # "VPN_PROXY", "ID_CLONADO"
    notificado = db.Column(db.Boolean, default=False)
class Alert(db.Model):
    __tablename__ = "alerts"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    device_id = db.Column(db.Integer, db.ForeignKey("devices.id"), nullable=True)

    tipo_evento = db.Column(db.String(50), nullable=False)   # vpn, clone, inactive
    nivel = db.Column(db.String(20), default="info")        # info, warning, critical
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    mensaje = db.Column(db.Text, nullable=True)

    # Relación para facilitar consultas
    student = db.relationship("Student", backref="alerts_list")
    device = db.relationship("Device", backref="alerts_list")


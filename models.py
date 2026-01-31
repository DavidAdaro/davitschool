from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date

db = SQLAlchemy()

# =========================
# CURSOS
# =========================

class Course(db.Model):
    __tablename__ = "courses"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    turno_base = db.Column(db.String(20), nullable=False)

    students = db.relationship(
        "Student",
        backref="course",
        cascade="all, delete-orphan"
    )

    schedules = db.relationship(
        "CourseSchedule",
        backref="course",
        cascade="all, delete-orphan"
    )


class CourseSchedule(db.Model):
    __tablename__ = "course_schedules"

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False)

    tipo = db.Column(db.String(20), nullable=False)
    dia_semana = db.Column(db.Integer, nullable=False)  # 0=lunes
    hora_inicio = db.Column(db.String(5), nullable=False)
    hora_fin = db.Column(db.String(5), nullable=False)

    sexo = db.Column(db.String(5), default="ALL")
    comision = db.Column(db.String(10), nullable=True)


# =========================
# ALUMNOS / DISPOSITIVOS
# =========================

class Student(db.Model):
    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    apellido = db.Column(db.String(50), nullable=False)
    sexo = db.Column(db.String(1), nullable=False)
    comision = db.Column(db.String(10), nullable=True)

    email_padre = db.Column(db.String(100), nullable=False)
    email_escuela = db.Column(db.String(100), nullable=False)

    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False)

    devices = db.relationship(
        "Device",
        backref="student",
        cascade="all, delete-orphan"
    )


class Device(db.Model):
    __tablename__ = "devices"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)

    tipo = db.Column(db.String(30), nullable=False)
    nombre = db.Column(db.String(50), nullable=False)

    nextdns_profile_id = db.Column(db.String(100), nullable=False, unique=True)


# =========================
# CALENDARIO
# =========================

class CalendarBlock(db.Model):
    __tablename__ = "calendar_blocks"

    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(20), nullable=False)
    fecha_inicio = db.Column(db.Date, nullable=False)
    fecha_fin = db.Column(db.Date, nullable=False)

    eliminado = db.Column(db.Boolean, default=False)


class SpecialEvent(db.Model):
    __tablename__ = "special_events"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)

    fecha = db.Column(db.Date, nullable=False)
    hora_inicio = db.Column(db.String(5), nullable=False)
    hora_fin = db.Column(db.String(5), nullable=False)


# =========================
# EVASIÓN
# =========================

class EvasionEvent(db.Model):
    __tablename__ = "evasion_events"

    id = db.Column(db.Integer, primary_key=True)

    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    device_id = db.Column(db.Integer, db.ForeignKey("devices.id"), nullable=False)

    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    motivo = db.Column(db.String(200), nullable=False)

    notificado = db.Column(db.Boolean, default=False)
    fecha_notificado = db.Column(db.DateTime, nullable=True)
# =========================
# ALERTAS
# =========================

class Alert(db.Model):
    __tablename__ = "alerts"

    id = db.Column(db.Integer, primary_key=True)

    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    device_id = db.Column(db.Integer, db.ForeignKey("devices.id"), nullable=True)

    tipo_evento = db.Column(db.String(50), nullable=False)   # vpn, clone, inactive, etc
    nivel = db.Column(db.Integer, nullable=False)            # 1,2,3

    descripcion = db.Column(db.String(255), nullable=False)

    fecha = db.Column(db.DateTime, default=datetime.utcnow)

    notificado_padre = db.Column(db.Boolean, default=False)
    notificado_escuela = db.Column(db.Boolean, default=False)

    student = db.relationship("Student")
    device = db.relationship("Device")


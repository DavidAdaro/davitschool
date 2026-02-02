from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class GlobalConfig(db.Model):
    __tablename__ = "global_config"
    key = db.Column(db.String(50), primary_key=True)
    value = db.Column(db.String(255), nullable=False)

class Course(db.Model):
    __tablename__ = "courses"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False, unique=True)
    turno_base = db.Column(db.String(20), nullable=False) # Mañana, Tarde, Vespertino
    students = db.relationship("Student", backref="course", cascade="all, delete-orphan")
    schedules = db.relationship("CourseSchedule", backref="course", cascade="all, delete-orphan")

class CourseSchedule(db.Model):
    __tablename__ = "course_schedules"
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False)
    tipo = db.Column(db.String(20), nullable=False) # 'base' o 'contraturno'
    dia_semana = db.Column(db.Integer, nullable=False) # 0-6
    hora_inicio = db.Column(db.Time, nullable=False)
    hora_fin = db.Column(db.Time, nullable=False)
    sexo = db.Column(db.String(1), default="T") # 'M', 'F', 'T'
    comision = db.Column(db.String(20), nullable=True)

class Student(db.Model):
    __tablename__ = "students"
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    sexo = db.Column(db.String(1), nullable=False)
    comision = db.Column(db.String(20), nullable=True)
    email_padre = db.Column(db.String(120), nullable=False)
    email_escuela = db.Column(db.String(120), nullable=False)
    devices = db.relationship("Device", backref="student", cascade="all, delete-orphan")

class Device(db.Model):
    __tablename__ = "devices"
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    tipo = db.Column(db.String(30), nullable=False)
    nombre_modelo = db.Column(db.String(50), nullable=False)
    nextdns_profile_id = db.Column(db.String(100), nullable=False, unique=True)

class CalendarExclusion(db.Model):
    __tablename__ = "calendar_exclusions"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    fecha_inicio = db.Column(db.Date, nullable=False)
    fecha_fin = db.Column(db.Date, nullable=False)

class SpecialEvent(db.Model):
    __tablename__ = "special_events"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    fecha = db.Column(db.Date, nullable=False)
    hora_inicio = db.Column(db.Time, nullable=False)
    hora_fin = db.Column(db.Time, nullable=False)

class Alert(db.Model):
    __tablename__ = "alerts"
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    device_id = db.Column(db.Integer, db.ForeignKey("devices.id"), nullable=True)
    tipo_evento = db.Column(db.String(50), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    notificado_padre = db.Column(db.Boolean, default=False)
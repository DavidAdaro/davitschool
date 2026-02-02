from flask import Blueprint, jsonify, render_template
from models import Student, Device, Alert, Course
from datetime import datetime, timedelta

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/api/stats")
def get_stats():
    # Alumnos y Cursos totales
    total_students = Student.query.count()
    total_courses = Course.query.count()
    
    # Dispositivos totales vs Dispositivos con alertas hoy
    total_devices = Device.query.count()
    today = datetime.utcnow().date()
    alerts_today = Alert.query.filter(Alert.fecha >= today).count()
    
    # Alertas por tipo (para el gráfico)
    evasion_count = Alert.query.filter_by(tipo_evento="falta_registros").count()
    
    return jsonify({
        "students": total_students,
        "courses": total_courses,
        "devices": total_devices,
        "alerts": alerts_today,
        "evasions": evasion_count
    })
@dashboard_bp.route("/api/student-report/<int:student_id>")
def get_student_report(student_id):
    student = Student.query.get_or_404(student_id)
    
    # Obtenemos todas las alertas del alumno, ordenadas por la más reciente
    alerts = (
        Alert.query.filter_by(student_id=student_id)
        .order_by(Alert.fecha.desc())
        .all()
    )
    
    history = []
    for a in alerts:
        history.append({
            "fecha": a.fecha.strftime('%d/%m/%Y %H:%M'),
            "dispositivo": a.device.tipo if a.device else "Desconocido",
            "modelo": a.device.nombre_modelo if a.device else "N/A",
            "motivo": a.tipo_evento.replace('_', ' ').upper(),
            "notificado": "Sí" if a.notificado_padre else "No"
        })
    
    return jsonify({
        "alumno": f"{student.apellido}, {student.nombre}",
        "curso": student.course.nombre,
        "total_alertas": len(history),
        "historial": history
    })

@dashboard_bp.route("/")
def index():
    return render_template("index.html")
from flask import Blueprint, request, jsonify
from models import db, Course, CourseSchedule, Student, Device
from nextdns_client import delete_profile
from datetime import datetime

courses_bp = Blueprint("courses", __name__, url_prefix="/courses")

# ==========================================
# LÓGICA AUXILIAR: TIEMPOS MUERTOS
# ==========================================

def update_gap_times(course_id, dia_semana):
    """
    Busca huecos entre el turno y el contraturno del mismo día
    y crea registros de 'tiempo_muerto' automáticamente.
    """
    # 1. Limpiamos tiempos muertos viejos para ese día
    CourseSchedule.query.filter_by(
        course_id=course_id, 
        dia_semana=dia_semana, 
        tipo="tiempo_muerto"
    ).delete()

    # 2. Obtenemos turnos y contraturnos ordenados por hora
    schedules = CourseSchedule.query.filter(
        CourseSchedule.course_id == course_id,
        CourseSchedule.dia_semana == dia_semana,
        CourseSchedule.tipo.in_(["turno", "contraturno"])
    ).order_by(CourseSchedule.hora_inicio).all()

    if len(schedules) < 2:
        db.session.commit()
        return

    # 3. Identificamos huecos entre bloques
    for i in range(len(schedules) - 1):
        fin_bloque_anterior = schedules[i].hora_fin
        inicio_bloque_siguiente = schedules[i+1].hora_inicio

        if fin_bloque_anterior < inicio_bloque_siguiente:
            gap = CourseSchedule(
                course_id=course_id,
                tipo="tiempo_muerto",
                dia_semana=dia_semana,
                hora_inicio=fin_bloque_anterior,
                hora_fin=inicio_bloque_siguiente,
                sexo="ALL" # El tiempo muerto protege a todos por defecto
            )
            db.session.add(gap)
    
    db.session.commit()

# ==========================================
# GESTIÓN DE CURSOS
# ==========================================

@courses_bp.route("/", methods=["GET"])
def list_courses():
    courses = Course.query.all()
    return jsonify([{
        "id": c.id, 
        "nombre": c.nombre, 
        "turno_base": c.turno_base
    } for c in courses])

@courses_bp.route("/add", methods=["POST"])
def add_course():
    data = request.json
    course = Course(nombre=data["nombre"], turno_base=data["turno_base"])
    db.session.add(course)
    db.session.commit()
    return jsonify({"message": "Curso creado", "course_id": course.id}), 201

@courses_bp.route("/delete/<int:course_id>", methods=["DELETE"])
def delete_course(course_id):
    """Elimina curso, alumnos y sus perfiles de NextDNS asociados."""
    course = Course.query.get(course_id)
    if not course:
        return jsonify({"error": "Curso no encontrado"}), 404

    # Limpieza en NextDNS antes de borrar de la DB
    for student in course.students:
        for device in student.devices:
            if device.nextdns_profile_id:
                try:
                    delete_profile(device.nextdns_profile_id)
                except Exception as e:
                    print(f"Error NextDNS: {e}")
    
    db.session.delete(course)
    db.session.commit()
    return jsonify({"message": "Curso y perfiles eliminados"}), 200

# ==========================================
# GESTIÓN DE HORARIOS (SCHEDULES)
# ==========================================

@courses_bp.route("/<int:course_id>/schedules", methods=["GET"])
def get_schedules(course_id):
    schedules = CourseSchedule.query.filter_by(course_id=course_id).all()
    return jsonify([{
        "id": s.id,
        "dia_semana": s.dia_semana,
        "hora_inicio": s.hora_inicio,
        "hora_fin": s.hora_fin,
        "tipo": s.tipo,
        "sexo": s.sexo,
        "comision": s.comision
    } for s in schedules])

@courses_bp.route("/<int:course_id>/schedules/add", methods=["POST"])
def add_schedule(course_id):
    data = request.json
    new_schedule = CourseSchedule(
        course_id=course_id,
        tipo=data.get("tipo", "contraturno"),
        dia_semana=data["dia_semana"],
        hora_inicio=data["hora_inicio"],
        hora_fin=data["hora_fin"],
        sexo=data.get("sexo", "ALL"),
        comision=data.get("comision")
    )

    db.session.add(new_schedule)
    db.session.commit()
    
    # Recalcular tiempos muertos automáticamente
    update_gap_times(course_id, data["dia_semana"])
    
    return jsonify({"message": "Horario agregado", "id": new_schedule.id}), 201

@courses_bp.route("/schedules/<int:schedule_id>", methods=["PUT"])
def edit_schedule(schedule_id):
    """Permite editar un horario existente."""
    schedule = CourseSchedule.query.get(schedule_id)
    if not schedule:
        return jsonify({"error": "Horario no encontrado"}), 404

    data = request.json
    schedule.hora_inicio = data.get("hora_inicio", schedule.hora_inicio)
    schedule.hora_fin = data.get("hora_fin", schedule.hora_fin)
    schedule.tipo = data.get("tipo", schedule.tipo)
    schedule.sexo = data.get("sexo", schedule.sexo)
    schedule.comision = data.get("comision", schedule.comision)
    schedule.dia_semana = data.get("dia_semana", schedule.dia_semana)

    db.session.commit()
    
    # Recalcular tras la edición
    update_gap_times(schedule.course_id, schedule.dia_semana)
    
    return jsonify({"message": "Horario actualizado"})

@courses_bp.route("/schedules/<int:schedule_id>", methods=["DELETE"])
def delete_schedule(schedule_id):
    schedule = CourseSchedule.query.get(schedule_id)
    if schedule:
        c_id = schedule.course_id
        d_semana = schedule.dia_semana
        db.session.delete(schedule)
        db.session.commit()
        
        # Limpiar/recalcular tiempos muertos tras borrar un bloque
        update_gap_times(c_id, d_semana)
        return jsonify({"message": "Horario eliminado"}), 200
    return jsonify({"error": "Horario no encontrado"}), 404
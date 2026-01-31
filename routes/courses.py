
from flask import Blueprint, request, jsonify
from models import db, Course, CourseSchedule, Student, Device
from nextdns_client import delete_profile

courses_bp = Blueprint("courses", __name__, url_prefix="/courses")

# =========================
# CURSOS
# =========================

@courses_bp.route("/", methods=["GET"])
def list_courses():
    """
    Usado por courses.html
    Lista cursos con su turno base
    """
    courses = Course.query.all()
    result = []

    for c in courses:
        result.append({
            "id": c.id,
            "nombre": c.nombre,
            "turno_base": c.turno_base
        })

    return jsonify(result)


@courses_bp.route("/add", methods=["POST"])
def add_course():
    """
    JSON esperado:
    {
      "nombre": "3B",
      "turno_base": "mañana | tarde | vespertino"
    }
    """
    data = request.json

    course = Course(
        nombre=data["nombre"],
        turno_base=data["turno_base"]
    )

    db.session.add(course)
    db.session.commit()

    return jsonify({
        "message": "Curso creado correctamente",
        "course_id": course.id
    }), 201


@courses_bp.route("/delete/<int:course_id>", methods=["DELETE"])
def delete_course(course_id):
    """
    Elimina:
    - curso
    - alumnos
    - dispositivos
    - perfiles NextDNS
    - horarios
    """
    course = Course.query.get(course_id)
    if not course:
        return jsonify({"error": "Curso no encontrado"}), 404

    alumnos = Student.query.filter_by(course_id=course.id).all()

    for alumno in alumnos:
        dispositivos = Device.query.filter_by(student_id=alumno.id).all()

        for device in dispositivos:
            # FIX REAL: nombre correcto del campo
            if device.nextdns_profile_id:
                try:
                    delete_profile(device.nextdns_profile_id)
                except Exception as e:
                    print("Error eliminando perfil NextDNS:", e)

            db.session.delete(device)

        db.session.delete(alumno)

    CourseSchedule.query.filter_by(course_id=course.id).delete()
    db.session.delete(course)
    db.session.commit()

    return jsonify({
        "message": "Curso y todos los datos asociados eliminados correctamente"
    })


# =========================
# HORARIOS DEL CURSO
# =========================

@courses_bp.route("/<int:course_id>/schedules", methods=["GET"])
def list_schedules(course_id):
    """
    Usado por courses.html
    Devuelve horarios:
    - turno
    - contraturno
    - tiempo_muerto
    """
    schedules = CourseSchedule.query.filter_by(course_id=course_id).all()
    result = []

    for s in schedules:
        result.append({
            "id": s.id,
            "tipo": s.tipo,
            "dia_semana": s.dia_semana,
            "hora_inicio": s.hora_inicio,
            "hora_fin": s.hora_fin,
            "sexo": s.sexo,
            "comision": s.comision
        })

    return jsonify(result)


@courses_bp.route("/<int:course_id>/schedules/add", methods=["POST"])
def add_schedule(course_id):
    """
    JSON esperado:
    {
      "tipo": "turno | contraturno | tiempo_muerto",
      "dia_semana": 0,
      "hora_inicio": "08:00",
      "hora_fin": "12:00",
      "sexo": "ALL | M | F",
      "comision": "A" (opcional)
    }
    """

    course = Course.query.get(course_id)
    if not course:
        return jsonify({"error": "Curso no encontrado"}), 404

    data = request.json

    schedule = CourseSchedule(
        course_id=course.id,
        tipo=data["tipo"],
        dia_semana=data["dia_semana"],
        hora_inicio=data["hora_inicio"],
        hora_fin=data["hora_fin"],
        sexo=data.get("sexo", "ALL"),
        comision=data.get("comision")
    )

    db.session.add(schedule)
    db.session.commit()

    return jsonify({
        "message": "Horario agregado correctamente",
        "schedule_id": schedule.id
    }), 201


@courses_bp.route("/schedules/delete/<int:schedule_id>", methods=["DELETE"])
def delete_schedule(schedule_id):
    """
    Elimina un horario individual
    """
    schedule = CourseSchedule.query.get(schedule_id)
    if not schedule:
        return jsonify({"error": "Horario no encontrado"}), 404

    db.session.delete(schedule)
    db.session.commit()

    return jsonify({"message": "Horario eliminado correctamente"})

from flask import Blueprint, request, jsonify
from models import db, Course, CourseSchedule
from nextdns_client import delete_profile
from datetime import datetime

courses_bp = Blueprint("courses", __name__, url_prefix="/courses")

@courses_bp.route("/<int:course_id>/schedules/add", methods=["POST"])
def add_schedule(course_id):
    data = request.json
    try:
        h_inicio = datetime.strptime(data["hora_inicio"], "%H:%M").time()
        h_fin = datetime.strptime(data["hora_fin"], "%H:%M").time()

        new_schedule = CourseSchedule(
            course_id=course_id,
            tipo=data.get("tipo", "contraturno"),
            dia_semana=data["dia_semana"],
            hora_inicio=h_inicio,
            hora_fin=h_fin,
            sexo=data.get("sexo", "T"),
            comision=data.get("comision")
        )
        db.session.add(new_schedule)
        db.session.commit()
        return jsonify({"message": "Horario agregado", "id": new_schedule.id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@courses_bp.route("/delete/<int:course_id>", methods=["DELETE"])
def delete_course(course_id):
    course = Course.query.get(course_id)
    if not course:
        return jsonify({"error": "Curso no encontrado"}), 404

    for student in course.students:
        for device in student.devices:
            if device.nextdns_device_id:
                delete_profile(device.nextdns_device_id)
    
    db.session.delete(course)
    db.session.commit()
    return jsonify({"message": "Curso eliminado"}), 200
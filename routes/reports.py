from flask import Blueprint, jsonify
from models import EvasionEvent, Student, Course
from sqlalchemy import func

reports_bp = Blueprint("reports", __name__, url_prefix="/reports")


@reports_bp.route("/by-student", methods=["GET"])
def report_by_student():
    data = (
        EvasionEvent.query
        .with_entities(
            EvasionEvent.student_id,
            func.count(EvasionEvent.id)
        )
        .group_by(EvasionEvent.student_id)
        .all()
    )

    result = []
    for student_id, total in data:
        student = Student.query.get(student_id)
        result.append({
            "student": f"{student.apellido}, {student.nombre}",
            "total_eventos": total
        })

    return jsonify(result)


@reports_bp.route("/by-course", methods=["GET"])
def report_by_course():
    data = (
        EvasionEvent.query
        .join(Student, Student.id == EvasionEvent.student_id)
        .join(Course, Course.id == Student.course_id)
        .with_entities(
            Course.nombre,
            func.count(EvasionEvent.id)
        )
        .group_by(Course.nombre)
        .all()
    )

    result = []
    for curso, total in data:
        result.append({
            "curso": curso,
            "total_eventos": total
        })

    return jsonify(result)

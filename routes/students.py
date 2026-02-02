from flask import Blueprint, request, jsonify
from models import db, Student, Course, Device
from nextdns_client import delete_profile

students_bp = Blueprint("students", __name__, url_prefix="/students")

@students_bp.route("/", methods=["GET"])
def list_students():
    students = Student.query.all()
    result = []
    for s in students:
        result.append({
            "id": s.id,
            "nombre": s.nombre,
            "apellido": s.apellido,
            "sexo": s.sexo,
            "comision": s.comision,
            "curso": s.course.nombre if s.course else "Sin Curso",
            "email_padre": s.email_padre,
            "email_escuela": s.email_escuela
        })
    return jsonify(result)

@students_bp.route("/add", methods=["POST"])
def add_student():
    data = request.json
    course = Course.query.get(data["course_id"])
    if not course:
        return jsonify({"error": "Curso no encontrado"}), 404

    student = Student(
        nombre=data["nombre"],
        apellido=data["apellido"],
        sexo=data["sexo"],
        comision=data.get("comision"),
        email_padre=data["email_padre"],
        email_escuela=data["email_escuela"],
        course_id=course.id
    )
    db.session.add(student)
    db.session.commit()
    return jsonify({"message": "Alumno creado correctamente", "id": student.id}), 201

@students_bp.route("/delete/<int:student_id>", methods=["DELETE"])
def delete_student(student_id):
    student = Student.query.get(student_id)
    if not student:
        return jsonify({"error": "Alumno no encontrado"}), 404

    # El borrado de dispositivos y perfiles NextDNS se maneja en cascada o manual aquí
    for device in student.devices:
        if device.nextdns_device_id:
            delete_profile(device.nextdns_device_id)
    
    db.session.delete(student)
    db.session.commit()
    return jsonify({"message": "Alumno eliminado correctamente"})
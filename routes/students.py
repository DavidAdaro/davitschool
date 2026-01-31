from flask import Blueprint, request, jsonify
from models import db, Student, Course, Device
from nextdns_client import delete_profile

students_bp = Blueprint("students", __name__, url_prefix="/students")


@students_bp.route("/", methods=["GET"])
def list_students():
    """
    Lista todos los alumnos
    """
    students = Student.query.all()

    result = []
    for s in students:
        result.append({
            "id": s.id,
            "nombre": s.nombre,
            "apellido": s.apellido,
            "sexo": s.sexo,
            "comision": s.comision,
            "curso": s.course.nombre,
            "email_padre": s.email_padre,
            "email_escuela": s.email_escuela
        })

    return jsonify(result)


@students_bp.route("/add", methods=["POST"])
def add_student():
    """
    Agrega un alumno
    """
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

    return jsonify({
        "message": "Alumno creado correctamente",
        "student_id": student.id
    }), 201


@students_bp.route("/edit/<int:student_id>", methods=["PUT"])
def edit_student(student_id):
    """
    Edita un alumno
    """
    student = Student.query.get(student_id)
    if not student:
        return jsonify({"error": "Alumno no encontrado"}), 404

    data = request.json

    student.nombre = data.get("nombre", student.nombre)
    student.apellido = data.get("apellido", student.apellido)
    student.sexo = data.get("sexo", student.sexo)
    student.comision = data.get("comision", student.comision)
    student.email_padre = data.get("email_padre", student.email_padre)
    student.email_escuela = data.get("email_escuela", student.email_escuela)

    db.session.commit()

    return jsonify({"message": "Alumno actualizado correctamente"})


@students_bp.route("/delete/<int:student_id>", methods=["DELETE"])
def delete_student(student_id):
    """
    Elimina:
    - alumno
    - dispositivos asociados
    - perfiles NextDNS asociados
    """
    student = Student.query.get(student_id)
    if not student:
        return jsonify({"error": "Alumno no encontrado"}), 404

    dispositivos = Device.query.filter_by(student_id=student.id).all()

    for device in dispositivos:
        if device.nextdns_profile_id:
            try:
                delete_profile(device.nextdns_profile_id)
            except Exception as e:
                print("Error eliminando perfil NextDNS:", e)

        db.session.delete(device)

    db.session.delete(student)
    db.session.commit()

    return jsonify({"message": "Alumno y dispositivos eliminados correctamente"})

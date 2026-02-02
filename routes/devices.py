from flask import Blueprint, request, jsonify
from models import db, Device, Student
from nextdns_client import create_profile, delete_profile

devices_bp = Blueprint("devices", __name__, url_prefix="/devices")

@devices_bp.route("/add", methods=["POST"])
def add_device():
    data = request.json
    student = Student.query.get(data["student_id"])
    if not student:
        return jsonify({"error": "Alumno no encontrado"}), 404

    # Formato: nombre_apellido_curso_tipo
    profile_name = f"{student.nombre}_{student.apellido}_{student.course.nombre}_{data['tipo']}"
    profile_name = profile_name.lower().replace(" ", "_")

    # Llamada a la función corregida en nextdns_client
    nextdns_id = create_profile(profile_name)

    if not nextdns_id:
        return jsonify({"error": "Fallo la sincronización con NextDNS"}), 500

    new_device = Device(
        student_id=student.id,
        tipo=data["tipo"],
        nombre_modelo=data["nombre_modelo"],
        nextdns_profile_id=nextdns_id
    )

    db.session.add(new_device)
    db.session.commit()
    return jsonify({"message": "Dispositivo vinculado", "nextdns_id": nextdns_id}), 201

@devices_bp.route("/<int:device_id>", methods=["DELETE"])
def delete_device(device_id):
    device = Device.query.get(device_id)
    if not device:
        return jsonify({"error": "Dispositivo no encontrado"}), 404

    delete_profile(device.nextdns_profile_id)
    db.session.delete(device)
    db.session.commit()
    return jsonify({"message": "Dispositivo eliminado"})
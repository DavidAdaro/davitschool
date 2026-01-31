from flask import Blueprint, request, jsonify, current_app
from models import db, Device, Student

devices_bp = Blueprint("devices", __name__, url_prefix="/devices")


@devices_bp.route("/add", methods=["POST"])
def add_device():
    data = request.json

    student = Student.query.get(data["student_id"])
    if not student:
        return jsonify({"error": "Alumno no encontrado"}), 404

    create_device_profile = current_app.config["CREATE_DEVICE_PROFILE"]

    profile_id = create_device_profile(
        student=student,
        tipo=data["tipo"],
        nombre=data["nombre"]
    )

    device = Device(
        student_id=student.id,
        tipo=data["tipo"],
        nombre=data["nombre"],
        nextdns_profile_id=profile_id
    )

    db.session.add(device)
    db.session.commit()

    return jsonify({
        "message": "Dispositivo agregado correctamente",
        "device_id": device.id,
        "nextdns_profile_id": profile_id
    }), 201


@devices_bp.route("/<int:device_id>", methods=["DELETE"])
def delete_device(device_id):
    device = Device.query.get(device_id)
    if not device:
        return jsonify({"error": "Dispositivo no encontrado"}), 404

    delete_device_profile = current_app.config["DELETE_DEVICE_PROFILE"]
    delete_device_profile(device.nextdns_profile_id)

    db.session.delete(device)
    db.session.commit()

    return jsonify({"message": "Dispositivo eliminado correctamente"})

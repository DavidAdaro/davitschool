from flask import Blueprint, jsonify
from models import EvasionEvent, Student, Device

evasion_bp = Blueprint("evasion", __name__, url_prefix="/evasion")


@evasion_bp.route("/", methods=["GET"])
def list_all_events():
    """
    Lista TODOS los eventos de evasión
    """
    events = EvasionEvent.query.order_by(EvasionEvent.fecha.desc()).all()
    result = []

    for e in events:
        student = Student.query.get(e.student_id)
        device = Device.query.get(e.device_id)

        result.append({
            "id": e.id,
            "fecha": e.fecha.isoformat(),
            "motivo": e.motivo,
            "alumno": f"{student.apellido}, {student.nombre}" if student else None,
            "dispositivo": device.nombre if device else None,
            "tipo_dispositivo": device.tipo if device else None
        })

    return jsonify(result)

from flask import Blueprint, jsonify
from models import Alert

alerts_bp = Blueprint("alerts", __name__, url_prefix="/alerts")


@alerts_bp.route("/", methods=["GET"])
def list_alerts():
    alerts = Alert.query.order_by(Alert.fecha.desc()).all()

    result = []
    for a in alerts:
        result.append({
            "id": a.id,
            "alumno": f"{a.student.nombre} {a.student.apellido}",
            "curso": a.student.course.nombre,
            "dispositivo": a.device.nombre if a.device else "-",
            "evento": a.tipo_evento,
            "nivel": a.nivel,
            "fecha": a.fecha.isoformat()
        })

    return jsonify(result)

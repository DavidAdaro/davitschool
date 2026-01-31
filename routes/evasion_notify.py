from flask import Blueprint, jsonify
from models import EvasionEvent, Student, db

notify_bp = Blueprint("notify", __name__, url_prefix="/evasion")


@notify_bp.route("/pending", methods=["GET"])
def pending_notifications():
    """
    Lista eventos NO notificados
    """
    events = EvasionEvent.query.filter_by(notificado=False).all()
    result = []

    for e in events:
        student = Student.query.get(e.student_id)

        result.append({
            "event_id": e.id,
            "fecha": e.fecha.isoformat(),
            "motivo": e.motivo,
            "email_padre": student.email_padre if student else None,
            "email_escuela": student.email_escuela if student else None
        })

    return jsonify(result)


@notify_bp.route("/mark-notified/<int:event_id>", methods=["POST"])
def mark_as_notified(event_id):
    event = EvasionEvent.query.get(event_id)
    if not event:
        return jsonify({"error": "Evento no encontrado"}), 404

    event.notificado = True
    db.session.commit()

    return jsonify({"message": "Evento marcado como notificado"})

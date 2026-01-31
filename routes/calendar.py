from flask import Blueprint, request, jsonify
from datetime import datetime

from models import db, CalendarBlock, SpecialEvent

calendar_bp = Blueprint("calendar", __name__, url_prefix="/calendar")

# =========================
# BLOQUEOS (feriados / recesos / jornadas)
# =========================

@calendar_bp.route("/blocks", methods=["GET"])
def list_blocks():
    blocks = CalendarBlock.query.all()
    return jsonify([
        {
            "id": b.id,
            "tipo": b.tipo,
            "fecha_inicio": b.fecha_inicio.isoformat(),
            "fecha_fin": b.fecha_fin.isoformat()
        }
        for b in blocks
    ])


@calendar_bp.route("/blocks/add", methods=["POST"])
def add_block():
    """
    JSON esperado:
    {
      "tipo": "feriado | receso | jornada",
      "fecha_inicio": "YYYY-MM-DD",
      "fecha_fin": "YYYY-MM-DD"
    }
    """
    data = request.json

    # Convertir strings a objetos date (OBLIGATORIO para SQLite)
    fecha_inicio = datetime.strptime(
        data["fecha_inicio"], "%Y-%m-%d"
    ).date()

    fecha_fin = datetime.strptime(
        data["fecha_fin"], "%Y-%m-%d"
    ).date()

    block = CalendarBlock(
        tipo=data["tipo"],
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin
    )

    db.session.add(block)
    db.session.commit()

    return jsonify({"message": "Bloqueo agregado correctamente"}), 201


@calendar_bp.route("/blocks/delete/<int:block_id>", methods=["DELETE"])
def delete_block(block_id):
    block = CalendarBlock.query.get(block_id)
    if not block:
        return jsonify({"error": "Bloqueo no encontrado"}), 404

    db.session.delete(block)
    db.session.commit()

    return jsonify({"message": "Bloqueo eliminado correctamente"})


# =========================
# EVENTOS ESPECIALES (override)
# =========================

@calendar_bp.route("/events", methods=["GET"])
def list_events():
    events = SpecialEvent.query.all()
    return jsonify([
        {
            "id": e.id,
            "nombre": e.nombre,
            "fecha": e.fecha.isoformat(),
            "hora_inicio": e.hora_inicio,
            "hora_fin": e.hora_fin
        }
        for e in events
    ])


@calendar_bp.route("/events/add", methods=["POST"])
def add_event():
    """
    JSON esperado:
    {
      "nombre": "Campamento",
      "fecha": "YYYY-MM-DD",
      "hora_inicio": "HH:MM",
      "hora_fin": "HH:MM"
    }
    """
    data = request.json

    # Convertir fecha a date
    fecha = datetime.strptime(
        data["fecha"], "%Y-%m-%d"
    ).date()

    event = SpecialEvent(
        nombre=data["nombre"],
        fecha=fecha,
        hora_inicio=data["hora_inicio"],
        hora_fin=data["hora_fin"]
    )

    db.session.add(event)
    db.session.commit()

    return jsonify({"message": "Evento especial agregado"}), 201


@calendar_bp.route("/events/delete/<int:event_id>", methods=["DELETE"])
def delete_event(event_id):
    event = SpecialEvent.query.get(event_id)
    if not event:
        return jsonify({"error": "Evento no encontrado"}), 404

    db.session.delete(event)
    db.session.commit()

    return jsonify({"message": "Evento eliminado correctamente"})

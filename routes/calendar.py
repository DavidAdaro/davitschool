
from flask import Blueprint, request, jsonify
from datetime import datetime
from models import db, CalendarExclusion, SpecialEvent

calendar_bp = Blueprint("calendar", __name__, url_prefix="/calendar")

# ==========================================
# BLOQUEOS (NextDNS OFF: Feriados, Recesos)
# ==========================================

@calendar_bp.route("/blocks", methods=["GET"])
def list_blocks():
    blocks = CalendarExclusion.query.all()
    return jsonify([
        {
            "id": b.id,
            "nombre": b.nombre,
            "fecha_inicio": b.fecha_inicio.isoformat(),
            "fecha_fin": b.fecha_fin.isoformat()
        }
        for b in blocks
    ])

@calendar_bp.route("/blocks/add", methods=["POST"])
def add_block():
    data = request.json
    try:
        fecha_inicio = datetime.strptime(data["fecha_inicio"], "%Y-%m-%d").date()
        fecha_fin = datetime.strptime(data["fecha_fin"], "%Y-%m-%d").date()

        block = CalendarExclusion(
            nombre=data.get("nombre", "Sin nombre"),
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin
        )

        db.session.add(block)
        db.session.commit()
        return jsonify({"message": "Bloqueo agregado correctamente", "id": block.id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@calendar_bp.route("/blocks/delete/<int:block_id>", methods=["DELETE"])
def delete_block(block_id):
    block = CalendarExclusion.query.get(block_id)
    if not block:
        return jsonify({"error": "Bloqueo no encontrado"}), 404

    db.session.delete(block)
    db.session.commit()
    return jsonify({"message": "Bloqueo eliminado correctamente"})

# ==========================================
# EVENTOS ESPECIALES (NextDNS ON: Campamentos)
# ==========================================

@calendar_bp.route("/events", methods=["GET"])
def list_events():
    events = SpecialEvent.query.all()
    return jsonify([
        {
            "id": e.id,
            "nombre": e.nombre,
            "fecha": e.fecha.isoformat(),
            "hora_inicio": str(e.hora_inicio),
            "hora_fin": str(e.hora_fin)
        }
        for e in events
    ])

@calendar_bp.route("/events/add", methods=["POST"])
def add_event():
    data = request.json
    try:
        fecha = datetime.strptime(data["fecha"], "%Y-%m-%d").date()
        h_inicio = datetime.strptime(data["hora_inicio"], "%H:%M").time()
        h_fin = datetime.strptime(data["hora_fin"], "%H:%M").time()
        
        event = SpecialEvent(
            nombre=data["nombre"],
            fecha=fecha,
            hora_inicio=h_inicio,
            hora_fin=h_fin
        )
        db.session.add(event)
        db.session.commit()
        return jsonify({"message": "Evento especial agregado", "id": event.id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

from flask import Blueprint, request, jsonify
from datetime import datetime
from models import db, CalendarBlock, SpecialEvent

calendar_bp = Blueprint("calendar", __name__, url_prefix="/calendar")

# ==========================================
# BLOQUEOS (NextDNS OFF: Feriados, Recesos)
# ==========================================

@calendar_bp.route("/blocks", methods=["GET"])
def list_blocks():
    # Solo listamos los que no han sido marcados como eliminados
    blocks = CalendarBlock.query.filter_by(eliminado=False).all()
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

        block = CalendarBlock(
            nombre=data.get("nombre", "Sin nombre"),
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin
        )

        db.session.add(block)
        db.session.commit()
        return jsonify({"message": "Bloqueo agregado correctamente", "id": block.id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@calendar_bp.route("/blocks/edit/<int:block_id>", methods=["PUT"])
def edit_block(block_id):
    block = CalendarBlock.query.get(block_id)
    if not block:
        return jsonify({"error": "Bloqueo no encontrado"}), 404

    data = request.json
    if "nombre" in data: block.nombre = data["nombre"]
    if "fecha_inicio" in data:
        block.fecha_inicio = datetime.strptime(data["fecha_inicio"], "%Y-%m-%d").date()
    if "fecha_fin" in data:
        block.fecha_fin = datetime.strptime(data["fecha_fin"], "%Y-%m-%d").date()

    db.session.commit()
    return jsonify({"message": "Bloqueo actualizado correctamente"})

@calendar_bp.route("/blocks/delete/<int:block_id>", methods=["DELETE"])
def delete_block(block_id):
    block = CalendarBlock.query.get(block_id)
    if not block:
        return jsonify({"error": "Bloqueo no encontrado"}), 404

    # Usamos borrado lógico para que el policy_engine deje de aplicarlo
    block.eliminado = True
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
            "hora_inicio": e.hora_inicio,
            "hora_fin": e.hora_fin
        }
        for e in events
    ])

@calendar_bp.route("/events/add", methods=["POST"])
def add_event():
    data = request.json
    try:
        fecha = datetime.strptime(data["fecha"], "%Y-%m-%d").date()
        event = SpecialEvent(
            nombre=data["nombre"],
            fecha=fecha,
            hora_inicio=data["hora_inicio"],
            hora_fin=data["hora_fin"]
        )
        db.session.add(event)
        db.session.commit()
        return jsonify({"message": "Evento especial agregado", "id": event.id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@calendar_bp.route("/events/edit/<int:event_id>", methods=["PUT"])
def edit_event(event_id):
    event = SpecialEvent.query.get(event_id)
    if not event:
        return jsonify({"error": "Evento no encontrado"}), 404

    data = request.json
    if "nombre" in data: event.nombre = data["nombre"]
    if "fecha" in data:
        event.fecha = datetime.strptime(data["fecha"], "%Y-%m-%d").date()
    if "hora_inicio" in data: event.hora_inicio = data["hora_inicio"]
    if "hora_fin" in data: event.hora_fin = data["hora_fin"]

    db.session.commit()
    return jsonify({"message": "Evento actualizado correctamente"})

@calendar_bp.route("/events/delete/<int:event_id>", methods=["DELETE"])
def delete_event(event_id):
    event = SpecialEvent.query.get(event_id)
    if not event:
        return jsonify({"error": "Evento no encontrado"}), 404

    db.session.delete(event)
    db.session.commit()
    return jsonify({"message": "Evento eliminado correctamente"})
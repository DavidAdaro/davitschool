from flask import Blueprint, jsonify
from models import Device
from nextdns_sync import get_base_profile_config, sync_profile

nextdns_bp = Blueprint("nextdns", __name__, url_prefix="/nextdns")


@nextdns_bp.route("/sync-all", methods=["POST"])
def sync_all_devices():
    base_config = get_base_profile_config()
    devices = Device.query.all()

    synced = []
    errors = []

    for d in devices:
        try:
            sync_profile(d.nextdns_profile_id, base_config)
            synced.append(d.id)
        except Exception as e:
            errors.append({
                "device_id": d.id,
                "error": str(e)
            })

    return jsonify({
        "base_profile": "acddf9",
        "synced_devices": synced,
        "errors": errors
    })

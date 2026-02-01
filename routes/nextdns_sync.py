import time
import requests
from flask import Blueprint, jsonify
from models import Device, db
from nextdns_client import NEXTDNS_API_KEY, BASE_URL, HEADERS

nextdns_sync_bp = Blueprint("nextdns_sync", __name__, url_prefix="/nextdns")

# Sugerencia: Mover esto a una tabla de base de datos en el futuro
BASE_PROFILE_ID = "acddf9" 

def obtener_config_base():
    r = requests.get(f"{BASE_URL}/profiles/{BASE_PROFILE_ID}", headers=HEADERS)
    r.raise_for_status()
    return r.json().get("data", {})

@nextdns_sync_bp.route("/sync-all", methods=["POST"])
def sync_all_devices():
    try:
        config = obtener_config_base()
        devices = Device.query.all()
        
        count = 0
        for d in devices:
            url = f"{BASE_URL}/profiles/{d.nextdns_profile_id}"
            # Replicamos Security, Privacy, Parental Control, Denylist y Allowlist
            payload = {
                "security": config.get("security"),
                "privacy": config.get("privacy"),
                "parentalControls": config.get("parentalControls"),
                "denylist": config.get("denylist"),
                "allowlist": config.get("allowlist")
            }
            requests.patch(url, headers=HEADERS, json=payload)
            
            count += 1
            time.sleep(0.3) # CORRECCIÓN: Rate Limiting para evitar bloqueos de API
            
        return jsonify({"status": "success", "synced": count})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
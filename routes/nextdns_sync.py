
from flask import Blueprint, jsonify
import requests
from datetime import datetime, timedelta

from models import Device, db, EvasionEvent
from engine.scheduler import nextdns_activo_para_alumno

nextdns_sync_bp = Blueprint(
    "nextdns_sync",
    __name__,
    url_prefix="/nextdns"
)

# =========================
# CONFIGURACIÓN NEXTDNS
# =========================

NEXTDNS_API_KEY = "658b6594906e85c8ef0181242c4da09e79680313"
BASE_PROFILE_ID = "acddf9"
BASE_URL = "https://api.nextdns.io"

HEADERS = {
    "X-Api-Key": NEXTDNS_API_KEY,
    "Content-Type": "application/json"
}

# =========================
# FUNCIONES INTERNAS
# =========================

def obtener_config_base():
    r = requests.get(
        f"{BASE_URL}/profiles/{BASE_PROFILE_ID}",
        headers=HEADERS
    )
    r.raise_for_status()

    data = r.json().get("data", {})

    return {
        "security": data.get("security"),
        "privacy": data.get("privacy"),
        "parentalControls": data.get("parentalControls"),
        "denylist": data.get("denylist"),
        "allowlist": data.get("allowlist")
    }


def aplicar_config_a_perfil(profile_id, config):
    payload = {k: v for k, v in config.items() if v is not None}

    r = requests.put(
        f"{BASE_URL}/profiles/{profile_id}",
        headers=HEADERS,
        json=payload
    )
    r.raise_for_status()


def obtener_ultima_actividad(profile_id):
    r = requests.get(
        f"{BASE_URL}/profiles/{profile_id}/stats",
        headers=HEADERS
    )
    r.raise_for_status()

    return r.json().get("lastActivity")


def detectar_evasion(device):
    alumno = device.student
    ahora = datetime.now()

    # Si no debería estar activo, no se evalúa
    if not nextdns_activo_para_alumno(alumno, ahora):
        return None

    last_activity = obtener_ultima_actividad(device.nextdns_profile_id)

    if not last_activity:
        return "Sin actividad registrada"

    last_dt = datetime.fromisoformat(last_activity)

    if ahora - last_dt > timedelta(minutes=15):
        return "Sin actividad reciente (>15 minutos)"

    return None


# =========================
# RUTAS PANEL WEB
# =========================

@nextdns_sync_bp.route("/sync-all", methods=["POST"])
def sync_all_devices():
    base_config = obtener_config_base()
    devices = Device.query.all()

    ok = []
    errores = []

    for d in devices:
        try:
            aplicar_config_a_perfil(d.nextdns_profile_id, base_config)
            ok.append(d.id)
        except Exception as e:
            errores.append({
                "device_id": d.id,
                "error": str(e)
            })

    return jsonify({
        "perfil_base": BASE_PROFILE_ID,
        "sincronizados": ok,
        "errores": errores
    })


@nextdns_sync_bp.route("/detect-evasion", methods=["POST"])
def detect_evasion_route():
    devices = Device.query.all()
    eventos = []

    for d in devices:
        motivo = detectar_evasion(d)
        if motivo:
            ev = EvasionEvent(
                device_id=d.id,
                student_id=d.student_id,
                motivo=motivo
            )
            db.session.add(ev)

            eventos.append({
                "device_id": d.id,
                "student_id": d.student_id,
                "motivo": motivo
            })

    db.session.commit()

    return jsonify({
        "eventos_detectados": eventos,
        "total": len(eventos)
    })

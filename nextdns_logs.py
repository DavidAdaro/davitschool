import requests
from datetime import datetime, timedelta

# ===============================
# CONFIGURACIÓN NEXTDNS
# ===============================

NEXTDNS_API_KEY = "658b6594906e85c8ef0181242c4da09e79680313"
BASE_URL = "https://api.nextdns.io"

HEADERS = {
    "X-Api-Key": NEXTDNS_API_KEY,
    "Content-Type": "application/json"
}


# ===============================
# OBTENER LOGS DE UN PERFIL
# ===============================

def get_logs_for_profile(profile_id: str, minutes: int = 15) -> list:
    """
    Obtiene logs DNS reales de NextDNS para un profile_id
    Devuelve una lista de dicts normalizados

    minutes: ventana de tiempo hacia atrás
    """

    since = datetime.utcnow() - timedelta(minutes=minutes)

    params = {
        "profile": profile_id,
        "from": int(since.timestamp())
    }

    url = f"{BASE_URL}/logs"

    try:
        r = requests.get(url, headers=HEADERS, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        print(f"❌ Error consultando logs NextDNS ({profile_id}):", e)
        return []

    logs = []

    for entry in data.get("data", []):
        try:
            logs.append({
                "timestamp": datetime.utcfromtimestamp(entry.get("timestamp")),
                "ip": entry.get("client", {}).get("ip"),
                "asn": entry.get("client", {}).get("asn"),
                "country": entry.get("client", {}).get("country"),
                "query": entry.get("domain"),
                "type": entry.get("type"),
                "blocked": entry.get("blocked", False),
            })
        except Exception:
            continue

    return logs

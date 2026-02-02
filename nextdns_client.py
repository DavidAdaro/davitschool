import requests
from config import Config

BASE_URL = "https://api.nextdns.io"
HEADERS = {"X-Api-Key": Config.NEXTDNS_API_KEY, "Content-Type": "application/json"}

def create_profile(student, device_tipo):
    """Crea perfil con formato: Nombre Apellido, Curso - Tipo"""
    profile_name = f"{student.nombre} {student.apellido}, {student.course.nombre} - {device_tipo}"
    url = f"{BASE_URL}/profiles"
    try:
        r = requests.post(url, headers=HEADERS, json={"name": profile_name})
        r.raise_for_status()
        data = r.json()
        p_id = data.get("data", {}).get("id") or data.get("id")
        if p_id:
            sync_with_base_config(p_id)
            return p_id
    except Exception as e:
        print(f"Error NextDNS: {e}")
    return None

def sync_with_base_config(target_id):
    """Aplica la configuración de seguridad del ID maestro a este nuevo perfil."""
    # Aquí iría el código para parchear seguridad/privacidad basado en el ID base
    pass

def delete_profile(profile_id):
    url = f"{BASE_URL}/profiles/{profile_id}"
    try:
        requests.delete(url, headers=HEADERS)
    except Exception as e:
        print(f"Error borrando perfil: {e}")

def has_active_traffic(profile_id):
    url = f"{BASE_URL}/profiles/{profile_id}/analytics/status"
    try:
        r = requests.get(url, headers=HEADERS)
        return r.json().get("status") == "active"
    except:
        return False
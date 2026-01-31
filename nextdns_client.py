import requests
import datetime
import json

# ===============================
# CONFIGURACION NEXTDNS
# ===============================
NEXTDNS_API_KEY = "658b6594906e85c8ef0181242c4da09e79680313"
BASE_URL = "https://api.nextdns.io"

HEADERS = {
    "X-Api-Key": NEXTDNS_API_KEY,
    "Content-Type": "application/json"
}

# ===============================
# FUNCIONES BASE
# ===============================
def create_profile(profile_name: str) -> dict:
    url = f"{BASE_URL}/profiles"
    payload = {"name": profile_name}

    r = requests.post(url, headers=HEADERS, json=payload)
    r.raise_for_status()
    return r.json()


def extract_profile_id(response_json: dict) -> str:
    if isinstance(response_json, dict):
        if "data" in response_json and "id" in response_json["data"]:
            return response_json["data"]["id"]
        if "id" in response_json:
            return response_json["id"]

    raise ValueError(
        f"No se pudo extraer profile id. Respuesta: {response_json}"
    )


def delete_profile(profile_id: str) -> bool:
    url = f"{BASE_URL}/profiles/{profile_id}"
    r = requests.delete(url, headers=HEADERS)
    r.raise_for_status()
    return True


# ===============================
# FUNCIONES LOGICAS FUTURAS
# ===============================
def enable_device(device):
    print("[NextDNS] ACTIVAR", device.nextdns_profile_id, device.nombre)


def disable_device(device):
    print("[NextDNS] DESACTIVAR", device.nextdns_profile_id, device.nombre)


# ===============================
# TEST MANUAL
# ===============================
if __name__ == "__main__":
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    name = f"PRUEBA_{ts}"

    print("Creando perfil:", name)
    resp = create_profile(name)
    print(json.dumps(resp, indent=2))

    pid = extract_profile_id(resp)
    print("ID:", pid)

    input("ENTER para borrar...")
    delete_profile(pid)
    print("OK")

# evasion_engine.py

from datetime import datetime, timedelta
from models import db, Student, Device, EvasionEvent
from policy_engine import should_use_nextdns
from nextdns_logs import get_logs_for_profile

# =========================
# CONFIGURACIÓN
# =========================

DNS_INACTIVE_MINUTES = 10
CLONE_WINDOW_MINUTES = 5
VPN_WINDOW_MINUTES = 5


# =========================
# FUNCIÓN PRINCIPAL (ENTRYPOINT)
# =========================

def detect_evasions(student: Student, now: datetime):
    """
    Detecta evasiones SOLO si NextDNS debería estar activo.
    Nunca lanza excepción.
    """

    if not should_use_nextdns(student, now):
        return

    for device in student.devices:
        try:
            _check_dns_inactive(student, device, now)
            _check_id_cloning(student, device, now)
            _check_vpn_or_proxy(student, device, now)

        except Exception as e:
            print(
                f"[EVASION] Error device={device.id} student={student.id}: {e}"
            )


# ======================================================
# BLOQUE b2 — DNS INACTIVO (sin logs)
# ======================================================

def _check_dns_inactive(student, device, now):
    """
    No hay logs recientes → DNS privado apagado / borrado
    """

    logs = get_logs_for_profile(
        profile_id=device.nextdns_profile_id,
        since_minutes=DNS_INACTIVE_MINUTES
    )

    if logs:
        return

    if _recent_event_exists(
        device.id, "DNS_INACTIVO", DNS_INACTIVE_MINUTES
    ):
        return

    _create_event(
        student.id,
        device.id,
        "DNS_INACTIVO"
    )


# ======================================================
# BLOQUE b3 — CLONACIÓN DE ID
# ======================================================

def _check_id_cloning(student, device, now):
    """
    Detecta:
    - múltiples IP
    - múltiples ASN
    - múltiples países
    """

    logs = get_logs_for_profile(
        profile_id=device.nextdns_profile_id,
        since_minutes=CLONE_WINDOW_MINUTES
    )

    if not logs:
        return

    ips = set()
    asns = set()
    countries = set()

    for log in logs:
        if log.get("ip"):
            ips.add(log["ip"])
        if log.get("asn"):
            asns.add(log["asn"])
        if log.get("country"):
            countries.add(log["country"])

    # 1 IP → OK
    if len(ips) <= 1:
        return

    # Excepción: red móvil (mismo ASN)
    if len(asns) == 1:
        return

    if _recent_event_exists(
        device.id, "CLONACION_ID", CLONE_WINDOW_MINUTES
    ):
        return

    _create_event(
        student.id,
        device.id,
        "CLONACION_ID"
    )


# ======================================================
# BLOQUE b4 — VPN / PROXY / EVASIÓN AVANZADA
# ======================================================

def _check_vpn_or_proxy(student, device, now):
    """
    Heurísticas reales:
    - ASN conocidos de VPN
    - categoría vpn/proxy en logs
    - cambios de país imposibles
    """

    logs = get_logs_for_profile(
        profile_id=device.nextdns_profile_id,
        since_minutes=VPN_WINDOW_MINUTES
    )

    if not logs:
        return

    vpn_flags = 0
    countries = set()

    for log in logs:
        if log.get("is_vpn") is True:
            vpn_flags += 1

        category = log.get("category", "").lower()
        if "vpn" in category or "proxy" in category:
            vpn_flags += 1

        if log.get("country"):
            countries.add(log["country"])

    # Cambio de país rápido → sospechoso
    if len(countries) > 1:
        vpn_flags += 1

    if vpn_flags == 0:
        return

    if _recent_event_exists(
        device.id, "VPN_PROXY", VPN_WINDOW_MINUTES
    ):
        return

    _create_event(
        student.id,
        device.id,
        "VPN_PROXY"
    )


# ======================================================
# HELPERS
# ======================================================

def _recent_event_exists(device_id, motivo, minutes):
    since = datetime.utcnow() - timedelta(minutes=minutes)

    return (
        EvasionEvent.query
        .filter_by(device_id=device_id, motivo=motivo)
        .filter(EvasionEvent.fecha >= since)
        .first()
        is not None
    )


def _create_event(student_id, device_id, motivo):
    event = EvasionEvent(
        student_id=student_id,
        device_id=device_id,
        motivo=motivo,
        notificado=False
    )

    db.session.add(event)
    db.session.commit()

    print(
        f"[EVASION] {motivo} | student={student_id} device={device_id}"
    )


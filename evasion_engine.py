
from datetime import datetime, timedelta
from models import db, Student, Device, EvasionEvent
from policy_engine import should_use_nextdns
from nextdns_logs import get_logs_for_profile

DNS_INACTIVE_MINUTES = 20 # Aumentado para reducir falsos positivos

def detect_evasions(student: Student, now: datetime):
    if not should_use_nextdns(student, now):
        return

    for device in student.devices:
        try:
            # Solo chequeamos clonación y VPN, la inactividad ya no dispara alerta automática
            _check_id_cloning(student, device, now)
            _check_vpn_or_proxy(student, device, now)
        except Exception as e:
            print(f"[EVASION ERROR] {e}")

def _check_id_cloning(student, device, now):
    logs = get_logs_for_profile(device.nextdns_profile_id, minutes=5)
    ips = {log.get("ip") for log in logs if log.get("ip")}
    
    if len(ips) > 1:
        _create_event(student.id, device.id, "ID_CLONADO")

def _check_vpn_or_proxy(student, device, now):
    logs = get_logs_for_profile(device.nextdns_profile_id, minutes=5)
    for log in logs:
        if log.get("is_vpn") or "vpn" in log.get("category", "").lower():
            _create_event(student.id, device.id, "VPN_PROXY")
            break

def _create_event(student_id, device_id, motivo):
    # Evitar duplicados recientes
    hace_poco = datetime.utcnow() - timedelta(minutes=30)
    exists = EvasionEvent.query.filter(
        EvasionEvent.device_id == device_id,
        EvasionEvent.motivo == motivo,
        EvasionEvent.fecha >= hace_poco
    ).first()
    
    if not exists:
        ev = EvasionEvent(student_id=student_id, device_id=device_id, motivo=motivo)
        db.session.add(ev)
        db.session.commit()
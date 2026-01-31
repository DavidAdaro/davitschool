
# alerts_engine.py

from datetime import datetime, timedelta
from models import db, EvasionEvent, Student, Device

# =========================
# CONFIGURACIÓN
# =========================

ALERT_COOLDOWN_MINUTES = 30
ALERT_CHANNELS = ["EMAIL"]  # futuro: SMS, WhatsApp, Webhook


# =========================
# FUNCIÓN PRINCIPAL
# =========================

def process_pending_alerts(now: datetime):
    """
    Procesa eventos de evasión no notificados.
    """
    events = (
        EvasionEvent.query
        .filter_by(notificado=False)
        .order_by(EvasionEvent.fecha.asc())
        .all()
    )

    for event in events:
        try:
            _process_event(event, now)
        except Exception as e:
            print(f"[ALERT] Error procesando evento {event.id}: {e}")


# =========================
# PROCESAMIENTO DE EVENTO
# =========================

def _process_event(event: EvasionEvent, now: datetime):
    """
    Envía alertas y marca el evento como notificado.
    """

    student = Student.query.get(event.student_id)
    device = Device.query.get(event.device_id)

    if not student or not device:
        print("[ALERT] Evento inválido, referencias faltantes")
        _mark_notified(event)
        return

    # Evitar spam: cooldown por alumno + motivo
    if _recent_alert_exists(student.id, event.motivo, now):
        print(f"[ALERT] Cooldown activo para alumno {student.id}")
        _mark_notified(event)
        return

    # Enviar alertas
    if "EMAIL" in ALERT_CHANNELS:
        _send_email_alert(student, device, event)

    # Marcar como notificado
    _mark_notified(event)


# =========================
# EMAIL
# =========================

def _send_email_alert(student, device, event):
    """
    Simulación de envío de email (real se conecta después).
    """

    subject = f"[ALERTA NextDNS] {event.motivo}"
    body = f"""
Alumno: {student.apellido}, {student.nombre}
Curso: {student.course.nombre}
Dispositivo: {device.nombre} ({device.tipo})

Motivo: {event.motivo}
Fecha: {event.fecha}

Esta alerta se generó durante horario escolar.
"""

    recipients = [
        student.email_padre,
        student.email_escuela
    ]

    for email in recipients:
        _send_email(email, subject, body)


def _send_email(to, subject, body):
    """
    MOCK de email.
    Reemplazable por SMTP / SendGrid.
    """
    print("📧 EMAIL ENVIADO")
    print("Para:", to)
    print("Asunto:", subject)
    print(body)
    print("-" * 50)


# =========================
# HELPERS
# =========================

def _mark_notified(event: EvasionEvent):
    event.notificado = True
    event.fecha_notificado = datetime.utcnow()
    db.session.commit()


def _recent_alert_exists(student_id, motivo, now):
    """
    Evita alertas repetidas para mismo alumno/motivo
    """
    since = now - timedelta(minutes=ALERT_COOLDOWN_MINUTES)

    return (
        EvasionEvent.query
        .filter_by(student_id=student_id, motivo=motivo, notificado=True)
        .filter(EvasionEvent.fecha_notificado >= since)
        .first()
        is not None
    )

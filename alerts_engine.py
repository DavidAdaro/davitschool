import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from models import db, Alert, Student, Device
from config import Config

def process_pending_alerts():
    alerts = Alert.query.filter_by(notificado_padre=False).all()
    for alert in alerts:
        student = Student.query.get(alert.student_id)
        device = Device.query.get(alert.device_id)
        if student:
            recipients = [student.email_padre, student.email_escuela]
            if _send_dual_alert(recipients, student, device, alert):
                alert.notificado_padre = True
                db.session.commit()

def _send_dual_alert(recipients, student, device, alert):
    msg = MIMEMultipart()
    msg['From'] = Config.MAIL_DEFAULT_SENDER[1]
    msg['To'] = ", ".join(recipients)
    msg['Subject'] = f"🛡️ DavIT Shield: Evasión Detectada - {student.apellido}"
    
    body = f"""
    Se ha detectado una evasión de seguridad.
    Alumno: {student.nombre} {student.apellido}
    Dispositivo: {device.tipo} ({device.nombre_modelo})
    Fecha: {alert.fecha.strftime('%d/%m/%Y %H:%M')}
    """
    msg.attach(MIMEText(body, 'plain'))
    try:
        with smtplib.SMTP_SSL(Config.MAIL_SERVER, Config.MAIL_PORT) as server:
            server.login(Config.MAIL_USERNAME, Config.MAIL_PASSWORD)
            server.send_message(msg)
        return True
    except:
        return False
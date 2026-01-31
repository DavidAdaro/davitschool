
# alerts_notifier.py

import smtplib
from email.mime.text import MIMEText

# =========================
# CONFIGURACIÓN MAIL
# =========================

SMTP_SERVER = "smtp.tuservidor.com"
SMTP_PORT = 587
SMTP_USER = "alertas@tudominio.com"
SMTP_PASS = "CLAVE"

FROM_EMAIL = "alertas@tudominio.com"

# =========================
# ENVÍO DE MAIL
# =========================

def send_alert_email(subject, body, recipients):
    """
    Envía mail simple de alerta
    """

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = FROM_EMAIL
    msg["To"] = ", ".join(recipients)

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(FROM_EMAIL, recipients, msg.as_string())

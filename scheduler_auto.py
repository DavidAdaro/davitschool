import time
from datetime import datetime

from app import app
from models import Student, db
from engine.scheduler import nextdns_activo_para_alumno
from nextdns_client import enable_device, disable_device

INTERVALO_SEGUNDOS = 60  # cada 1 minuto


def log(msg):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")


def ciclo_scheduler():
    with app.app_context():
        alumnos = Student.query.all()
        ahora = datetime.now()

        for alumno in alumnos:
            activo = nextdns_activo_para_alumno(alumno, ahora)

            for device in alumno.devices:
                if activo and not device.activo:
                    enable_device(device)
                    device.activo = True
                    log(f"ACTIVADO → {alumno.nombre} {alumno.apellido} | {device.nombre}")

                elif not activo and device.activo:
                    disable_device(device)
                    device.activo = False
                    log(f"DESACTIVADO → {alumno.nombre} {alumno.apellido} | {device.nombre}")

        db.session.commit()


if __name__ == "__main__":
    log("🚀 Scheduler automático iniciado")
    while True:
        try:
            ciclo_scheduler()
            time.sleep(INTERVALO_SEGUNDOS)
        except Exception as e:
            log(f"❌ ERROR: {e}")
            time.sleep(10)

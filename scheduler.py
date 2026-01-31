# scheduler.py

from datetime import datetime
import time

from models import Student
from policy_engine import should_use_nextdns
from evasion_engine import detect_evasions
from alerts_engine import process_pending_alerts

# =========================
# CONFIG
# =========================

TICK_SECONDS = 30  # frecuencia del scheduler (segundos)


# =========================
# MAIN LOOP
# =========================

def scheduler_loop():
    print("🟢 Scheduler NextDNS iniciado")

    while True:
        try:
            now = datetime.now()
            print(f"\n⏱️ Scheduler tick: {now}")

            students = Student.query.all()

            # --- BLOQUE 1: detección de evasiones ---
            for student in students:
                try:
                    if should_use_nextdns(student, now):
                        detect_evasions(student, now)
                except Exception as e:
                    print(
                        f"❌ Error evaluando alumno {student.id}: {e}"
                    )

            # --- BLOQUE 2: envío de alertas ---
            try:
                process_pending_alerts(now)
            except Exception as e:
                print(f"❌ Error procesando alertas: {e}")

        except Exception as e:
            print(f"❌ Error general en scheduler: {e}")

        time.sleep(TICK_SECONDS)


# =========================
# ENTRYPOINT
# =========================

if __name__ == "__main__":
    from app import app

    with app.app_context():
        scheduler_loop()


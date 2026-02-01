# scheduler.py

import os
from datetime import datetime
from flask_apscheduler import APScheduler
from models import db, Student
from policy_engine import is_nextdns_active_now
from evasion_engine import detect_evasions
from alerts_engine import process_pending_alerts

# Inicializamos el objeto scheduler
scheduler = APScheduler()

def task_main_loop():
    """
    Esta es la función que Flask-APScheduler ejecutará periódicamente.
    Sustituye al antiguo 'while True'.
    """
    # Importamos la app para tener acceso al contexto de base de datos
    from app import app 
    
    with app.app_context():
        now = datetime.now()
        print(f"\n⏱️ [SCHEDULER] Tick iniciado: {now.strftime('%Y-%m-%d %H:%M:%S')}")

        try:
            # 1. Obtener todos los alumnos
            students = Student.query.all()
            
            # 2. BLOQUE: Detección de evasiones
            for student in students:
                try:
                    # Solo verificamos si la política dice que debe estar protegido ahora
                    if is_nextdns_active_now(student, now):
                        detect_evasions(student, now)
                except Exception as e:
                    print(f"❌ Error evaluando alumno {student.apellido}: {e}")

            # 3. BLOQUE: Procesamiento y envío de alertas (Email, etc.)
            try:
                process_pending_alerts(now)
            except Exception as e:
                print(f"❌ Error en motor de alertas: {e}")

        except Exception as e:
            print(f"❌ Error crítico en el loop del scheduler: {e}")

def init_scheduler(app):
    """
    Configura e inicia el scheduler dentro de la app de Flask.
    """
    app.config['SCHEDULER_API_ENABLED'] = True
    scheduler.init_app(app)
    scheduler.start()

    # Evitar ejecuciones dobles en modo Debug de Flask
    if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        # Agregamos la tarea: cada 2 minutos (puedes ajustar el tiempo)
        scheduler.add_job(
            id='nextdns_main_job',
            func=task_main_loop,
            trigger='interval',
            minutes=2 
        )
        print("🟢 Scheduler NextDNS programado exitosamente.")

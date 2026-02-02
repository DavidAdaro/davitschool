import os
from datetime import datetime
from flask_apscheduler import APScheduler
from models import db, Student, Alert
from policy_engine import is_nextdns_active_now
from nextdns_client import has_active_traffic
from alerts_engine import process_pending_alerts

scheduler = APScheduler()

def security_check_task():
    from app import create_app
    app = create_app()
    with app.app_context():
        now = datetime.now()
        for student in Student.query.all():
            if is_nextdns_active_now(student, now):
                for dev in student.devices:
                    if not has_active_traffic(dev.nextdns_profile_id):
                        db.session.add(Alert(student_id=student.id, device_id=dev.id, tipo_evento="evasion_dns"))
        db.session.commit()
        process_pending_alerts()

def init_scheduler(app):
    scheduler.init_app(app)
    scheduler.start()
    if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        scheduler.add_job(id='patrol', func=security_check_task, trigger='interval', minutes=5)
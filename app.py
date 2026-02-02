import os
from flask import Flask, render_template
from models import db
from config import Config
from routes.students import students_bp
from routes.courses import courses_bp
from routes.calendar import calendar_bp
from routes.devices import devices_bp
from routes.dashboard import dashboard_bp
from scheduler import init_scheduler

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    # Registro de Blueprints
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(students_bp)
    app.register_blueprint(courses_bp)
    app.register_blueprint(calendar_bp)
    app.register_blueprint(devices_bp)

    # Rutas para los Templates (Evita el Error 404)
    @app.route("/courses")
    def ui_courses(): return render_template("courses.html")

    @app.route("/students")
    def ui_students(): return render_template("students.html")

    @app.route("/calendar")
    def ui_calendar(): return render_template("calendar.html")

    @app.route("/alerts")
    def ui_alerts(): return render_template("alerts.html")

    with app.app_context():
        init_scheduler(app)
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)
import os
from flask import Flask
from models import db
from datetime import datetime

from routes.students import students_bp
from routes.devices import devices_bp
from routes.courses import courses_bp
from routes.calendar import calendar_bp
from routes.evasion import evasion_bp
from routes.evasion_notify import notify_bp
from routes.reports import reports_bp
from nextdns_client import create_profile, extract_profile_id, delete_profile
from routes.alerts import alerts_bp

app = Flask(__name__)

# ======================
# DATABASE
# ======================
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
INSTANCE_DIR = os.path.join(BASE_DIR, "instance")
os.makedirs(INSTANCE_DIR, exist_ok=True)

DB_PATH = os.path.join(INSTANCE_DIR, "database.db")

app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# ======================
# NEXTDNS FUNCTIONS
# ======================
def create_device_profile(student, tipo, nombre):
    base_name = f"{student.apellido}_{student.nombre}_{tipo}_{nombre}"
    profile_name = base_name.replace(" ", "_")

    response = create_profile(profile_name)

    # Manejo de duplicados
    if isinstance(response, dict) and "errors" in response:
        if response["errors"][0].get("code") == "duplicate":
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            profile_name = f"{profile_name}_{ts}"
            response = create_profile(profile_name)

    return extract_profile_id(response)


def delete_device_profile(profile_id):
    delete_profile(profile_id)


app.config["CREATE_DEVICE_PROFILE"] = create_device_profile
app.config["DELETE_DEVICE_PROFILE"] = delete_device_profile

# ======================
# BLUEPRINTS
# ======================
app.register_blueprint(students_bp)
app.register_blueprint(devices_bp)
app.register_blueprint(courses_bp)
app.register_blueprint(calendar_bp)
app.register_blueprint(evasion_bp)
app.register_blueprint(notify_bp)
app.register_blueprint(reports_bp)
app.register_blueprint(alerts_bp)

# ======================
# ROOT
# ======================
@app.route("/")
def index():
    return "Panel NextDNS Colegio OK"
from flask import render_template

@app.route("/courses-ui")
def courses_ui():
    return render_template("courses.html")
@app.route("/students-ui")
def students_ui():
    return render_template("students.html")


# ======================
# START
# ======================
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)

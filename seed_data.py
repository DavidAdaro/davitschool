from app import create_app
from models import db, Course, Student, Device, Alert, CourseSchedule
from datetime import datetime, time

def seed():
    app = create_app()
    with app.app_context():
        # 1. Crear un Curso
        curso = Course(nombre="6to Informatica", turno_base="Mañana")
        db.session.add(curso)
        db.session.flush()

        # 2. Crear un Horario (Lunes de 08:00 a 12:00)
        horario = CourseSchedule(
            course_id=curso.id,
            tipo="escolar",
            dia_semana=0, # Lunes
            hora_inicio=time(8, 0),
            hora_fin=time(12, 0),
            sexo="T"
        )
        db.session.add(horario)

        # 3. Crear Alumnos
        alumno1 = Student(
            nombre="David", apellido="Test", sexo="M", 
            email_padre="tu_correo@ejemplo.com", course_id=curso.id
        )
        alumno2 = Student(
            nombre="Valeria", apellido="Sosa", sexo="F", 
            email_padre="otro@ejemplo.com", course_id=curso.id
        )
        db.session.add_all([alumno1, alumno2])
        db.session.flush()

        # 4. Crear Dispositivos ficticios (IDs de NextDNS de prueba)
        dev1 = Device(student_id=alumno1.id, tipo="Smartphone", nombre_modelo="Samsung S21", nextdns_profile_id="test_id_1")
        dev2 = Device(student_id=alumno2.id, tipo="Tablet", nombre_modelo="iPad Air", nextdns_profile_id="test_id_2")
        db.session.add_all([dev1, dev2])
        db.session.flush()

        # 5. Generar Alertas para que el Dashboard tenga color
        alerta1 = Alert(student_id=alumno1.id, device_id=dev1.id, tipo_evento="falta_registros", fecha=datetime.now())
        alerta2 = Alert(student_id=alumno2.id, device_id=dev2.id, tipo_evento="falta_registros", fecha=datetime.now())
        db.session.add_all([alerta1, alerta2])

        db.session.commit()
        print("✅ Datos de prueba cargados exitosamente.")

if __name__ == "__main__":
    seed()
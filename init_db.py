# init_db.py
from app import app
from models import db, Course, CourseSchedule, Student

def seed_data():
    with app.app_context():
        # 1. Crear las tablas desde cero
        db.create_all()
        print("✅ Tablas creadas.")

        # 2. Crear un Curso de prueba
        curso_test = Course(nombre="5to Año - Computación", turno_base="Mañana")
        db.session.add(curso_test)
        db.session.commit()

        # 3. Crear un Horario para hoy (Lunes a Viernes 08:00 a 13:00)
        # Nota: 0=Lunes, 1=Martes...
        for i in range(5):
            horario = CourseSchedule(
                course_id=curso_test.id,
                tipo="turno",
                dia_semana=i,
                hora_inicio="08:00",
                hora_fin="13:00",
                sexo="ALL"
            )
            db.session.add(horario)
        
        # 4. Crear un Alumno de prueba
        alumno = Student(
            nombre="Juan",
            apellido="Perez",
            sexo="M",
            course_id=curso_test.id,
            email_padre="padre_test@gmail.com", # Pon tu mail aquí para probar
            email_escuela="preceptoria@colegio.com"
        )
        db.session.add(alumno)
        db.session.commit()
        
        print(f"✅ Datos de prueba insertados: Curso '{curso_test.nombre}' y Alumno '{alumno.apellido}'.")
        print("🚀 Ya puedes correr 'python app.py' y verás actividad en el Scheduler.")

if __name__ == "__main__":
    seed_data()
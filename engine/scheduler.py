from datetime import datetime
from models import CourseSchedule
from engine.calendar import dia_bloqueado, evento_especial_activo


def hora_en_rango(hora_actual, inicio, fin):
    h_ini = datetime.strptime(inicio, "%H:%M").time()
    h_fin = datetime.strptime(fin, "%H:%M").time()
    return h_ini <= hora_actual < h_fin


def schedule_aplica(schedule, sexo_alumno, comision_alumno):
    if schedule.sexo != "ALL" and schedule.sexo != sexo_alumno:
        return False

    if schedule.comision and schedule.comision != comision_alumno:
        return False

    return True


def nextdns_activo_para_alumno(student, fecha_hora=None):
    if student is None:
        return False

    if fecha_hora is None:
        fecha_hora = datetime.now()

    # Bloqueo total por calendario
    if dia_bloqueado(fecha_hora):
        return False

    # Evento especial fuerza activacion
    if evento_especial_activo(fecha_hora):
        return True

    dia_semana = fecha_hora.weekday()
    hora_actual = fecha_hora.time()

    schedules = CourseSchedule.query.filter_by(
        course_id=student.course_id,
        dia_semana=dia_semana
    ).all()

    for s in schedules:
        if not schedule_aplica(s, student.sexo, student.comision):
            continue

        if hora_en_rango(hora_actual, s.hora_inicio, s.hora_fin):
            return True

    return False

from datetime import datetime, time
from models import (
    CourseSchedule,
    CalendarBlock,
    SpecialEvent,
    Student,
)


def is_nextdns_active_now(student: Student, now: datetime | None = None) -> bool:
    """
    Determina si NextDNS debe estar activo para un alumno según:
    - calendario (feriados / recesos)
    - eventos especiales
    - horarios del curso (turno, contraturno, tiempo muerto)
    """

    if now is None:
        now = datetime.now()

    today = now.date()
    current_time = now.time()
    weekday = now.weekday()  # 0 = lunes

    # --------------------------------------------------
    # 1. CALENDARIO BLOQUEANTE
    # --------------------------------------------------
    calendar_blocks = CalendarBlock.query.filter(
        CalendarBlock.eliminado == False,
        CalendarBlock.fecha_inicio <= today,
        CalendarBlock.fecha_fin >= today,
    ).all()

    if calendar_blocks:
        # Excepción: evento especial
        events = SpecialEvent.query.filter_by(fecha=today).all()
        for ev in events:
            if time.fromisoformat(ev.hora_inicio) <= current_time <= time.fromisoformat(ev.hora_fin):
                return True
        return False

    # --------------------------------------------------
    # 2. HORARIOS DEL CURSO
    # --------------------------------------------------
    schedules = CourseSchedule.query.filter_by(
        course_id=student.course_id,
        dia_semana=weekday
    ).all()

    for sch in schedules:
        # filtro sexo
        if sch.sexo != "ALL" and sch.sexo != student.sexo:
            continue

        # filtro comisión
        if sch.comision and sch.comision != student.comision:
            continue

        start = time.fromisoformat(sch.hora_inicio)
        end = time.fromisoformat(sch.hora_fin)

        if start <= current_time <= end:
            return True

    # --------------------------------------------------
    # 3. FUERA DE TODO HORARIO
    # --------------------------------------------------
    return False


# Alias semántico (para scheduler / evasion_engine)
def should_use_nextdns(student: Student, now: datetime | None = None) -> bool:
    return is_nextdns_active_now(student, now)

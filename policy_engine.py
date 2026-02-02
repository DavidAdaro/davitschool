from datetime import datetime
from models import CourseSchedule, CalendarExclusion, SpecialEvent, Student

def is_nextdns_active_now(student: Student, now: datetime | None = None) -> bool:
    """
    JERARQUÍA: 1. Eventos Especiales (ON) | 2. Feriados (OFF) | 3. Horarios + Tiempos Muertos (ON)
    """
    if now is None: now = datetime.now()
    today, cur_time, wday = now.date(), now.time(), now.weekday()

    # 1. EVENTOS ESPECIALES (Campamentos, etc.) -> Prioridad Máxima ON
    special = SpecialEvent.query.filter(SpecialEvent.fecha == today).all()
    for ev in special:
        if ev.hora_inicio <= cur_time <= ev.hora_fin:
            return True

    # 2. CALENDARIO BLOQUEANTE (Feriados, Recesos) -> Prioridad OFF
    exclusion = CalendarExclusion.query.filter(
        CalendarExclusion.fecha_inicio <= today,
        CalendarExclusion.fecha_fin >= today
    ).first()
    if exclusion:
        return False

    # 3. HORARIOS Y TIEMPOS MUERTOS
    schedules = CourseSchedule.query.filter_by(course_id=student.course_id, dia_semana=wday).all()
    applicable_times = []

    for sch in schedules:
        # Filtrar por sexo (Gimnasia) y Comisión
        if sch.sexo in ['T', student.sexo] and (not sch.comision or sch.comision == student.comision):
            applicable_times.append((sch.hora_inicio, sch.hora_fin))

    if not applicable_times:
        return False

    # Lógica de Tiempos Muertos: Protege desde la primera clase hasta la última del día
    start_day = min(t[0] for t in applicable_times)
    end_day = max(t[1] for t in applicable_times)

    return start_day <= cur_time <= end_day
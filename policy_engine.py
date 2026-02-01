from datetime import datetime, time
from models import (
    CourseSchedule,
    CalendarBlock,
    SpecialEvent,
    Student,
)

def is_nextdns_active_now(student: Student, now: datetime | None = None) -> bool:
    """
    Determina si NextDNS debe estar activo para un alumno.
    JERARQUÍA DE LÓGICA CORREGIDA:
    1. Eventos Especiales (Prioridad Máxima: ON)
    2. Calendario Bloqueante (Prioridad Media: OFF)
    3. Horarios de Curso (Prioridad Base: ON/OFF)
    """
    if now is None:
        now = datetime.now()

    today = now.date()
    current_time = now.time()
    weekday = now.weekday()  # 0 = lunes

    # --- 1. EVENTOS ESPECIALES (FUERZA ENCENDIDO) ---
    # Si hay un evento especial ahora, se activa NextDNS sin importar el calendario
    special_event = SpecialEvent.query.filter_by(fecha=today).all()
    for ev in special_event:
        start = time.fromisoformat(ev.hora_inicio)
        end = time.fromisoformat(ev.hora_fin)
        if start <= current_time <= end:
            return True

    # --- 2. CALENDARIO BLOQUEANTE (FUERZA APAGADO) ---
    # Si no hay evento especial, revisamos si es feriado o receso
    calendar_block = CalendarBlock.query.filter(
        CalendarBlock.eliminado == False,
        CalendarBlock.fecha_inicio <= today,
        CalendarBlock.fecha_fin >= today,
    ).first()
    
    if calendar_block:
        return False

    # --- 3. HORARIOS DEL CURSO (LÓGICA BASE) ---
    schedules = CourseSchedule.query.filter_by(
        course_id=student.course_id,
        dia_semana=weekday
    ).all()

    for sch in schedules:
        # Filtro estricto por sexo (Gimnasia)
        if sch.sexo != "ALL" and sch.sexo != student.sexo:
            continue

        # Filtro por comisión
        if sch.comision and sch.comision != student.comision:
            continue

        start = time.fromisoformat(sch.hora_inicio)
        end = time.fromisoformat(sch.hora_fin)

        if start <= current_time <= end:
            return True

    return False

def should_use_nextdns(student, now):
    return is_nextdns_active_now(student, now)

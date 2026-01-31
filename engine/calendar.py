
from datetime import datetime
from models import CalendarBlock, SpecialEvent


def dia_bloqueado(fecha_hora):
    fecha = fecha_hora.date()

    blocks = CalendarBlock.query.filter(
        CalendarBlock.fecha_inicio <= fecha,
        CalendarBlock.fecha_fin >= fecha,
        CalendarBlock.eliminado == False
    ).all()

    return len(blocks) > 0


def evento_especial_activo(fecha_hora):
    fecha = fecha_hora.date()
    hora = fecha_hora.time()

    events = SpecialEvent.query.filter_by(fecha=fecha).all()

    for e in events:
        h_ini = datetime.strptime(e.hora_inicio, "%H:%M").time()
        h_fin = datetime.strptime(e.hora_fin, "%H:%M").time()

        if h_ini <= hora < h_fin:
            return True

    return False

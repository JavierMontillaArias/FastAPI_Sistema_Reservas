from typing import List, Optional
from datetime import datetime, timedelta, time
from app.models.reserva import ReservaCreate, ReservaUpdate
from app.database import obtener_conexion
from app.exceptions.custom_exceptions import (
    ClienteNoEncontradoError,
    MesaNoDisponibleError,
    ReservaSolapadaError,
    CapacidadExcedidaError,
    FueraDeHorarioError,
    CancelacionNoPermitidaError
)

HORARIO_COMIDA_INICIO = time(12, 0)
HORARIO_COMIDA_FIN = time(16, 0)
HORARIO_CENA_INICIO = time(20, 0)
HORARIO_CENA_FIN = time(0, 0)
DURACION_RESERVA_HORAS = 2


def listar_todas(fecha: Optional[str] = None, cliente_id: Optional[int] = None, mesa_id: Optional[int] = None, estado: Optional[str] = None) -> List[dict]:
    conn = obtener_conexion()
    cursor = conn.cursor()
    
    sql = "SELECT * FROM reservas WHERE 1=1"
    params = []
    
    if fecha:
        sql += " AND DATE(fecha_hora_inicio) = ?"
        params.append(fecha)
    
    if cliente_id:
        sql += " AND cliente_id = ?"
        params.append(cliente_id)
    
    if mesa_id:
        sql += " AND mesa_id = ?"
        params.append(mesa_id)
    
    if estado:
        sql += " AND estado = ?"
        params.append(estado)
    
    cursor.execute(sql, params)
    reservas = [dict(row) for row in cursor.fetchall()]
    
    for reserva in reservas:
        reserva["fecha_hora_inicio"] = datetime.fromisoformat(reserva["fecha_hora_inicio"])
        reserva["fecha_hora_fin"] = datetime.fromisoformat(reserva["fecha_hora_fin"])
        reserva["fecha_creacion"] = datetime.fromisoformat(reserva["fecha_creacion"])
    
    conn.close()
    return reservas


def obtener_por_id(reserva_id: int) -> Optional[dict]:
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM reservas WHERE id = ?", (reserva_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        reserva = dict(row)
        reserva["fecha_hora_inicio"] = datetime.fromisoformat(reserva["fecha_hora_inicio"])
        reserva["fecha_hora_fin"] = datetime.fromisoformat(reserva["fecha_hora_fin"])
        reserva["fecha_creacion"] = datetime.fromisoformat(reserva["fecha_creacion"])
        return reserva
    return None


def obtener_con_detalles(reserva_id: int) -> Optional[dict]:
    conn = obtener_conexion()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            r.*,
            c.nombre as cliente_nombre,
            c.email as cliente_email,
            m.numero as mesa_numero,
            m.ubicacion as mesa_ubicacion
        FROM reservas r
        JOIN clientes c ON r.cliente_id = c.id
        JOIN mesas m ON r.mesa_id = m.id
        WHERE r.id = ?
    """, (reserva_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        reserva = dict(row)
        reserva["fecha_hora_inicio"] = datetime.fromisoformat(reserva["fecha_hora_inicio"])
        reserva["fecha_hora_fin"] = datetime.fromisoformat(reserva["fecha_hora_fin"])
        reserva["fecha_creacion"] = datetime.fromisoformat(reserva["fecha_creacion"])
        
        reserva["cliente"] = {
            "nombre": reserva.pop("cliente_nombre"),
            "email": reserva.pop("cliente_email")
        }
        reserva["mesa"] = {
            "numero": reserva.pop("mesa_numero"),
            "ubicacion": reserva.pop("mesa_ubicacion")
        }
        
        return reserva
    return None


def validar_horario_operacion(fecha_hora: datetime) -> bool:
    hora = fecha_hora.time()
    
    if HORARIO_COMIDA_INICIO <= hora < HORARIO_COMIDA_FIN:
        return True
    
    if hora >= HORARIO_CENA_INICIO or hora < time(0, 1):
        return True
    
    return False


def verificar_solapamiento(mesa_id: int, fecha_hora_inicio: datetime, fecha_hora_fin: datetime, excluir_reserva_id: Optional[int] = None) -> bool:
    conn = obtener_conexion()
    cursor = conn.cursor()
    
    sql = """
        SELECT COUNT(*) as count FROM reservas
        WHERE mesa_id = ?
        AND estado != 'cancelada'
        AND fecha_hora_inicio < ?
        AND fecha_hora_fin > ?
    """
    params = [mesa_id, fecha_hora_fin.isoformat(), fecha_hora_inicio.isoformat()]
    
    if excluir_reserva_id:
        sql += " AND id != ?"
        params.append(excluir_reserva_id)
    
    cursor.execute(sql, params)
    count = cursor.fetchone()["count"]
    conn.close()
    
    return count > 0


def obtener_mesas_disponibles(fecha_hora_inicio: datetime, num_comensales: int) -> List[dict]:
    fecha_hora_fin = fecha_hora_inicio + timedelta(hours=DURACION_RESERVA_HORAS)
    
    conn = obtener_conexion()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM mesas
        WHERE activa = 1
        AND capacidad >= ?
        AND id NOT IN (
            SELECT mesa_id FROM reservas
            WHERE estado != 'cancelada'
            AND fecha_hora_inicio < ?
            AND fecha_hora_fin > ?
        )
    """, (num_comensales, fecha_hora_fin.isoformat(), fecha_hora_inicio.isoformat()))
    
    mesas = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return mesas


def crear(reserva_data: ReservaCreate) -> dict:
    conn = obtener_conexion()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM clientes WHERE id = ?", (reserva_data.cliente_id,))
    cliente = cursor.fetchone()
    if not cliente:
        conn.close()
        raise ClienteNoEncontradoError(f"No existe un cliente con ID {reserva_data.cliente_id}")
    
    cursor.execute("SELECT * FROM mesas WHERE id = ?", (reserva_data.mesa_id,))
    mesa_row = cursor.fetchone()
    if not mesa_row:
        conn.close()
        raise MesaNoDisponibleError(f"No existe una mesa con ID {reserva_data.mesa_id}")
    
    mesa = dict(mesa_row)
    
    if not mesa["activa"]:
        conn.close()
        raise MesaNoDisponibleError(f"La mesa {mesa['numero']} no está activa actualmente")
    
    if reserva_data.fecha_hora_inicio <= datetime.now():
        conn.close()
        raise ValueError("No se pueden crear reservas en el pasado")
    
    if not validar_horario_operacion(reserva_data.fecha_hora_inicio):
        conn.close()
        raise FueraDeHorarioError(
            "La reserva está fuera del horario de operación. "
            "Horarios: 12:00-16:00 (comidas) y 20:00-00:00 (cenas)"
        )
    
    if reserva_data.num_comensales > mesa["capacidad"]:
        conn.close()
        raise CapacidadExcedidaError(
            f"El número de comensales ({reserva_data.num_comensales}) "
            f"excede la capacidad de la mesa ({mesa['capacidad']})"
        )
    
    fecha_hora_fin = reserva_data.fecha_hora_inicio + timedelta(hours=DURACION_RESERVA_HORAS)
    
    if verificar_solapamiento(reserva_data.mesa_id, reserva_data.fecha_hora_inicio, fecha_hora_fin):
        mesas_alternativas = obtener_mesas_disponibles(reserva_data.fecha_hora_inicio, reserva_data.num_comensales)
        numeros_alternativas = [m["numero"] for m in mesas_alternativas]
        conn.close()
        
        raise ReservaSolapadaError(
            f"La mesa {mesa['numero']} ya tiene una reserva en ese horario. "
            f"Mesas disponibles: {', '.join(map(str, numeros_alternativas)) if numeros_alternativas else 'ninguna'}"
        )
    
    cursor.execute("""
        INSERT INTO reservas (cliente_id, mesa_id, fecha_hora_inicio, fecha_hora_fin, num_comensales, estado, notas)
        VALUES (?, ?, ?, ?, ?, 'pendiente', ?)
    """, (
        reserva_data.cliente_id,
        reserva_data.mesa_id,
        reserva_data.fecha_hora_inicio.isoformat(),
        fecha_hora_fin.isoformat(),
        reserva_data.num_comensales,
        reserva_data.notas
    ))
    
    reserva_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return obtener_por_id(reserva_id)


def actualizar(reserva_id: int, reserva_data: ReservaUpdate) -> Optional[dict]:
    reserva = obtener_por_id(reserva_id)
    if not reserva:
        return None
    
    if reserva["estado"] in ["completada", "cancelada"]:
        raise ValueError(f"No se puede modificar una reserva en estado '{reserva['estado']}'")
    
    conn = obtener_conexion()
    cursor = conn.cursor()
    
    campos = []
    valores = []
    
    if reserva_data.mesa_id is not None:
        cursor.execute("SELECT * FROM mesas WHERE id = ?", (reserva_data.mesa_id,))
        mesa_row = cursor.fetchone()
        if not mesa_row:
            conn.close()
            raise MesaNoDisponibleError(f"No existe una mesa con ID {reserva_data.mesa_id}")
        
        mesa = dict(mesa_row)
        if not mesa["activa"]:
            conn.close()
            raise MesaNoDisponibleError(f"La mesa {mesa['numero']} no está activa")
        
        campos.append("mesa_id = ?")
        valores.append(reserva_data.mesa_id)
        reserva["mesa_id"] = reserva_data.mesa_id
    
    if reserva_data.fecha_hora_inicio is not None:
        if reserva_data.fecha_hora_inicio <= datetime.now():
            conn.close()
            raise ValueError("No se pueden crear reservas en el pasado")
        
        if not validar_horario_operacion(reserva_data.fecha_hora_inicio):
            conn.close()
            raise FueraDeHorarioError(
                "La reserva está fuera del horario de operación. "
                "Horarios: 12:00-16:00 (comidas) y 20:00-00:00 (cenas)"
            )
        
        fecha_hora_fin = reserva_data.fecha_hora_inicio + timedelta(hours=DURACION_RESERVA_HORAS)
        campos.append("fecha_hora_inicio = ?")
        valores.append(reserva_data.fecha_hora_inicio.isoformat())
        campos.append("fecha_hora_fin = ?")
        valores.append(fecha_hora_fin.isoformat())
        reserva["fecha_hora_inicio"] = reserva_data.fecha_hora_inicio
        reserva["fecha_hora_fin"] = fecha_hora_fin
    
    if reserva_data.num_comensales is not None:
        cursor.execute("SELECT capacidad FROM mesas WHERE id = ?", (reserva["mesa_id"],))
        capacidad = cursor.fetchone()["capacidad"]
        
        if reserva_data.num_comensales > capacidad:
            conn.close()
            raise CapacidadExcedidaError(
                f"El número de comensales ({reserva_data.num_comensales}) "
                f"excede la capacidad de la mesa ({capacidad})"
            )
        
        campos.append("num_comensales = ?")
        valores.append(reserva_data.num_comensales)
    
    if reserva_data.notas is not None:
        campos.append("notas = ?")
        valores.append(reserva_data.notas)
    
    if verificar_solapamiento(
        reserva["mesa_id"],
        reserva["fecha_hora_inicio"],
        reserva["fecha_hora_fin"],
        excluir_reserva_id=reserva_id
    ):
        conn.close()
        raise ReservaSolapadaError("La modificación genera un conflicto de horario con otra reserva")
    
    if campos:
        valores.append(reserva_id)
        sql = f"UPDATE reservas SET {', '.join(campos)} WHERE id = ?"
        cursor.execute(sql, valores)
        conn.commit()
    
    conn.close()
    return obtener_por_id(reserva_id)


def cancelar(reserva_id: int) -> Optional[dict]:
    reserva = obtener_por_id(reserva_id)
    if not reserva:
        return None
    
    if reserva["estado"] not in ["pendiente", "confirmada"]:
        raise CancelacionNoPermitidaError(f"No se puede cancelar una reserva en estado '{reserva['estado']}'")
    
    tiempo_hasta_reserva = reserva["fecha_hora_inicio"] - datetime.now()
    if tiempo_hasta_reserva < timedelta(hours=2):
        raise CancelacionNoPermitidaError("No se puede cancelar una reserva con menos de 2 horas de antelación")
    
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("UPDATE reservas SET estado = 'cancelada' WHERE id = ?", (reserva_id,))
    conn.commit()
    conn.close()
    
    return obtener_por_id(reserva_id)


def confirmar(reserva_id: int) -> Optional[dict]:
    reserva = obtener_por_id(reserva_id)
    if not reserva:
        return None
    
    if reserva["estado"] != "pendiente":
        raise ValueError("Solo se pueden confirmar reservas pendientes")
    
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("UPDATE reservas SET estado = 'confirmada' WHERE id = ?", (reserva_id,))
    conn.commit()
    conn.close()
    
    return obtener_por_id(reserva_id)


def completar(reserva_id: int) -> Optional[dict]:
    reserva = obtener_por_id(reserva_id)
    if not reserva:
        return None
    
    if reserva["estado"] != "confirmada":
        raise ValueError("Solo se pueden completar reservas confirmadas")
    
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("UPDATE reservas SET estado = 'completada' WHERE id = ?", (reserva_id,))
    conn.commit()
    conn.close()
    
    return obtener_por_id(reserva_id)
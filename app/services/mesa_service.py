from typing import List, Optional
from app.models.mesa import MesaCreate, MesaUpdate
from app.database import obtener_conexion


def listar_todos() -> List[dict]:
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM mesas")
    mesas = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return mesas


def listar_activas() -> List[dict]:
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM mesas WHERE activa = 1")
    mesas = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return mesas


def obtener_por_id(mesa_id: int) -> Optional[dict]:
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM mesas WHERE id = ?", (mesa_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return dict(row)
    return None


def obtener_por_numero(numero: int) -> Optional[dict]:
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM mesas WHERE numero = ?", (numero,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return dict(row)
    return None


def crear(mesa_data: MesaCreate) -> dict:
    if obtener_por_numero(mesa_data.numero):
        raise ValueError(f"Ya existe una mesa con el número {mesa_data.numero}")
    
    if mesa_data.numero < 1 or mesa_data.numero > 99:
        raise ValueError("El número de mesa debe estar entre 1 y 99")
    
    if mesa_data.capacidad not in [2, 4, 6, 8]:
        raise ValueError("La capacidad debe ser 2, 4, 6 u 8")
    
    if mesa_data.ubicacion not in ["interior", "terraza", "privado"]:
        raise ValueError("La ubicación debe ser interior, terraza o privado")
    
    conn = obtener_conexion()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO mesas (numero, capacidad, ubicacion, activa)
        VALUES (?, ?, ?, ?)
    """, (mesa_data.numero, mesa_data.capacidad, mesa_data.ubicacion, mesa_data.activa))
    
    mesa_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return obtener_por_id(mesa_id)


def actualizar(mesa_id: int, mesa_data: MesaUpdate) -> Optional[dict]:
    mesa = obtener_por_id(mesa_id)
    if not mesa:
        return None
    
    if mesa_data.numero is not None:
        if mesa_data.numero < 1 or mesa_data.numero > 99:
            raise ValueError("El número de mesa debe estar entre 1 y 99")
        
        mesa_existente = obtener_por_numero(mesa_data.numero)
        if mesa_existente and mesa_existente["id"] != mesa_id:
            raise ValueError(f"Ya existe una mesa con el número {mesa_data.numero}")
    
    conn = obtener_conexion()
    cursor = conn.cursor()
    
    campos = []
    valores = []
    
    if mesa_data.numero is not None:
        campos.append("numero = ?")
        valores.append(mesa_data.numero)
    
    if mesa_data.capacidad is not None:
        campos.append("capacidad = ?")
        valores.append(mesa_data.capacidad)
    
    if mesa_data.ubicacion is not None:
        campos.append("ubicacion = ?")
        valores.append(mesa_data.ubicacion)
    
    if mesa_data.activa is not None:
        campos.append("activa = ?")
        valores.append(1 if mesa_data.activa else 0)
    
    if campos:
        valores.append(mesa_id)
        sql = f"UPDATE mesas SET {', '.join(campos)} WHERE id = ?"
        cursor.execute(sql, valores)
        conn.commit()
    
    conn.close()
    
    return obtener_por_id(mesa_id)


def eliminar(mesa_id: int) -> bool:
    mesa = obtener_por_id(mesa_id)
    if not mesa:
        return False
    
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM mesas WHERE id = ?", (mesa_id,))
    conn.commit()
    conn.close()
    
    return True


def obtener_disponibles(fecha_hora: str, num_comensales: int) -> List[dict]:
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM mesas 
        WHERE activa = 1 AND capacidad >= ?
    """, (num_comensales,))
    
    mesas = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return mesas
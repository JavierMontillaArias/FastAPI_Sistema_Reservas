from typing import List, Optional
from datetime import datetime
from app.models.cliente import ClienteCreate, ClienteUpdate
from app.database import obtener_conexion


def listar_todos() -> List[dict]:
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clientes")
    clientes = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return clientes


def obtener_por_id(cliente_id: int) -> Optional[dict]:
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clientes WHERE id = ?", (cliente_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return dict(row)
    return None


def obtener_por_email(email: str) -> Optional[dict]:
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clientes WHERE email = ?", (email,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return dict(row)
    return None


def crear(cliente_data: ClienteCreate) -> dict:
    if len(cliente_data.nombre.strip()) < 3:
        raise ValueError("El nombre debe tener al menos 3 caracteres")
    
    if obtener_por_email(cliente_data.email):
        raise ValueError("El email ya está registrado")
    
    if len(cliente_data.telefono) != 9 or not cliente_data.telefono.isdigit():
        raise ValueError("El teléfono debe tener exactamente 9 dígitos")
    
    conn = obtener_conexion()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO clientes (nombre, email, telefono, notas)
        VALUES (?, ?, ?, ?)
    """, (cliente_data.nombre, cliente_data.email, cliente_data.telefono, cliente_data.notas))
    
    cliente_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return obtener_por_id(cliente_id)


def actualizar(cliente_id: int, cliente_data: ClienteUpdate) -> Optional[dict]:
    cliente = obtener_por_id(cliente_id)
    if not cliente:
        return None
    
    if cliente_data.nombre is not None:
        if len(cliente_data.nombre.strip()) < 3:
            raise ValueError("El nombre debe tener al menos 3 caracteres")
    
    if cliente_data.email is not None:
        cliente_existente = obtener_por_email(cliente_data.email)
        if cliente_existente and cliente_existente["id"] != cliente_id:
            raise ValueError("El email ya está en uso por otro cliente")
    
    if cliente_data.telefono is not None:
        if len(cliente_data.telefono) != 9 or not cliente_data.telefono.isdigit():
            raise ValueError("El teléfono debe tener exactamente 9 dígitos")
    
    conn = obtener_conexion()
    cursor = conn.cursor()
    
    campos = []
    valores = []
    
    if cliente_data.nombre is not None:
        campos.append("nombre = ?")
        valores.append(cliente_data.nombre)
    
    if cliente_data.email is not None:
        campos.append("email = ?")
        valores.append(cliente_data.email)
    
    if cliente_data.telefono is not None:
        campos.append("telefono = ?")
        valores.append(cliente_data.telefono)
    
    if cliente_data.notas is not None:
        campos.append("notas = ?")
        valores.append(cliente_data.notas)
    
    if campos:
        valores.append(cliente_id)
        sql = f"UPDATE clientes SET {', '.join(campos)} WHERE id = ?"
        cursor.execute(sql, valores)
        conn.commit()
    
    conn.close()
    
    return obtener_por_id(cliente_id)


def eliminar(cliente_id: int) -> bool:
    cliente = obtener_por_id(cliente_id)
    if not cliente:
        return False
    
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM clientes WHERE id = ?", (cliente_id,))
    conn.commit()
    conn.close()
    
    return True


def buscar(termino: str) -> List[dict]:
    conn = obtener_conexion()
    cursor = conn.cursor()
    
    termino_like = f"%{termino}%"
    cursor.execute("""
        SELECT * FROM clientes 
        WHERE nombre LIKE ? OR email LIKE ? OR telefono LIKE ?
    """, (termino_like, termino_like, termino_like))
    
    clientes = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return clientes
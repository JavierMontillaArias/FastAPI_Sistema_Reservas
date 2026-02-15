from fastapi import APIRouter, HTTPException, status
from typing import List
from app.models.cliente import ClienteCreate, ClienteRead, ClienteUpdate
from app.services import cliente_service
from app.database import obtener_conexion

router = APIRouter(
    prefix="/clientes",
    tags=["Clientes"]
)


@router.get("/", response_model=List[ClienteRead])
def listar_clientes():
    """Listar todos los clientes"""
    return cliente_service.listar_todos()


@router.get("/buscar/", response_model=List[ClienteRead])
def buscar_clientes(nombre: str):
    """Buscar clientes por nombre, email o teléfono"""
    return cliente_service.buscar(nombre)


@router.get("/{id}", response_model=ClienteRead)
def obtener_cliente(id: int):
    """Obtener un cliente por su ID"""
    cliente = cliente_service.obtener_por_id(id)
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cliente con ID {id} no encontrado"
        )
    return cliente


@router.post("/", response_model=ClienteRead, status_code=status.HTTP_201_CREATED)
def crear_cliente(cliente: ClienteCreate):
    """Crear un nuevo cliente"""
    try:
        return cliente_service.crear(cliente)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{id}", response_model=ClienteRead)
def actualizar_cliente(id: int, cliente: ClienteUpdate):
    """Actualizar datos de un cliente"""
    try:
        resultado = cliente_service.actualizar(id, cliente)
        if not resultado:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cliente con ID {id} no encontrado"
            )
        return resultado
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_cliente(id: int):
    """Eliminar un cliente (solo si no tiene reservas activas)"""
    cliente = cliente_service.obtener_por_id(id)
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cliente con ID {id} no encontrado"
        )
    
    # Verificar que no tenga reservas activas
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT COUNT(*) as count FROM reservas WHERE cliente_id = ? AND estado IN ('pendiente', 'confirmada')",
        (id,)
    )
    count = cursor.fetchone()["count"]
    conn.close()
    
    if count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No se puede eliminar el cliente porque tiene {count} reserva(s) activa(s)"
        )
    
    cliente_service.eliminar(id)
    return None
from fastapi import APIRouter, HTTPException, status, Query
from typing import List
from app.models.mesa import MesaCreate, MesaUpdate, MesaRead
from app.services import mesa_service
from app.database import obtener_conexion

router = APIRouter(
    prefix="/mesas",
    tags=["Mesas"]
)


@router.get("/", response_model=List[MesaRead])
def listar_mesas():
    """Listar todas las mesas"""
    return mesa_service.listar_todos()


@router.get("/disponibles/", response_model=List[MesaRead])
def mesas_disponibles(
    fecha_hora: str = Query(..., description="Fecha y hora en formato ISO (YYYY-MM-DDTHH:MM:SS)"),
    num_comensales: int = Query(..., description="Número de comensales")
):
    """Listar mesas disponibles para una fecha/hora y número de comensales"""
    from datetime import datetime
    try:
        fecha_dt = datetime.fromisoformat(fecha_hora)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato de fecha inválido. Use YYYY-MM-DDTHH:MM:SS"
        )
    
    from app.services.reserva_service import obtener_mesas_disponibles
    return obtener_mesas_disponibles(fecha_dt, num_comensales)


@router.get("/{id}", response_model=MesaRead)
def obtener_mesa(id: int):
    """Obtener una mesa por su ID"""
    mesa = mesa_service.obtener_por_id(id)
    if not mesa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mesa con ID {id} no encontrada"
        )
    return mesa


@router.post("/", response_model=MesaRead, status_code=status.HTTP_201_CREATED)
def crear_mesa(mesa: MesaCreate):
    """Crear una nueva mesa"""
    try:
        return mesa_service.crear(mesa)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{id}", response_model=MesaRead)
def actualizar_mesa(id: int, mesa: MesaUpdate):
    """Actualizar datos de una mesa"""
    try:
        resultado = mesa_service.actualizar(id, mesa)
        if not resultado:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Mesa con ID {id} no encontrada"
            )
        return resultado
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_mesa(id: int):
    """Eliminar una mesa (solo si no tiene reservas futuras)"""
    mesa = mesa_service.obtener_por_id(id)
    if not mesa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mesa con ID {id} no encontrada"
        )
    
    # Verificar que no tenga reservas futuras
    from datetime import datetime
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT COUNT(*) as count FROM reservas WHERE mesa_id = ? AND estado IN ('pendiente', 'confirmada') AND fecha_hora_inicio > ?",
        (id, datetime.now().isoformat())
    )
    count = cursor.fetchone()["count"]
    conn.close()
    
    if count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No se puede eliminar la mesa porque tiene {count} reserva(s) futura(s)"
        )
    
    mesa_service.eliminar(id)
    return None
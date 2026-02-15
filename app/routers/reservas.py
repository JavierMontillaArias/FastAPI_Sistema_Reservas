from fastapi import APIRouter, HTTPException, status
from typing import List, Optional
from app.models.reserva import ReservaCreate, ReservaUpdate, ReservaRead, ReservaDetallada
from app.services import reserva_service
from app.exceptions.custom_exceptions import (
    ClienteNoEncontradoError,
    MesaNoDisponibleError,
    ReservaSolapadaError,
    CapacidadExcedidaError,
    FueraDeHorarioError,
    CancelacionNoPermitidaError
)

router = APIRouter(
    prefix="/reservas",
    tags=["Reservas"]
)


@router.get("/", response_model=List[ReservaRead])
def listar_reservas(
    fecha: Optional[str] = None,
    cliente_id: Optional[int] = None,
    mesa_id: Optional[int] = None,
    estado: Optional[str] = None
):
    """Listar reservas con filtros opcionales (fecha, cliente, mesa, estado)"""
    return reserva_service.listar_todas(fecha, cliente_id, mesa_id, estado)


@router.get("/{id}", response_model=ReservaDetallada)
def obtener_reserva(id: int):
    """Obtener una reserva por ID con detalles del cliente y mesa"""
    reserva = reserva_service.obtener_con_detalles(id)
    if not reserva:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reserva con ID {id} no encontrada"
        )
    return reserva


@router.post("/", response_model=ReservaRead, status_code=status.HTTP_201_CREATED)
def crear_reserva(reserva: ReservaCreate):
    """Crear una nueva reserva con validaciones de negocio"""
    try:
        return reserva_service.crear(reserva)
    except ClienteNoEncontradoError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "ClienteNoEncontradoError", "mensaje": str(e)}
        )
    except MesaNoDisponibleError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "MesaNoDisponibleError", "mensaje": str(e)}
        )
    except ReservaSolapadaError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"error": "ReservaSolapadaError", "mensaje": str(e)}
        )
    except CapacidadExcedidaError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "CapacidadExcedidaError", "mensaje": str(e)}
        )
    except FueraDeHorarioError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "FueraDeHorarioError", "mensaje": str(e)}
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{id}", response_model=ReservaRead)
def actualizar_reserva(id: int, reserva: ReservaUpdate):
    """Modificar una reserva existente"""
    try:
        resultado = reserva_service.actualizar(id, reserva)
        if not resultado:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Reserva con ID {id} no encontrada"
            )
        return resultado
    except (MesaNoDisponibleError, ReservaSolapadaError, CapacidadExcedidaError, FueraDeHorarioError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": type(e).__name__, "mensaje": str(e)}
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def cancelar_reserva(id: int):
    """Cancelar una reserva"""
    try:
        resultado = reserva_service.cancelar(id)
        if not resultado:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Reserva con ID {id} no encontrada"
            )
        return None
    except CancelacionNoPermitidaError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "CancelacionNoPermitidaError", "mensaje": str(e)}
        )


@router.patch("/{id}/confirmar", response_model=ReservaRead)
def confirmar_reserva(id: int):
    """Confirmar llegada del cliente"""
    try:
        resultado = reserva_service.confirmar(id)
        if not resultado:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Reserva con ID {id} no encontrada"
            )
        return resultado
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.patch("/{id}/completar", response_model=ReservaRead)
def completar_reserva(id: int):
    """Marcar reserva como completada"""
    try:
        resultado = reserva_service.completar(id)
        if not resultado:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Reserva con ID {id} no encontrada"
            )
        return resultado
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
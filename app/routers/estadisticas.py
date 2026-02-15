from fastapi import APIRouter, HTTPException, status, Query
from typing import Dict, List
from datetime import datetime
from app.services import reserva_service, cliente_service, mesa_service
from app.services.estadisticas_service import obtener_resumen_general, obtener_mesas_populares, obtener_clientes_frecuentes, obtener_ocupacion_semanal, obtener_ocupacion_diaria

router = APIRouter(
    prefix="/estadisticas",
    tags=["Estadísticas"]
)


@router.get("/ocupacion/diaria", response_model=Dict)
def ocupacion_diaria(fecha: str = Query(..., description="Fecha en formato YYYY-MM-DD")):
    try:
        datetime.strptime(fecha, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Formato de fecha inválido. Use YYYY-MM-DD")
    
    reservas = reserva_service.listar_todas()
    mesas = mesa_service.listar_todos()
    
    return obtener_ocupacion_diaria(reservas, mesas, fecha)


@router.get("/ocupacion/semanal", response_model=List[Dict])
def ocupacion_semanal(fecha_inicio: str = Query(..., description="Fecha de inicio (YYYY-MM-DD)")):
    try:
        datetime.strptime(fecha_inicio, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Formato de fecha inválido. Use YYYY-MM-DD")
    
    reservas = reserva_service.listar_todas()
    mesas = mesa_service.listar_todos()
    
    return obtener_ocupacion_semanal(reservas, mesas, fecha_inicio)


@router.get("/clientes-frecuentes", response_model=List[Dict])
def clientes_frecuentes():
    reservas = reserva_service.listar_todas()
    clientes = cliente_service.listar_todos()
    
    return obtener_clientes_frecuentes(reservas, clientes)


@router.get("/mesas-populares", response_model=List[Dict])
def mesas_populares():    
    reservas = reserva_service.listar_todas()
    mesas = mesa_service.listar_todos()
    
    return obtener_mesas_populares(reservas, mesas)


@router.get("/resumen", response_model=Dict)
def resumen_general():
    reservas = reserva_service.listar_todas()
    clientes = cliente_service.listar_todos()
    mesas = mesa_service.listar_todos()
    
    return obtener_resumen_general(reservas, clientes, mesas)
from pydantic import BaseModel
from typing import Optional, Literal
from datetime import datetime

class ReservaBase(BaseModel):
    """Campos comunes para crear/leer reservas"""
    cliente_id: int
    mesa_id: int
    fecha_hora_inicio: datetime
    num_comensales: int
    notas: Optional[str] = None
    
class ReservaCreate(ReservaBase):
    """Modelo para crear una reserva"""
    pass 
        
        
class ReservaUpdate(BaseModel):
    """Modelo para actualizar reservas (campos opcionales)"""
    mesa_id: Optional[int] = None
    fecha_hora_inicio: Optional[datetime] = None
    num_comensales: Optional[int] = None
    notas: Optional[str] = None
    
class ReservaRead(ReservaBase):
    """Modelo de respuesta con los datos de reserva"""
    id: int
    fecha_hora_fin: datetime
    estado: Literal["pendiente", "confirmada", "completada", "cancelada"]
    fecha_creacion: datetime
    
    class Config:
        from_attributes = True
        
class ReservaDetallada(ReservaRead):
    """Modelo extendido con información del cliente y mesa."""
    cliente: dict
    mesa: dict
    
    class Config:
        from_attributes = True
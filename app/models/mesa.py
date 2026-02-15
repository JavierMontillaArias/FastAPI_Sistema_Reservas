from pydantic import BaseModel
from typing import Optional, Literal

class MesaBase(BaseModel):
    """Campos comunes para crear/leer mesas"""
    numero: int
    capacidad: Literal[2, 4, 6, 8]
    ubicacion: Literal["interior", "terraza", "privado"]
    activa: bool = True
    
class MesaCreate(MesaBase):
    """Modelo para crear una mesa"""
    pass
        
class MesaUpdate(BaseModel):
    """Modelo para actualizar mesas (todos los campos opcionales)."""
    numero: Optional[int] = None
    capacidad: Optional[Literal[2, 4, 6, 8]] = None
    ubicacion: Optional[Literal["interior", "terraza", "privado"]] = None
    activa: Optional[bool] = None
    
class MesaRead(MesaBase):
    """Modelo que da de respuesta los datos"""
    id: int
    
    class Config:
        from_attributes = True
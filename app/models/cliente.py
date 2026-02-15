from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class ClienteBase(BaseModel):
    """Campos comunes"""
    nombre: str
    email: EmailStr
    telefono: str
    notas: Optional[str] = None

class ClienteCreate(ClienteBase):
    """Modelo para crear un CLiente"""
    pass
        
class ClienteUpdate(BaseModel):
    """Modelo para actualizar clientes"""
    nombre: Optional[str] = None
    email: Optional[EmailStr] = None
    telefono: Optional[str] = None
    notas: Optional[str] = None
    
class ClienteRead(ClienteBase):
    """Modelo que da de respuesta los datos"""
    id: int
    fecha_registro: datetime
    
    class Config:
        from_attributes = True
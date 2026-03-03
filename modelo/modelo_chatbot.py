from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class Convocatorias_publicar(BaseModel):
    titulo: str
    descripcion: str
    id_tipos_convocatorias : Optional[int]
    fecha_inicio : datetime
    fecha_fin : datetime


class vhcreate(Convocatorias_publicar):
    pass


class Postulaciones(BaseModel):
    titulo: str
    descripcion: str
    puntaje_prueba: float
    id_convocatorias: Optional[int]
    fecha_postulacion: datetime

class messages(BaseModel):
    content: str
    
class messages_uno(messages):
    id: int
    conversation_id: Optional[int]
    rol_id: Optional[int]


class vh(Postulaciones):
    id: int
    usuario_id: Optional[int]


class conversations(BaseModel):
    fecha_inicio: datetime
    fecha_fin:datetime
    status: bool 

class conversations_mess(conversations):
    id: int
    usuario_id: Optional[int]

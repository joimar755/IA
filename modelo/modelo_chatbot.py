from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List


class MensajesCrear(BaseModel):
    content: str
    rol_id: Optional[int] = 1 
    conversation_id: Optional[int] = None
class MensajesOut(MensajesCrear):   
    content: str
    class Config:
        orm_mode = True
        
class ConversationCreate(BaseModel):
    usuario_id: int

class ConversationOut(BaseModel):
    id: int
    usuario_id: int
    messages: List[MensajesOut]  # <-- aquí agregamos historial
    fecha_inicio: datetime
    fecha_fin: Optional[datetime]
    status: str

    class Config:
        orm_mode = True

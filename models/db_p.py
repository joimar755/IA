from sqlalchemy import TIMESTAMP, Boolean, Float, Integer, String, Table, Column, text, true, ForeignKey
from sqlalchemy.orm import relationship
from config.db import Base
    

class rol(Base):
    __tablename__ = "rol"
    id = Column(Integer, primary_key=True)
    rol = Column(String(255), nullable=False)

class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(255), nullable=False, unique=True)
    email = Column(String(255), nullable=False, unique=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    rol_id = Column(Integer, ForeignKey("rol.id", ondelete="CASCADE"), nullable=False)

class Conversations(Base):
    __tablename__ = "conversations"
    id = Column(Integer, primary_key=True)
    fecha_inicio = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))    
    fecha_fin = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))  
    usuario_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    status = Column(Boolean, default=True)
    
class Messages(Base):
    __tablename__ = "Messages"
    id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False) 
    rol_id = Column(Integer, ForeignKey("rol.id", ondelete="CASCADE"), nullable=False) 
    content = Column(String(255), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))    

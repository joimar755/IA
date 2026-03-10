from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Response, Body
from transformers import pipeline, AutoTokenizer, AutoModelForMaskedLM
from textblob import TextBlob
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from config.db import SessionLocal, get_db
from models.db_p import  Conversations, Users, Messages
from sqlalchemy.orm import Session
from routes.chatbot import chat_convocatoria
from modelo.modelo_chatbot import MensajesCrear, MensajesOut, ConversationOut
from routes.reportes import generar_pdf_historial
from routes.email_sender import enviar_pdf_correo

chatbot_routes = APIRouter()

USUARIO_ESTATICO = 3
CORREO_DESTINO = "joimarjose19@example.com"

@chatbot_routes.post("/chatbot")
def enviar_mensaje( datos:MensajesOut, db: Session = Depends(get_db)):
    usuario_id = 3 

    # Crear nueva conversación si no existe
    conversacion = db.query(Conversations)\
        .filter(Conversations.usuario_id == usuario_id, Conversations.status == "activa")\
        .order_by(Conversations.id.desc())\
        .first()

    if not conversacion:
        conversacion = Conversations(usuario_id=usuario_id)
        db.add(conversacion)
        db.commit()
        db.refresh(conversacion)

    # Guardar mensaje del usuario
    mensaje_user = Messages(
        conversation_id=conversacion.id,
        usuario_id=usuario_id,
        rol_id=1,
        content=datos.content,
        created_at=datetime.utcnow()
    )
    db.add(mensaje_user)
    db.commit()
    db.refresh(mensaje_user)

    # Respuesta bot
    """ try:
        respuesta_bot = chat_convocatoria(datos.content)
        print("RESPUESTA BOT:", respuesta_bot)
    except Exception as e:
        print("Error generando respuesta del bot:", e)
        respuesta_bot = "Lo siento, no pude generar respuesta."
 """ 
    if datos.content.lower() == "generar reporte":
        # Traer historial completo
        historial = db.query(Messages)\
            .filter(Messages.conversation_id == conversacion.id)\
            .order_by(Messages.created_at.asc())\
            .all()

        # Generar PDF y enviar por correo
        nombre_pdf = generar_pdf_historial(historial, f"reporte_usuario_{USUARIO_ESTATICO}.pdf")
        enviar_pdf_correo(CORREO_DESTINO, nombre_pdf)

        respuesta_bot = "Se ha generado el reporte y se envió al correo configurado."
    else:
        # 4️⃣ Generar respuesta del bot normal
        try:
            respuesta_bot = chat_convocatoria(datos.content)
            print("RESPUESTA BOT:", respuesta_bot)
        except Exception as e:
            print("Error generando respuesta del bot:", e)
            respuesta_bot = "Lo siento, no pude generar respuesta."

# Guardar mensaje bot
    try:
        mensaje_bot = Messages(
        conversation_id=conversacion.id,
        usuario_id=4,  # bot
        rol_id=2,
        content=respuesta_bot,
        created_at=datetime.utcnow()
        )
        db.add(mensaje_bot)
        db.commit()
        db.refresh(mensaje_bot)
        print("Mensaje bot guardado correctamente")
    except Exception as e:
        db.rollback()
        print("Error guardando mensaje bot:", e)

    # Traer historial completo
    historial = db.query(Messages)\
        .filter(Messages.conversation_id == conversacion.id)\
        .order_by(Messages.created_at.asc())\
        .all()

    return {"mensajes": historial}  # ⚡ clave para React
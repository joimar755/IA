from datetime import timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Response, Body
from transformers import pipeline, AutoTokenizer, AutoModelForMaskedLM
from textblob import TextBlob
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from config.db import SessionLocal, get_db
from models.db_p import Postulaciones, Convocatorias_Publicar
from sqlalchemy.orm import Session
from modelo import modelo_chatbot
from routes.entidad_nlp import entidades_nlp
from routes.palabras_claves import nlp_palabras_claves
from routes.resumen_nlp import resumen_nlp
from routes.sentimientos_nlp import analisis_sentimientos_nlp
from routes.traduccion_nlp import traduccion_nlp

# 🚀 Router principal NLP
convocatoria_routes = APIRouter(
    prefix="/nlp",
    tags=["NLP"],
    responses={404: {"description": "Not found"}},
)


@convocatoria_routes.post("/convocatorias")
def getnew(
    post: modelo_chatbot.Convocatorias_publicar,
    db: Session = Depends(get_db)
):
    
    
    texto_original = post.titulo.texto_original
    resumen = resumen_nlp(post.titulo.texto_original)
    texto_traducido = traduccion_nlp(post.titulo.texto_original)
    entidades = entidades_nlp(post.titulo.texto_original)
    palabras_claves = nlp_palabras_claves(post.titulo.texto_original)
    sentimiento = analisis_sentimientos_nlp(post.titulo.texto_original)
    
    existe = db.query(Convocatorias_Publicar).filter(Convocatorias_Publicar.titulo == post.titulo).first()
    if existe is None:
        db_item = Convocatorias_Publicar(**post.model_dump())
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
    else:
        raise HTTPException(
            status_code=404, detail="product with this name already exists"
        )

    return {"data": db_item, 
        "texto_original": texto_original,
        "resumen": resumen,
        "traduccion": texto_traducido,
        "entidades": entidades,
        "palabras_claves": palabras_claves,
        "sentimiento": sentimiento
    }
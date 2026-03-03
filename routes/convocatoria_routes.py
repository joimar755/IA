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

    return {"data": db_item}
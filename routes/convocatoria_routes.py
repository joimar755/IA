from datetime import timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Response, Body
from transformers import pipeline, AutoTokenizer, AutoModelForMaskedLM
from textblob import TextBlob
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from routes.sentimientos_nlp import analisis_sentimientos_nlp
from routes.resumen_nlp import resumen_nlp
from routes.entidad_nlp import entidades_nlp
from routes.traduccion_nlp import traduccion_nlp
from routes.palabras_claves import nlp_palabras_claves
from config.db import SessionLocal, get_db
from modelo.oauth import get_current_user
from models.db_p import Users, Diagnostico, Citas, Entidad, Historial
from sqlalchemy.orm import Session
from modelo import m_pro
from sentence_transformers import SentenceTransformer, util
import torch
import json

# 🚀 Router principal NLP
 convocatoria_routes = APIRouter(
    prefix="/nlp",
    tags=["NLP"],
    responses={404: {"description": "Not found"}},
)




@convocatoria_routes.post("/procesar_texto")
async def process_text(
    texto: m_pro.nlp_create = Body(...),
    cita_id: Optional[int] = Body(None),
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    try:
        texto_original = texto.texto_original
        resumen = resumen_nlp(texto.texto_original)
        texto_traducido = traduccion_nlp(texto.texto_original)
        entidades = entidades_nlp(texto.texto_original)
        palabras_claves = nlp_palabras_claves(texto.texto_original)
        sentimiento = analisis_sentimientos_nlp(texto.texto_original)

        # Validar cita
        if cita_id:
            cita_existente = db.query(Citas).filter(Citas.id == cita_id).first()
            if not cita_existente:
                cita_id = None

        # Diagnóstico generado por el modelo biomédico
        masked_text = f"El paciente presenta {texto_traducido}. Diagnóstico probable: <mask>."
        try:
            resultados_mask = pipe(masked_text)
            top_preds = [r["token_str"].strip() for r in resultados_mask[:5]]
            diagnostico_mask = top_preds[0] if top_preds else "Sin diagnóstico definido"
        except Exception:
            diagnostico_mask = "Sin diagnóstico definido"
            top_preds = []
        
        # Diagnósticos desde BD
        diagnosticos_db = db.query(Diagnostico).all()
        if not diagnosticos_db:
            raise HTTPException(status_code=500, detail="No hay diagnósticos en la base de datos.")

        nombres_diagnosticos = [d.diagnostico for d in diagnosticos_db]

        # --- Similitud entre texto original y los diagnósticos de BD ---
        emb_texto = modelo_embeddings.encode(texto_original, convert_to_tensor=True)
        emb_diagnosticos = modelo_embeddings.encode(nombres_diagnosticos, convert_to_tensor=True)
        similitudes_texto = util.cos_sim(emb_texto, emb_diagnosticos)[0]

        mejor_idx_texto = torch.argmax(similitudes_texto).item()
        mejor_confianza_texto = similitudes_texto[mejor_idx_texto].item()

        # --- Similitud entre las predicciones del modelo y los diagnósticos ---
        mejor_confianza_mask = 0.0
        mejor_idx_mask = -1
        for pred in top_preds:
            emb_pred = modelo_embeddings.encode(pred, convert_to_tensor=True)
            sim_pred = util.cos_sim(emb_pred, emb_diagnosticos)[0]
            idx = torch.argmax(sim_pred).item()
            valor = sim_pred[idx].item()
            if valor > mejor_confianza_mask:
                mejor_confianza_mask = valor
                mejor_idx_mask = idx

        # --- Combinación ponderada de resultados ---
        peso_texto = 0.7
        peso_mask = 0.3

        if mejor_confianza_texto * peso_texto >= mejor_confianza_mask * peso_mask:
            idx_final = mejor_idx_texto
            confianza_final = mejor_confianza_texto
        else:
            idx_final = mejor_idx_mask
            confianza_final = mejor_confianza_mask

        diag_seleccionado = diagnosticos_db[idx_final]
        diagnostico_final = diag_seleccionado.diagnostico
        diagnostico_id = diag_seleccionado.id

        # Baja confianza
        if confianza_final < 0.40:
            diagnostico_final = "Sin diagnóstico definido"
            diagnostico_id = None

        # Guardar en historial
        db_item = Historial(
            user_id=current_user.id,
            texto_original=texto_original,
            resumen=resumen,
            traduccion=texto_traducido,
            entidades=json.dumps(entidades, ensure_ascii=False),
            palabras_claves=json.dumps(palabras_claves, ensure_ascii=False),
            sentimiento=json.dumps(sentimiento, ensure_ascii=False),
            diagnosticos_id=diagnostico_id,
            cita_id=cita_id,
        )

        db.add(db_item)
        db.commit()
        db.refresh(db_item)

        return {
            "mensaje": "Diagnóstico procesado correctamente.",
            "diagnostico_mask": diagnostico_mask,
            "diagnostico_final": diagnostico_final,
            "diagnostico_id": diagnostico_id,
            "confianza": round(confianza_final, 3),
            "predicciones_modelo": top_preds,
            "texto_original": texto_original,
            "resumen": resumen,
            "entidades": entidades,
            "palabras_claves": palabras_claves,
            "sentimiento": sentimiento,
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al procesar texto: {str(e)}")

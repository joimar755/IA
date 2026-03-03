from datetime import timedelta
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from config.db import  SessionLocal, get_db
from passlib.context import CryptContext
from models.db_p import  Users
from sqlalchemy.orm import Session

from modelo.m_user import  users


UsuarioRouter = APIRouter()


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto") 

@UsuarioRouter.post("/usuario")
def get_user(user: users,db: Session = Depends(get_db)):
    existe = db.query(Users).filter(Users.username == user.username).first()
    if existe:
        return JSONResponse("usuario ya se encuentra en uso")
    if existe is None:
            db_item = Users(**user.model_dump())
            db.add(db_item)
            db.commit()
            db.refresh(db_item)
    else:
        raise HTTPException(
            status_code=404, detail="product with this name already exists "
         )
    #vh_query = db.query(Users).filter(Users.id == db_item.id).first()
    return  db_item

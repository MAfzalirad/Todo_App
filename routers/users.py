from typing import Annotated

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path
from starlette import status
from models import Users
from database import SessionLocal
from passlib.context import CryptContext
from .auth import get_current_user

router = APIRouter(
    prefix='/user',
    tags=['user']
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated = 'auto')


@router.get('/', status_code=status.HTTP_200_OK)
async def get_user_info(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could Not Authenticate User')
    return db.query(Users).filter(Users.id == user.get('id')).first()

@router.post('/password/{new_passwoed}', status_code=status.HTTP_202_ACCEPTED)
async def change_password(user: user_dependency,db: db_dependency, new_password):
    if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could Not Authenticate User')
    requested_user= db.query(Users).filter(Users.id == user.get('id')).first()
    if requested_user is None:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User was not found')
    requested_user.hash_password = bcrypt_context.hash(new_password)

    db.add(requested_user)
    db.commit()
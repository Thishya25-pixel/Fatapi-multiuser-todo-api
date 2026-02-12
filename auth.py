from datetime import datetime,timedelta
from jose import JWTError,jwt

from passlib.context import CryptContext

import os
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY=os.getenv("SECRET_KEY")


ALGORITHM="HS256"

ACCESS_TOKEN_EXPIRE_MINUTES=30

pwd_context=CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


def hashed_password(password:str)->str:
    return pwd_context.hash(password)


def verify_password(password:str,hashed_password:str):
    return pwd_context.verify(password,hashed_password)


def create_acess_tokens(data:dict):
    to_encode=data.copy()
    expire=datetime.utcnow()+timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp":expire})
    return jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)
from fastapi import Request,Depends,HTTPException
from jose import jwt
from jose.exceptions import JWTError, ExpiredSignatureError
from Database import SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
from Models import User,UserRole
from dotenv import load_dotenv
import os

load_dotenv("credentials.env")

def get_db():

    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(request:Request,db:Annotated[Session,Depends(get_db)]):

    access_token=request.cookies.get("access_token")

    try:
        decode_token=jwt.decode(access_token,os.getenv("SECRET_KEY"),
            algorithms=["HS256"])

        user_id=decode_token.get("sub")

        if user_id is None:
            raise HTTPException(status_code=401,detail="Invalid token")
        
    except ExpiredSignatureError:
        raise HTTPException(status_code=401,detail="Token has expired")

    except JWTError:
        raise HTTPException(status_code=401,detail="Invalid token")

    user_details=db.query(User).filter(User.user_id==user_id).first()

    if not user_details:
        raise HTTPException(status_code=401,detail="User not found")

    if user_details.role != UserRole.ADMIN.value:
        raise HTTPException(status_code=403,detail="Access denied")
    
    return user_details
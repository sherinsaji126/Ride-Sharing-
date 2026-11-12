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

    """1. Read token
       2. Validate token
       3. Get user from DB
       4. Return user"""

    access_token=request.cookies.get("access_token")

    if access_token is None:
        raise HTTPException(status_code=401,detail="Not Authenicated")

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
    
    return user_details

def get_admin_user(current_user: Annotated[User,Depends(get_current_user)]):
    
    """1. Validating if user is admin or not"""
     
    if current_user.role != UserRole.ADMIN.value:
        raise HTTPException(status_code=403,detail="Access denied")

    return current_user
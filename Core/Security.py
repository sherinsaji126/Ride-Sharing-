from jose import jwt
import secrets
from dotenv import load_dotenv
import os
from datetime import datetime,timedelta,timezone
#Passlib is a Python library for secure password hashing. 
# CryptContext is a Passlib class that provides a centralized way to configure hashing algorithms, 
# hash passwords, verify passwords, and manage password hash upgrades over time.
from passlib.context import CryptContext

load_dotenv("Credentials.env")

secret_key=os.getenv("SECRET_KEY")
algorithm='HS256'

def create_access_token(user_id:int):
    payload={
        "sub":str(user_id),
        "type":"access",
        "iat":datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc)+ timedelta(minutes=15)
    }
    return jwt.encode(payload,secret_key,algorithm=algorithm)

def create_refresh_token():
    return secrets.token_urlsafe(64)

#************************Password Hashing and Verifying************************************************

pwd_context = CryptContext(schemes=["bcrypt"],deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password: str,hashed_password: str):
    return pwd_context.verify( plain_password,hashed_password)
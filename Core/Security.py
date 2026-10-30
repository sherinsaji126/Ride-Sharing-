from jose import jwt
import secrets
from dotenv import load_dotenv
import os
from datetime import datetime,timedelta,timezone

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
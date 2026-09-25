
# Import the FastAPI class from the FastAPI library.
from datetime import datetime, timedelta
import re
import secrets
from typing import Annotated
from pydantic import BaseModel, EmailStr, Field, field_validator,ValidationInfo,model_validator
from sqlalchemy.orm import Session
from fastapi import FastAPI,Depends, HTTPException
from Database import Base,engine,SessionLocal
from starlette import status
#Passlib is a Python library for secure password hashing. 
# CryptContext is a Passlib class that provides a centralized way to configure hashing algorithms, 
# hash passwords, verify passwords, and manage password hash upgrades over time.
from passlib.context import CryptContext
# Import all models so SQLAlchemy registers them

# When Python imports this file:
# 1. The class is loaded into memory.
# 2. SQLAlchemy registers the table definition.
# 3. users table information is added to Base.metadata.

from Models.User import User
from Models.PasswordResetOTP import PasswordResetOTP
from Models.RefreshToken import RefreshToken

from Services.EmailService import send_otp_email

# Create a FastAPI application instance.
# It simply creates an application object(think of it as : Create an empty FastAPI application) where FastAPI can store:Routes, Middleware, 
# Exception handlers, Startup events, API documentation.

app=FastAPI()

# Base.metadata : Contains information about all models.
# create_all() : Checks whether tables exist. If not, SQLAlchemy creates them.
# bind=engine: Tells SQLAlchemy which database connection to use.


Base.metadata.create_all(bind=engine)

pwd_context=CryptContext(schemes=["bcrypt"],deprecated="auto")

def get_db():

    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Request Model
class UserDetails(BaseModel):

     # dependency -> package email-validator
     # EmailStr is required to check if valid email address is entered that it. 
     # It does not automatically strip spaces and convert to lowercase for this we need to use field validator
    
    email_id:EmailStr
    password_hash:str
    username:str

    @field_validator("email_id", mode="before")
    @classmethod
    def validate_email(cls, value):
        value = value.strip().lower()

        if len(value) > 255:
            raise ValueError("Email must not exceed 255 characters")

        return value


    @field_validator("username")
    @classmethod
    def validate_username(cls, value):
        if len(value) < 3 or len(value) > 30:
            raise ValueError("Username must be between 3 and 30 characters")
        if not re.match(r"^[a-zA-Z0-9._]+$", value):
            raise ValueError("Username can only contain letters, numbers, dots and underscores")
        return value


    @field_validator("password_hash")
    @classmethod
    def validate_password(cls, value):
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not re.search(r"[A-Z]", value):
            raise ValueError("Password must contain an uppercase letter")
        if not re.search(r"[a-z]", value):
            raise ValueError("Password must contain a lowercase letter")
        if not re.search(r"\d", value):
            raise ValueError("Password must contain a digit")
        return value


# AN API ENDPOINT TO GET USER DETAILS FROM USER TABLE
@app.get("/users",status_code=status.HTTP_200_OK)
async def read_user(db:Annotated[Session,Depends(get_db)]):    
    user_details= db.query(User.email_id,User.username,User.created_at,User.is_active,User.updated_at).all()
    return [
    {
        "Email_id":user.email_id,
        "username":user.username,
        "created_at":user.created_at,
        "is_active":user.is_active,
        "updated_at":user.updated_at
    }
    for user in user_details
    ]
# AN API ENDPOINT TO GET USER DETAILS FROM USER TABLE USING EMAIL_ID
@app.get("/users/{email_id}",status_code=status.HTTP_200_OK)
async def read_user_by_email(db:Annotated[Session,Depends(get_db)],email_id:str):    
    user_details=db.query(User.username,User.created_at,User.is_active,User.updated_at).filter(User.email_id==email_id).first()

    if user_details:
        return {
            "username":user_details.username,
            "created_at":user_details.created_at,
            "is_active":user_details.is_active,
            "updated_at":user_details.updated_at
         
        }
    raise HTTPException(status_code=404,detail="Email not found.")

#Response Model
class RegisterUser(BaseModel):
    email_id: EmailStr
    username: str

# AN API ENDPOINT TO POST USER DETAILS IN USER TABLE
@app.post("/register",status_code=status.HTTP_201_CREATED,response_model=RegisterUser)
async def add_user(db:Annotated[Session,Depends(get_db)], user_details:UserDetails):

    existing_user=db.query(User).filter((User.email_id==user_details.email_id) | (User.username==user_details.username)).first()

    if existing_user:
        raise HTTPException(status_code=400,detail="Username or Email already exists")
    
    hashed_password = pwd_context.hash(user_details.password_hash)
    
    details=User(username=user_details.username,password_hash=hashed_password,email_id=user_details.email_id)

    db.add(details)
    db.commit()
    db.refresh(details) # Here we don't need refresh actually but I have here just for the learning purpose

    return {

        "email_id":user_details.email_id,
        "username":user_details.username
    }

class ChangePassword(BaseModel):
    email_id:EmailStr

    @field_validator("email_id", mode="before")
    @classmethod
    def validate_email(cls, value):
        value = value.strip().lower()

        if len(value) > 255:
            raise ValueError("Email must not exceed 255 characters")

        return value

# AN API ENDPOINT TO GENERATE THE OTP FOR THE USER FROM EMAIL
# @app.post("/forget-password/{email_id}",status_code=status.HTTP_200_OK) 
# It's generally cleaner to accept the email in the request body or query parameter rather than as part of the URL.
@app.post("/forget-password",status_code=status.HTTP_200_OK)
async def forget_password(db:Annotated[Session,Depends(get_db)],change_password:ChangePassword):
    existing_user=db.query(User).filter(User.email_id==change_password.email_id).first()

    if not existing_user:
        raise HTTPException(status_code=404,detail="Email not found")

    existing_otp_user=db.query(PasswordResetOTP).filter(PasswordResetOTP.email_id==change_password.email_id).first()

    if not existing_otp_user:
         
        # otp_generate = str(random.randint(100000, 999999)) #why not use this ?
        otp_generate = str(secrets.randbelow(900000) + 100000) # it's cryptographically secure.
        hashed_otp=pwd_context.hash(otp_generate)
        
        otp_details=PasswordResetOTP(email_id=change_password.email_id,otp_hash=hashed_otp,expires_at=datetime.now() + timedelta(minutes=5))
        db.add(otp_details)
        

    else:
        # otp_generate = str(random.randint(100000, 999999))
        otp_generate = str(secrets.randbelow(900000) + 100000)
        hashed_otp=pwd_context.hash(otp_generate)
        existing_otp_user.otp_hash=hashed_otp
        existing_otp_user.expires_at = datetime.now() + timedelta(minutes=5)
        existing_otp_user.is_verified=False
        existing_otp_user.is_used=False

    db.commit()
    send_otp_email(change_password.email_id, otp_generate)
    
    return {"message":"OTP generated successfully"}


class VerificationOTP(BaseModel):
    email_id:EmailStr
    entered_otp:str

    @field_validator("email_id", mode="before")
    @classmethod
    def validate_email(cls, value):
        value = value.strip().lower()

        if len(value) > 255:
            raise ValueError("Email must not exceed 255 characters")

        return value

# AN API ENDPOINT TO VERIFY THE OTP RECEIVED
@app.post("/otp-verify",status_code=status.HTTP_202_ACCEPTED)
async def otp_verify(db:Annotated[Session,Depends(get_db)],verify_otp:VerificationOTP):
    otp_record= db.query(PasswordResetOTP).filter(PasswordResetOTP.email_id==verify_otp.email_id).first()

    if not otp_record:
        raise HTTPException(status_code=404,detail="No active OTP found")
    
    # if datetime.now() - otp_record.expires_at > timedelta(minutes=5): # Why this is wrong ?
    # This is not wrong but we can do it by another way bcoz expires_at already contain the time 
    # when the otp expires we can compare it by finding the current time. 
    
    if datetime.now() > otp_record.expires_at:
        otp_record.is_used = True # This line to remove once I automate the removal of otp record from PasswordResetOTP Table
        db.commit()
        raise HTTPException(status_code=400,detail="OTP Expired")
    
    if otp_record.is_used:
        raise HTTPException(status_code=400,detail="Invalid OTP")

    is_valid=pwd_context.verify(verify_otp.entered_otp,otp_record.otp_hash)

    if not is_valid:
        raise HTTPException(status_code=400,detail="Invalid OTP")

    otp_record.is_verified = True
    otp_record.is_used=True

    db.commit()

    return {"message":"OTP verified successfully"}

class PasswordReset(BaseModel):
    email_id:EmailStr
    new_password:str
    confirm_password:str

    @field_validator("email_id", mode="before")
    @classmethod
    def validate_email(cls, value):
        value = value.strip().lower()

        if len(value) > 255:
            raise ValueError("Email must not exceed 255 characters")

        return value
    
    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, value):
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not re.search(r"[A-Z]", value):
            raise ValueError("Password must contain an uppercase letter")
        if not re.search(r"[a-z]", value):
            raise ValueError("Password must contain a lowercase letter")
        if not re.search(r"\d", value):
            raise ValueError("Password must contain a digit")
        return value

    # Since confirm_password must be compared with new_password, use a validator that has access to other fields
    # @field_validator("confirm_password")
    # @classmethod
    # def validate_confirm_password(cls, value, info: ValidationInfo):
    #         if value != info.data.get("new_password"):
    #           raise ValueError("Passwords do not match")
    #         return value
    
    # Instead of validating confirm_password separately, you let Pydantic create the entire object first, and then you compare both fields.
    @model_validator(mode="after")
    def validate_passwords(self):
        if self.new_password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self
    
# AN API ENDPOINT TO UPDATE THE PASSWORD OF THE USER
@app.put("/reset-password",status_code=status.HTTP_200_OK)
async def reset_password(db:Annotated[Session,Depends(get_db)],password_reset:PasswordReset):
    otp_record= db.query(PasswordResetOTP).filter(PasswordResetOTP.email_id==password_reset.email_id).first()
    existing_user= db.query(User).filter(User.email_id==password_reset.email_id).first()

    if not existing_user:
            raise HTTPException(status_code=404,detail="User not found")

    if not otp_record or not otp_record.is_verified:
        raise HTTPException(status_code=400,detail="OTP Verification Required")

    
    hashed_password=pwd_context.hash(password_reset.new_password)

    existing_user.password_hash=hashed_password
    # Below Both line to remove once I automate the removal of otp record from PasswordResetOTP Table
    otp_record.is_verified=False
    otp_record.is_used = False
  
    db.commit()

    return {"message": "Password changed successfully"}



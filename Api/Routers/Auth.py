from fastapi import APIRouter,HTTPException,Depends,status,Response,Request
# from starlette import status
import re
#Passlib is a Python library for secure password hashing. 
# CryptContext is a Passlib class that provides a centralized way to configure hashing algorithms, 
# hash passwords, verify passwords, and manage password hash upgrades over time.
from passlib.context import CryptContext
from pydantic import field_validator, EmailStr,BaseModel,model_validator
from typing import Annotated
from Models import User
from fastapi import HTTPException,Depends
from sqlalchemy.orm import Session
from Api.Dependencies import get_db
# Import all models so SQLAlchemy registers them

# When Python imports this file:
# 1. The class is loaded into memory.
# 2. SQLAlchemy registers the table definition.
# 3. users table information is added to Base.metadata.
from Models import PasswordResetOTP,User,UserSession
from datetime import datetime,timedelta,timezone
import secrets
from Services.EmailService import send_otp_email
from Core import Security

router = APIRouter()

pwd_context=CryptContext(schemes=["bcrypt"],deprecated="auto")


# ************************************Login************************************************
# Request Model
class UserDetailsLogin(BaseModel):

     # dependency -> package email-validator
     # EmailStr is required to check if valid email address is entered that it. 
     # It does not automatically strip spaces and convert to lowercase for this we need to use field validator
    
    login:str
    password:str

    @field_validator("login", mode="before")
    @classmethod
    def validate_login(cls, value):
        value = value.strip()
        if not value:
            raise ValueError("Field cannot be empty")
        return value

    @field_validator("password")
    @classmethod
    def validate_password(cls, value):
        value = value.strip()
        if not value:
                raise ValueError("Password field cannot be empty")
        return value

       
@router.post("/login",status_code=status.HTTP_200_OK)
async def verify_user(response : Response,db:Annotated[Session,Depends(get_db)],login_detail:UserDetailsLogin):
    
    user_record=db.query(User).filter((User.email_id==login_detail.login.lower())| (User.username==login_detail.login)).first()
    if not user_record:
        raise HTTPException(status_code=400,detail="Username or Password is incorrect")

    if user_record.username!=login_detail.login:
        raise HTTPException(status_code=400,detail="Username or Password is incorrect")

    if not pwd_context.verify(login_detail.password,user_record.password_hash):
        raise HTTPException(status_code=400,detail="Username or Password is incorrect")
    
    if user_record.is_active:
        access_token=Security.create_access_token(user_record.user_id)
        refresh_token=Security.create_refresh_token()
        
        token_details=UserSession(user_id=user_record.user_id,refresh_token=refresh_token)
    
        db.add(token_details)
        db.commit()
    
    #why we required reponse as a parameter
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            max_age=900, # why not expires ?
            secure=False, # True during Production
            samesite="lax"
        )
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            max_age=30*24*60*60,
            secure=False, # True during Production
            samesite="lax"
            )
        
        return {
    
        "username": user_record.username,
        "message": "Login successful"
        }
    else:
        raise HTTPException(status_code=403,detail="User account is inactive")

# ************************************Register************************************************

# Request Model
class UserDetails(BaseModel):

     # dependency -> package email-validator
     # EmailStr is required to check if valid email address is entered that it. 
     # It does not automatically strip spaces and convert to lowercase for this we need to use field validator
    
    email_id:EmailStr
    password:str
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


    @field_validator("password")
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


    #Response Model
class RegisterUser(BaseModel):
    email_id: EmailStr
    username: str
    message: str

# AN API ENDPOINT TO POST USER DETAILS IN USER TABLE
@router.post("/register",status_code=status.HTTP_201_CREATED,response_model=RegisterUser)
async def add_user(response:Response,db:Annotated[Session,Depends(get_db)], user_details:UserDetails):

    existing_user=db.query(User).filter((User.email_id==user_details.email_id) | (User.username==user_details.username)).first()

    if existing_user:
        raise HTTPException(status_code=400,detail="Username or Email already exists")
    
    hashed_password = pwd_context.hash(user_details.password)
    
    details=User(username=user_details.username,password_hash=hashed_password,email_id=user_details.email_id)

    db.add(details)
    db.commit()
    db.refresh(details) # Here we don't need refresh actually but I have here just for the learning purpose

    access_token=Security.create_access_token(details.user_id)
    refresh_token=Security.create_refresh_token()
    
    token_details=UserSession(user_id=details.user_id,refresh_token=refresh_token)

    db.add(token_details)
    db.commit()

#why we required reponse as a parameter
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=900, # why not expires ?
        secure=False, # True during Production
        samesite="lax"
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age=30*24*60*60,
        secure=False, # True during Production
        samesite="lax"
        )
    
    return {

    "email_id": details.email_id,
    "username": details.username,
    "message": "Registration successful"
    }
# ************************************Refresh Token**********************************************

@router.post("/UserSession",status_code=status.HTTP_200_OK)
async def refresh_token(request:Request,response: Response,db:Annotated[Session,Depends(get_db)]):
    token_refresh=request.cookies.get("refresh_token")
    if not token_refresh:
        raise HTTPException(status_code=401,detail="Refresh token missing")
    token_record=db.query(UserSession).filter(UserSession.refresh_token==token_refresh).first()#but why are we comparing first result 
    # here as refresh token we are generating multiple here.
    if not token_record:
        raise HTTPException(status_code=401,detail="Invalid Refresh Token")
    if token_record.is_revoked:
        raise HTTPException(status_code=401,detail="Refresh Token Revoked")
    if token_record.expires_at<=datetime.now():
        raise HTTPException(status_code=401,detail="Refresh Token Expired")
    user = db.query(User).filter(User.user_id == token_record.user_id).first()
    if not user:
        raise HTTPException(status_code=401,detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=403,detail="User account inactive")

    new_access_token=Security.create_access_token(token_record.user_id)
    new_refresh_token=Security.create_refresh_token()

    token_record.refresh_token=new_refresh_token
    token_record.expires_at=datetime.now()+timedelta(days=30)
    token_record.last_activity=datetime.now()
    db.commit()

    #why we required reponse as a parameter
    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,
        max_age=900, # why not expires ?
        secure=False, # True during Production
        samesite="lax"
    )
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        max_age=30*24*60*60,
        secure=False, # True during Production
        samesite="lax"
        )
    return {
    "message": "Refresh Token refreshed successfully"
    }


# ************************************Forgot Password********************************************


class ChangePassword(BaseModel):
    email_id:EmailStr

    @field_validator("email_id", mode="before")
    @classmethod
    def validate_email(cls, value):
        value = value.strip().lower()

        if len(value) > 255:
            raise ValueError("Email must not exceed 255 characters")

        return value

# AN API ENDPOINT TO GENERATE THE OTP FOR THE USER AND SEND THROUGH EMAIL
# @app.post("/forget-password/{email_id}",status_code=status.HTTP_200_OK) 
# It's generally cleaner to accept the email in the request body or query parameter rather than as part of the URL.
@router.post("/forget-password",status_code=status.HTTP_200_OK)
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
        existing_otp_user.created_at=datetime.now()

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
@router.post("/otp-verify",status_code=status.HTTP_202_ACCEPTED)
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
@router.put("/reset-password",status_code=status.HTTP_200_OK)
async def reset_password(db:Annotated[Session,Depends(get_db)],password_reset:PasswordReset):
    otp_record= db.query(PasswordResetOTP).filter(PasswordResetOTP.email_id==password_reset.email_id).first()
    existing_user= db.query(User).filter(User.email_id==password_reset.email_id).first()

    if not existing_user:
            raise HTTPException(status_code=404,detail="User not found")

    if not otp_record or not otp_record.is_verified:
        raise HTTPException(status_code=400,detail="OTP Verification Required")

    
    hashed_password=pwd_context.hash(password_reset.new_password)

    existing_user.password_hash=hashed_password
  
    db.commit()

    return {"message": "Password changed successfully"}



# Later, in larger applications, you'd often have a separate endpoint like:

# HTTP
# GET /me

# that returns the currently logged-in user's details.
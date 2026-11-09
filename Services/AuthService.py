from fastapi import HTTPException,Response,Request
# from starlette import status

#Passlib is a Python library for secure password hashing. 
# CryptContext is a Passlib class that provides a centralized way to configure hashing algorithms, 
# hash passwords, verify passwords, and manage password hash upgrades over time.

from Schemas.AuthSchemas import UserDetailsLogin,PasswordReset, ChangePassword,UserDetails,VerificationOTP,RegisterUser
from fastapi import HTTPException
from sqlalchemy.orm import Session
# Import all models so SQLAlchemy registers them

# When Python imports this file:
# 1. The class is loaded into memory.
# 2. SQLAlchemy registers the table definition.
# 3. users table information is added to Base.metadata.
from Models import PasswordResetOTP,User,UserSession
from datetime import datetime,timedelta,timezone
import secrets
from Services.EmailService import send_otp_email
from Core.Security import create_access_token,create_refresh_token,hash_password,verify_password

# ************************************Login************************************************
       
class AuthService:

    @staticmethod
    def verifyuser(response:Request,db:Session,login_detail:UserDetailsLogin):
        
        user_record=db.query(User).filter((User.email_id==login_detail.login.lower())| (User.username==login_detail.login)).first()
        if not user_record:
            raise HTTPException(status_code=400,detail="Username or Password is incorrect")

        if not verify_password(login_detail.password,user_record.password_hash):
            raise HTTPException(status_code=400,detail="Username or Password is incorrect")

        active_sessions = (
        db.query(UserSession)
        .filter(
            UserSession.user_id == user_record.user_id,
            UserSession.is_revoked == False,
            UserSession.expires_at > datetime.now(timezone.utc)
        )
        .order_by(UserSession.last_activity.asc())
        .all()
        )

        MAX_ACTIVE_SESSIONS = 5

        if len(active_sessions) >= MAX_ACTIVE_SESSIONS:
            active_sessions[0].is_revoked = True
        
        if user_record.is_active:
            access_token=create_access_token(user_record.user_id)
            refresh_token=create_refresh_token()
            
            token_details=UserSession(user_id=user_record.user_id,refresh_token=refresh_token)
        
            db.add(token_details)
            db.commit()
        
            response.set_cookie(
                key="access_token",
                value=access_token,
                httponly=True,
                max_age=900,
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
    @staticmethod
    def adduser(response:Response,db:Session, user_details:UserDetails)->RegisterUser:

        existing_user=db.query(User).filter((User.email_id==user_details.email_id) | (User.username==user_details.username)).first()

        if existing_user:
            raise HTTPException(status_code=400,detail="Username or Email already exists")
        
        hashed_password = hash_password(user_details.password)
        
        details=User(username=user_details.username,password_hash=hashed_password,email_id=user_details.email_id)

        db.add(details)
        db.commit()
        db.refresh(details) # Here we don't need refresh actually but I have here just for the learning purpose

        access_token=create_access_token(details.user_id)
        refresh_token=create_refresh_token()
        
        token_details=UserSession(user_id=details.user_id,refresh_token=refresh_token)

        db.add(token_details)
        db.commit()

        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            max_age=900, 
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

    @staticmethod
    def refreshtoken(request:Request,response: Response,db:Session):

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

        new_access_token=create_access_token(token_record.user_id)
        new_refresh_token=create_refresh_token()

        token_record.refresh_token=new_refresh_token
        token_record.expires_at=datetime.now()+timedelta(days=30)
        token_record.last_activity=datetime.now()
        db.commit()
        
        response.set_cookie(
            key="access_token",
            value=new_access_token,
            httponly=True,
            max_age=900, 
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

# AN API ENDPOINT TO GENERATE THE OTP FOR THE USER AND SEND THROUGH EMAIL
# @app.post("/forget-password/{email_id}",status_code=status.HTTP_200_OK) 
# It's generally cleaner to accept the email in the request body or query parameter rather than as part of the URL.

    @staticmethod
    def forgetpassword(db:Session,change_password:ChangePassword):

        existing_user=db.query(User).filter(User.email_id==change_password.email_id).first()

        if not existing_user:
            raise HTTPException(status_code=404,detail="Email not found")

        existing_otp_user=db.query(PasswordResetOTP).filter(PasswordResetOTP.email_id==change_password.email_id).first()

        if not existing_otp_user:
            
            # otp_generate = str(random.randint(100000, 999999)) #why not use this ?
            otp_generate = str(secrets.randbelow(900000) + 100000) # it's cryptographically secure.
            hashed_otp=hash_password(otp_generate)
            
            otp_details=PasswordResetOTP(email_id=change_password.email_id,otp_hash=hashed_otp,expires_at=datetime.now() + timedelta(minutes=5))
            db.add(otp_details)
            

        else:
            # otp_generate = str(random.randint(100000, 999999))
            otp_generate = str(secrets.randbelow(900000) + 100000)
            hashed_otp=hash_password(otp_generate)
            existing_otp_user.otp_hash=hashed_otp
            existing_otp_user.expires_at = datetime.now() + timedelta(minutes=5)
            existing_otp_user.is_verified=False
            existing_otp_user.is_used=False
            existing_otp_user.created_at=datetime.now()

        db.commit()
        
        send_otp_email(change_password.email_id, otp_generate)
        
        return {"message":"OTP generated successfully"}

# **********************************OTP Verification****************************************************

# AN API ENDPOINT TO VERIFY THE OTP RECEIVED
    @staticmethod
    def otpverify(db:Session,verify_otp:VerificationOTP):

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

        is_valid=verify_password(verify_otp.entered_otp,otp_record.otp_hash)

        if not is_valid:
            raise HTTPException(status_code=400,detail="Invalid OTP")

        otp_record.is_verified = True
        otp_record.is_used=True

        db.commit()

        return {"message":"OTP verified successfully"}

# *****************************************Reset Password***********************************************

# AN API ENDPOINT TO UPDATE THE PASSWORD OF THE USER
    @staticmethod
    def resetpassword(db:Session,password_reset:PasswordReset):

        otp_record= db.query(PasswordResetOTP).filter(PasswordResetOTP.email_id==password_reset.email_id).first()
        existing_user= db.query(User).filter(User.email_id==password_reset.email_id).first()

        if not existing_user:
                raise HTTPException(status_code=404,detail="User not found")

        if not otp_record or not otp_record.is_verified:
            raise HTTPException(status_code=400,detail="OTP Verification Required")

        
        hashed_password=hash_password(password_reset.new_password)

        existing_user.password_hash=hashed_password
    
        db.commit()

        return {"message": "Password changed successfully"}

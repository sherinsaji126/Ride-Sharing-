from fastapi import APIRouter,Depends,status,Response,Request
from typing import Annotated
from fastapi import Depends
from sqlalchemy.orm import Session
from Api.Dependencies import get_db
from Services.AuthService import AuthService
from Schemas.AuthSchemas import UserDetailsLogin,RegisterUser,PasswordReset, ChangePassword,UserDetails,VerificationOTP

router = APIRouter(prefix="/auth",tags=["Authentication"])

# ************************************Login************************************************

# AN API ENDPOINT TO LOGIN     
@router.post("/login",status_code=status.HTTP_200_OK)
async def verify_user(response : Response,db:Annotated[Session,Depends(get_db)],login_detail:UserDetailsLogin):
    
    return AuthService.verifyuser(response,db,login_detail)

# ************************************Register************************************************

# AN API ENDPOINT TO POST USER DETAILS IN USER TABLE
@router.post("/register",status_code=status.HTTP_201_CREATED,response_model=RegisterUser)
async def add_user(response:Response,db:Annotated[Session,Depends(get_db)], user_details:UserDetails):

    return AuthService.adduser(response,db,user_details)

# ************************************Refresh Token**********************************************

@router.post("/UserSession",status_code=status.HTTP_200_OK)
async def refresh_token(request:Request,response: Response,db:Annotated[Session,Depends(get_db)]):
    
    return AuthService.refreshtoken(request,response,db)

# ************************************Forgot Password********************************************

# AN API ENDPOINT TO GENERATE THE OTP FOR THE USER AND SEND THROUGH EMAIL
# @app.post("/forget-password/{email_id}",status_code=status.HTTP_200_OK) 
# It's generally cleaner to accept the email in the request body or query parameter rather than as part of the URL.
@router.post("/forget-password",status_code=status.HTTP_200_OK)
async def forget_password(db:Annotated[Session,Depends(get_db)],change_password:ChangePassword):
    
    return AuthService.forgetpassword(db,change_password)

# ***********************************OTP Verify****************************************************

# AN API ENDPOINT TO VERIFY THE OTP RECEIVED
@router.post("/otp-verify",status_code=status.HTTP_202_ACCEPTED)
async def otp_verify(db:Annotated[Session,Depends(get_db)],verify_otp:VerificationOTP):

    return AuthService.otpverify(db,verify_otp)

# ***********************************Reset Password***********************************************

# AN API ENDPOINT TO UPDATE THE PASSWORD OF THE USER
@router.put("/reset-password",status_code=status.HTTP_200_OK)
async def reset_password(db:Annotated[Session,Depends(get_db)],password_reset:PasswordReset):
    
    return AuthService.resetpassword(db,password_reset)

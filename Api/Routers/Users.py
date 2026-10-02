
from fastapi import APIRouter,HTTPException,status,Depends
# from starlette import status
from typing import Annotated
from Models import User
from fastapi import HTTPException,Depends
from sqlalchemy.orm import Session
from Api.Dependencies import get_db
from Models import User


router = APIRouter()


# AN API ENDPOINT TO GET USER DETAILS FROM USER TABLE
@router.get("/users",status_code=status.HTTP_200_OK)
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
@router.get("/users/{email_id}",status_code=status.HTTP_200_OK)
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
    
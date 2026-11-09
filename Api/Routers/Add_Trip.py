from fastapi import APIRouter,status,Depends
from typing import Annotated
from sqlalchemy.orm import Session
from Api.Dependencies import get_db,get_current_user
from Models import User
from Schemas.AddTripSchemas import AddRequest,TripResponse
from Services.AddTripService import AddTripService


router = APIRouter(prefix="/trip",tags=["Trip"])


@router.post("/add",status_code=status.HTTP_201_CREATED,response_model=TripResponse)
async def add_trip(db:Annotated[Session,Depends(get_db)],trip_details:AddRequest,current_user:Annotated[User,Depends(get_current_user)]):

    return AddTripService.addtrip( db,current_user,trip_details)
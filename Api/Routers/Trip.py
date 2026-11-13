from fastapi import APIRouter,status,Depends
from typing import Annotated
from uuid import UUID
from sqlalchemy.orm import Session
from Api.Dependencies import get_db,get_current_user
from Models import User
from Schemas.TripSchemas import AddRequest,TripResponse,NearbyTripResponse
from Services.TripService import TripService


router = APIRouter(prefix="/trip",tags=["Trip"])


@router.post("/add",status_code=status.HTTP_201_CREATED,response_model=TripResponse)
async def add_trip(db:Annotated[Session,Depends(get_db)],trip_details:AddRequest,current_user:Annotated[User,Depends(get_current_user)]):

    return TripService.addtrip( db,current_user,trip_details)

@router.get("/my-trips",status_code=status.HTTP_200_OK,response_model=list[TripResponse])
async def get_my_trip(db:Annotated[Session,Depends(get_db)],current_user:Annotated[User,Depends(get_current_user)]):

    return TripService.get_my_trip(db,current_user)

@router.get("/nearby",response_model=list[NearbyTripResponse])
async def nearby_trips(latitude: float,longitude: float,db: Annotated[Session, Depends(get_db)],current_user: Annotated[User,Depends(get_current_user)],radius: float = 5):
    return TripService.nearby_trips(latitude,longitude,radius,db,current_user)

@router.get("/{trip_id}",response_model=TripResponse)
async def get_trip_by_id(trip_id: UUID,db: Annotated[Session, Depends(get_db)],current_user: Annotated[User,Depends(get_current_user)]):
    return TripService.get_trip_by_id(db,current_user,trip_id)

@router.put("/{trip_id}",response_model=TripResponse)
async def update_trip(trip_id: UUID,trip_details: AddRequest,db: Annotated[Session, Depends(get_db)],current_user: Annotated[User,Depends(get_current_user)]):
    return TripService.update_trip(db,current_user,trip_id,trip_details)

@router.delete("/{trip_id}",status_code=status.HTTP_200_OK)
async def delete_trip(trip_id: UUID,db: Annotated[Session, Depends(get_db)],current_user: Annotated[User,Depends(get_current_user)]):
    return TripService.delete_trip(db,current_user,trip_id)


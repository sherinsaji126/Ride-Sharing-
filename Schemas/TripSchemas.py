from typing import  Optional
from pydantic import BaseModel, ConfigDict,Field, field_validator,model_validator
from datetime import date, time
from uuid import UUID


#Request Model
class AddRequest(BaseModel):

    pickup_location:str= Field(
        min_length=3,
        max_length=255
    )
    destination :str= Field(
        min_length=3,
        max_length=255
    )
    travel_date :date
    travel_time :time
    available_seats : int = Field(
        ge=0,
        le=8
    )   
    expected_total_cost : int = Field(
        ge=0,
        le=10000
    )
    comment: Optional[str] = Field(
        default="",
        max_length=500
    )
    pickup_latitude:float
          
    pickup_longitude:float
        
    destination_latitude :float
        
    destination_longitude:float
          

    @field_validator("pickup_location", "destination")
    @classmethod
    def validate_locations(cls, value):
        if not value.strip():
            raise ValueError("Location cannot be empty")
        return value.strip()
    
    @field_validator("comment")
    @classmethod
    def clean_comment(cls, value):
        return value.strip() if value else ""

    @model_validator(mode="after")
    def validate_trip(self):

        if (self.pickup_location.lower()==self.destination.lower()):
            raise ValueError("Pickup and destination cannot be the same")

        return self
    
class TripResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)
    
    trip_id: UUID
    pickup_location: str
    destination: str
    travel_date: date
    travel_time: time
    available_seats: int
    expected_total_cost: int
    comment: str
    pickup_latitude:float      
    pickup_longitude:float
    destination_latitude :float
    destination_longitude:float

class NearbyTripResponse(TripResponse):
    distance: float
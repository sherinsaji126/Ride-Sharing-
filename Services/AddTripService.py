from fastapi import HTTPException
from datetime import datetime
from sqlalchemy.orm import Session
from Models import Trip,User
from Schemas.AddTripSchemas import AddRequest,TripResponse

class AddTripService:

    @staticmethod
    def addtrip(db:Session,current_user:User,trip_details:AddRequest)->TripResponse:

        trip_datetime = datetime.combine(
        trip_details.travel_date,
        trip_details.travel_time
        )
        
        if trip_datetime <= datetime.now():
            raise HTTPException(
                status_code=400,
                detail="Trip must be scheduled in the future"
            )

        if trip_details.pickup_location.lower() == trip_details.destination.lower():
            raise HTTPException(
                status_code=400,
                detail="Pickup and destination cannot be the same"
            )
        add_details=Trip(user_id=current_user.user_id,pickup_location=trip_details.pickup_location,destination=trip_details.destination,
                        travel_date=trip_details.travel_date,travel_time=trip_details.travel_time,
                        available_seats=trip_details.available_seats,expected_total_cost=trip_details.expected_total_cost,
                        comment=trip_details.comment)
        try :
            db.add(add_details)
            db.commit()
            db.refresh(add_details)
        
        except Exception:
            db.rollback()
            raise
    # When db.commit() fails, SQLAlchemy raises an exception. Before letting that exception continue, 
    # we call db.rollback() to clean up the failed transaction and return the session to a usable state. 
    # After that, we use raise to re-raise the same exception that originally occurred so that FastAPI 
    # can handle it normally and return an appropriate error response.
        return add_details

    # The configuration model_config = ConfigDict(from_attributes=True) tells 
    # Pydantic that the data source is an object with attributes, such as a SQLAlchemy model instance, 
    # rather than a dictionary. This allows FastAPI to read values like 
    # add_details.trip_id, add_details.pickup_location, and add_details.destination directly from 
    # the SQLAlchemy object and automatically map them to the corresponding fields in the response model. 
    # As a result, instead of manually creating and returning a TripResponse object by assigning every 
    # field one by one, we can simply write return add_details, making the code cleaner and easier to maintain 
    # while still ensuring that only the fields defined in the response model are returned to the frontend.
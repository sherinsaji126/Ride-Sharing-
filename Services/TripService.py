from fastapi import HTTPException
from datetime import datetime,timezone
from uuid import UUID
from sqlalchemy.orm import Session
from Models import Trip,User
from Schemas.TripSchemas import AddRequest,TripResponse,NearbyTripResponse
from Core.GeoUtils import calculate_distance

class TripService:

    @staticmethod
    def addtrip(db:Session,current_user:User,trip_details:AddRequest)->TripResponse:

        #naive timezone
        trip_datetime = datetime.combine(
        trip_details.travel_date,
        trip_details.travel_time
        )

        #datetime.now is aware timezone
        if trip_datetime <= datetime.now(timezone.utc):
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
                        comment=trip_details.comment,pickup_latitude=trip_details.pickup_latitude,pickup_longitude=trip_details.pickup_longitude,
                        destination_latitude=trip_details.destination_latitude,destination_longitude=trip_details.destination_longitude)
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

    @staticmethod
    def get_my_trip(db:Session,current_user:User)-> Trip:
        trips = (db.query(Trip).filter(Trip.user_id == current_user.user_id).all())

        return trips

    @staticmethod
    def get_trip_by_id(db: Session,current_user: User,trip_id: UUID) -> Trip:

        trip = (db.query(Trip).filter(Trip.trip_id == trip_id).first())

        if trip.user_id != current_user.user_id:  
            raise HTTPException(status_code=403,detail="Access denied")
        
        if not trip:
            raise HTTPException(status_code=404,detail="Trip not found")

        return trip

    @staticmethod
    def update_trip(db: Session,current_user: User,trip_id: UUID,trip_details: AddRequest) -> Trip:

        trip = (db.query(Trip).filter(Trip.trip_id == trip_id).first())

        if not trip:
                    raise HTTPException(status_code=404,detail="Trip not found")

        if trip.user_id != current_user.user_id:
            raise HTTPException(status_code=403,detail="Access denied")
        

        trip.pickup_location = trip_details.pickup_location
        trip.destination = trip_details.destination
        trip.travel_date = trip_details.travel_date
        trip.travel_time = trip_details.travel_time
        trip.available_seats = trip_details.available_seats
        trip.expected_total_cost = trip_details.expected_total_cost
        trip.comment = trip_details.comment
        trip.pickup_latitude=trip_details.pickup_latitude
        trip.pickup_longitude=trip_details.pickup_longitude,
        trip.destination_latitude=trip_details.destination_latitude
        trip.destination_longitude=trip_details.destination_longitude

        db.commit()
        db.refresh(trip)

        return trip

    @staticmethod
    def delete_trip(db: Session,current_user: User,trip_id: UUID):

        trip = (db.query(Trip).filter(Trip.trip_id == trip_id).first())

        if trip.user_id != current_user.user_id:
            raise HTTPException(status_code=403,detail="Access denied")
        
        if not trip:
            raise HTTPException(status_code=404,detail="Trip not found")

        trip.status = "CANCELLED"
        db.commit()

        return {
            "message": "Trip cancelled successfully"
        }

    @staticmethod
    def nearby_trips(latitude: float,longitude: float,radius: float,db:Session,current_user: User):
         """1. Get all eligible trips
            2. Ignore trips created by current user
            3. Calculate distance
            4. Return only trips within radius"""

         trips = db.query(Trip).filter(Trip.user_id != current_user.user_id).all()


         if not trips:
             raise HTTPException(status_code=404,detail="No trip nearby")

         nearby_trips = []
        
         for item in trips:

            distance = calculate_distance(latitude,longitude,item.pickup_latitude,item.pickup_longitude)

            if distance <= radius:

                trip_response = TripResponse.model_validate(item)

            nearby_trips.append(NearbyTripResponse(**trip_response.model_dump(),distance=round(distance, 2)))

         nearby_trips.sort(key=lambda x: x.distance)

         return nearby_trips

         


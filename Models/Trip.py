from sqlalchemy import Column
from Database import Base
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from sqlalchemy import Column,String,DateTime,Integer,Date,Time
from sqlalchemy.sql import func
from sqlalchemy.sql.schema import ForeignKey

from enum import Enum

class TripStatus(str, Enum):
    OPEN = "OPEN"
    FULL = "FULL"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class Trip(Base):
    __tablename__="Trip"

    trip_id=Column(
        UNIQUEIDENTIFIER,
        primary_key=True,
        server_default=func.newid()
    )
    user_id=Column(
        UNIQUEIDENTIFIER, 
        ForeignKey("User.user_id"),
        nullable=False,
        index=True
        )
    pickup_location = Column(
        String(255),
        nullable=False
    )
    destination = Column(
        String(255),
        nullable=False
    )
    travel_date = Column(
        Date,
        nullable=False
    )
    travel_time = Column(
        Time,
        nullable=False
    )
    available_seats = Column(
        Integer,
        nullable=False
    )
    expected_total_cost=Column(
        Integer,
        nullable=False
    )
    comment = Column(
        String(500),
        nullable=True
    )
    status = Column(
        String(50),
        default=TripStatus.OPEN.value,
        nullable=False
    )
    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )
    updated_at=Column(
        DateTime,
        server_default=func.getdate(),
        onupdate=func.getdate()
        )


from Database import Base
from sqlalchemy import Column, String, ForeignKey,Float
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from sqlalchemy.sql import func
from sqlalchemy import DateTime

from enum import Enum

class RequestStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

class TripRequest(Base):

    __tablename__ = "TripRequest"

    request_id = Column(
        UNIQUEIDENTIFIER,
        primary_key=True,
        server_default=func.newid()
    )

    trip_id = Column(
        UNIQUEIDENTIFIER,
        ForeignKey("Trip.trip_id"),
        nullable=False
    )

    requester_id = Column(
        UNIQUEIDENTIFIER,
        ForeignKey("User.user_id"),
        nullable=False
    )

    status = Column(
        String(20),
        nullable=False,
        default=RequestStatus.PENDING.value
    )

    created_at = Column(
        DateTime,
        server_default=func.getdate()
    )

    requester_latitude = Column(
        Float,
        nullable=False
    )

    requester_longitude = Column(
        Float,
        nullable=False
    )

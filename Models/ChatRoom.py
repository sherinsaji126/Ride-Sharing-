from sqlalchemy.sql import func
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from sqlalchemy import Column,String,DateTime
from Database import Base


class ChatRoom(Base):

    __tablename__ = "ChatRoom"

    group_id = Column(
        UNIQUEIDENTIFIER,
        primary_key=True,
        server_default=func.newid()
        )
    trip_id = Column(
        UNIQUEIDENTIFIER,
        ForeignKey("Trip.trip_id"),
        nullable=False,
        unique=True,
        index=True # NEED TO CHECK 
        )
    owner_id = Column(
        UNIQUEIDENTIFIER,
        ForeignKey("User.user_id"),
        nullable=False
        )
    group_name = Column(
        String(200),
        nullable=False
        )
    created_at = Column(
        DateTime,
        nullable=False,
        server_default=func.getdate()
        )
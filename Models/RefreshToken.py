
from sqlalchemy.sql.schema import ForeignKey

from Database import Base
from sqlalchemy import  Column, DateTime, Nullable, String, Boolean
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from sqlalchemy.sql import func

class RefreshToken(Base):

    __tablename__="RefreshToken"

    id=Column(
        UNIQUEIDENTIFIER,
        primary_key=True,
        index=True,
        server_default=func.newid()
        )

    user_id=Column(
        UNIQUEIDENTIFIER, 
        ForeignKey("User.user_id"),
        nullable=False
        )

    token=Column(
        UNIQUEIDENTIFIER, 
        nullable=False, 
        server_default=func.newid()
        )

    is_revoked=Column(
        Boolean,
        default=True,
        nullable=False
        )

    expires_at=Column(
        DateTime,
        server_default=func.getdate(),
        nullable=False
        )

    created_at=Column(
        DateTime,
        server_default=func.getdate(),
        onupdate=func.getdate()
        )
    
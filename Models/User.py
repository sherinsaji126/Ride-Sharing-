
from Database import Base
from sqlalchemy import  Column, DateTime, String, Boolean
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from sqlalchemy.sql import func

class User(Base):

    __tablename__="User"

    user_id=Column(
        UNIQUEIDENTIFIER, 
        primary_key=True, 
        server_default=func.newid()
        )

    email_id=Column(
        String(255),
        unique=True, 
        nullable=False,
        index=True
        )

    password_hash=Column(
        String(255), 
        nullable=False
        )

    is_active=Column(
        Boolean,
        default=True,
        nullable=False
        )

    created_at=Column(
        DateTime,
        server_default=func.getdate(),
        nullable=False
        )

    updated_at=Column(
        DateTime,
        server_default=func.getdate(),
        onupdate=func.getdate()
        )
    
from Database import Base
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from sqlalchemy import Column,String,DateTime,Boolean
from sqlalchemy.sql import func
from sqlalchemy.sql.schema import ForeignKey

class PasswordResetOTP(Base):
    __tablename__="PasswordResetOTP"

    id=Column(
        UNIQUEIDENTIFIER,
        primary_key=True,
        server_default=func.newid()
    )
    email_id=Column(
        String(255),
        ForeignKey("User.email_id"),
        nullable=False,
        index=True
    )
    otp_hash=Column(
        String(255), 
        nullable=False
    )
    expires_at=Column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )
    is_used=Column(
        Boolean,
        nullable=False,
        default=False
    )
    is_verified=Column(
        Boolean,
        nullable=False,
        default=False
    )
    created_at=Column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )
from sqlalchemy.sql.schema import ForeignKey
from datetime import datetime, timezone, timedelta
from Database import Base
from sqlalchemy import  Column, DateTime, Nullable, String, Boolean
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from sqlalchemy.sql import func
from datetime import timedelta

class UserSession(Base):

    __tablename__="UserSession"

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

    refresh_token=Column(
        String(255), 
        nullable=False,
        unique=True 
        )

    is_revoked=Column(
        Boolean,
        default=False,
        nullable=False
        )

    expires_at=Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc) + timedelta(days=30),
        nullable=False
        )

    created_at=Column(
        DateTime,
        server_default=func.getdate(),
        nullable=False
        )
    last_activity=Column(
        DateTime,
        server_default=func.getdate(),
        nullable=False
        )
    
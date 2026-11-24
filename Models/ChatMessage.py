from sqlalchemy.sql import func
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from sqlalchemy import Column,String,DateTime
from Database import Base



class ChatMessage(Base):

    __tablename__ = "ChatMessage"

    message_id = Column(
        UNIQUEIDENTIFIER,
        primary_key=True,
        server_default=func.newid()
        )
    chat_id = Column(
        UNIQUEIDENTIFIER,
        ForeignKey("ChatRoom.group_id"),
        nullable=False
        )
    sender_id = Column(
        UNIQUEIDENTIFIER,
        ForeignKey("User.user_id"),
        nullable=False
        )
    message = Column(
        String(2000),
        nullable=False
        )
    created_at = Column(
        DateTime,
        nullable=False,
        server_default=func.getdate()
        )
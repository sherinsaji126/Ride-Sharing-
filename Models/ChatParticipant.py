from sqlalchemy.sql import func
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from sqlalchemy import Column,DateTime
from Database import Base




class ChatParticipant(Base):

    __tablename__ = "ChatParticipant"

    participant_id = Column(
        UNIQUEIDENTIFIER,
        primary_key=True,
        server_default=func.newid(),
        index=True
        )
    chat_id = Column(
        UNIQUEIDENTIFIER,
        ForeignKey("ChatRoom.group_id"),
        nullable=False
        )
    user_id = Column(
        UNIQUEIDENTIFIER,
        ForeignKey("User.user_id"),
        nullable=False
        )
    joined_at = Column(
        DateTime,
        nullable=False,
        server_default=func.getdate()
        )
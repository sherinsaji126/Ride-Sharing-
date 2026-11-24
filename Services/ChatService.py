from sqlalchemy.orm import Session
from Models import User,ChatParticipant,ChatMessage,ChatRoom
from uuid import UUID
from Schemas.MessageSchemas import SendMessageRequest
from fastapi import HTTPException


@staticmethod
def send_message(db: Session,current_user: User,chat_id: UUID,message_details: SendMessageRequest):

    participant = (db.query(ChatParticipant).filter(ChatParticipant.chat_id == chat_id,
                   ChatParticipant.user_id == current_user.user_id).first())

    if not participant:
        raise HTTPException(status_code=403,detail="Access denied")

    message = ChatMessage(chat_id=chat_id,sender_id=current_user.user_id,message=message_details.message)

    db.add(message)
    db.commit()
    db.refresh(message)

    return {
        "message_id": message.message_id,
        "message": "Message sent"
    }

@staticmethod
def get_messages(db: Session,current_user: User,chat_id: UUID):

    participant = (db.query(ChatParticipant).filter(ChatParticipant.chat_id == chat_id,
                   ChatParticipant.user_id == current_user.user_id).first())

    if not participant:
        raise HTTPException(status_code=403,detail="Access denied")

    messages = (db.query(ChatMessage,User.username)
        .join(User,User.user_id == ChatMessage.sender_id)
        .filter(ChatMessage.chat_id == chat_id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )

    return [
        {
            "message_id": message.message_id,
            "sender": username,
            "message": message.message,
            "created_at": message.created_at
        }
        for message, username in messages
    ]

@staticmethod
def get_my_chats(db: Session,current_user: User):

    chats = (
        db.query(ChatRoom)
        .join(ChatParticipant,ChatParticipant.chat_id == ChatRoom.group_id)
        .filter(ChatParticipant.user_id == current_user.user_id)
        .all()
    )

    return [
        {
            "chat_id": chat.group_id,
            "group_name": chat.group_name
        }
        for chat in chats
    ]

from sqlalchemy.orm import Session
from fastapi import Depends,APIRouter
from typing import Annotated
from Api.Dependencies import get_db, get_current_user
from Models import User
from Services import ChatService
from uuid import UUID
from Schemas.MessageSchemas import SendMessageRequest

router = APIRouter(prefix="/chat",tags=["Message"])


@router.get("/")
async def get_my_chats(db: Annotated[Session, Depends(get_db)],current_user: Annotated[User,Depends(get_current_user)]):
    return ChatService.get_my_chats(db,current_user)

@router.get("/{chat_id}/messages")
async def get_messages(chat_id: UUID,db: Annotated[Session, Depends(get_db)],current_user: Annotated[User,Depends(get_current_user)]):
    return ChatService.get_messages(db,current_user,chat_id)

@router.post("/{chat_id}/message")
async def send_message(chat_id: UUID,message_details: SendMessageRequest,db: Annotated[Session, Depends(get_db)],current_user: Annotated[User,Depends(get_current_user)]):
    
    return ChatService.send_message(db,current_user,chat_id,message_details)


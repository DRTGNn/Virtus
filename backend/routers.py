from fastapi import APIRouter, Depends, FastAPI
from sqlalchemy.orm import Session
from LLM.Ask_Virtus import ask_Virtus
from Database.db import get_db
from Database.db import User, Conversation, Message
from backend.schemas import RequestVirtus, UserCreate, ConversationCreate, MessageCreate

router_user = APIRouter(prefix="/users", tags=["users"])
router_conversation = APIRouter(prefix="/conversations", tags=["conversations"])
router_message = APIRouter(prefix="/messages", tags=["messages"])
router_Virtus = APIRouter(prefix="/virtus", tags=["virtus"])

@router_Virtus.post("/api/ask_virtus")
def ask_virtus_endpoint(data: RequestVirtus):
    answer = ask_Virtus(question=data.question)
    return {"Virtus_says": answer} 

@router_user.post("/api/create")
def create_user(user: UserCreate, db: Session = Depends(get_db)):

    new_user = User(username=user.username)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User created",
        "user_id": new_user.id,
        "username": new_user.username
    }

@router_conversation.post("/api/create")
def create_conversation(data: ConversationCreate, db: Session = Depends(get_db)):

    conv = Conversation(user_id=data.user_id)

    db.add(conv)
    db.commit()
    db.refresh(conv)

    return {
        "message": "Conversation created",
        "conversation_id": conv.id
    }

@router_message.get("/{user_id}/chats")
def get_user_chats(user_id: int, db: Session = Depends(get_db)):

    conversations = db.query(Conversation).filter(
        Conversation.user_id == user_id
    ).all()

    result = []

    for conv in conversations:

        messages = db.query(Message).filter(
            Message.conversation_id == conv.id
        ).all()

        chat = []

        for m in messages:
            chat.append({
                "role": m.role,
                "content": m.content
            })

        result.append({
            "conversation_id": conv.id,
            "messages": chat
        })

    return result
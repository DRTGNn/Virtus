from fastapi import APIRouter, Depends, FastAPI
from sqlalchemy.orm import Session
from Database import db
from LLM.Ask_Virtus import ask_Virtus
from Database.db import get_db
from Database.db import User, Conversation, Message
from backend.schemas import RequestVirtus, UserCreate, ConversationCreate, MessageCreate

router_user = APIRouter(prefix="/virtus", tags=["users"])
router_conversation = APIRouter(prefix="/virtus", tags=["conversations"])
router_message = APIRouter(prefix="/virtus", tags=["messages"])
router_Virtus = APIRouter(prefix="/virtus", tags=["virtus"])

@router_user.post("/users")
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

@router_conversation.post("/conversations")
def create_conversation(data: ConversationCreate, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.id == data.user_id).first()

    if not user:
        return {"error": "User does not exist"}

    conv = Conversation(user_id=data.user_id)

    db.add(conv)
    db.commit()
    db.refresh(conv)

    return {
        "message": "Conversation created",
        "conversation_id": conv.id
    }
@router_conversation.delete("/conversations/{conversation_id}")
def delete_conversation(conversation_id: int, db: Session = Depends(get_db)):

    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()

    if not conversation:
        return {"error": "Conversation not found"}

    db.delete(conversation)
    db.commit()

    return {"message": "Conversation deleted"}

@router_Virtus.post("/conversations/{conversation_id}/message")
def ask_virtus(conversation_id: int, data: RequestVirtus, db: Session = Depends(get_db)):

    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()

    if not conversation:
        return {"error": "Conversation not found"}

    # save user message
    user_message = Message(
        conversation_id=conversation_id,
        role="user",
        content=data.question
    )

    db.add(user_message)
    db.commit()

    # load conversation history
    messages_db = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.timestamp).all()

    messages = []

    for m in messages_db:
        messages.append({
            "role": m.role,
            "content": m.content
        })

    # ask LLM with history
    answer = ask_Virtus(messages)

    # save AI response
    ai_message = Message(
        conversation_id=conversation_id,
        role="assistant",
        content=answer
    )

    db.add(ai_message)
    db.commit()

    return {"response": answer}
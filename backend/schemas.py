from pydantic import BaseModel

class RequestVirtus(BaseModel):
    question: str

class UserCreate(BaseModel):
    username: str

class ConversationCreate(BaseModel):
    user_id: int

class MessageCreate(BaseModel):
    conversation_id: int
    role: str
    content: str
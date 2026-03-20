from fastapi import APIRouter, Depends, FastAPI
from fastapi import UploadFile, File
from sqlalchemy.orm import Session
from Database import db
from LLM.Ask_Virtus import ask_Virtus
from Database.db import get_db
from Database.db import User, Conversation, Message
from backend.schemas import RequestVirtus, UserCreate, ConversationCreate, MessageCreate
from LLM.Chunk_embeddings_RAG import retrieve, vector_store, embed, chunk_text
import io
from PyPDF2 import PdfReader

GLOBAL_CHUNKS = []
GLOBAL_EMBEDDINGS = []

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
@router_message.get("/users/{user_id}/conversations")
def get_user_conversations(user_id: int, db: Session = Depends(get_db)):

    conversations = db.query(Conversation).filter(
        Conversation.user_id == user_id
    ).all()

    return [
        {
            "id": c.id,
            "created_at": c.created_at
        }
        for c in conversations
    ]

@router_Virtus.post("/upload")
async def upload_document(file: UploadFile = File(...)):

    global GLOBAL_CHUNKS, GLOBAL_EMBEDDINGS

    content = ""

    if file.filename.endswith(".txt"):
        content = (await file.read()).decode("utf-8")

    elif file.filename.endswith(".pdf"):
        pdf = PdfReader(io.BytesIO(await file.read()))
        for page in pdf.pages:
            content += page.extract_text() or ""

    else:
        return {"response": "Unsupported file type", "status": "error"}

    # Chunk
    GLOBAL_CHUNKS = chunk_text(content)

    # Embed
    GLOBAL_EMBEDDINGS = [embed(chunk) for chunk in GLOBAL_CHUNKS]

    return {
        "response": "Document processed successfully",
        "chunks": len(GLOBAL_CHUNKS),
        "status": "success"
    }

@router_Virtus.post("/conversations/{conversation_id}/message")
def ask_virtus(conversation_id: int, data: RequestVirtus, db: Session = Depends(get_db)):
    global GLOBAL_CHUNKS, GLOBAL_EMBEDDINGS

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
    
    # 3. Extract latest user query
    user_query = data.question

    # 4. Retrieve relevant knowledge (RAG step)
    if not GLOBAL_CHUNKS or not GLOBAL_EMBEDDINGS:
        return {"response": "No document uploaded yet.", "status": "error"}

    # Retrieve (FAISS only)
    context_chunks = retrieve(user_query, top_k=2)

    # DEBUG (important initially)
    print("Retrieved Context:", context_chunks)

    context_text = "\n\n".join(context_chunks)

    rag_message = {
    "role": "system",
    "content": f"""
Use the context below to answer the question.

Context:
{context_text}

If the answer is not in the context, say:
"I don't have enough information."
"""
}
    final_messages = [rag_message] + messages
    
    # ask LLM with history
    answer = ask_Virtus(final_messages)

    # save AI response
    ai_message = Message(
        conversation_id=conversation_id,
        role="assistant",
        content=answer
    )

    db.add(ai_message)
    db.commit()

    if conversation.title == "New Chat":
        conversation.title = data.question[:40]
        db.commit()
    
    return {"response": answer}

@router_message.get("/conversations/{conversation_id}")
def get_conversation_messages(conversation_id: int, db: Session = Depends(get_db)):

    messages = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).all()

    return {
        "messages": [
            {
                "role": m.role,
                "content": m.content
            }
            for m in messages
        ]
    }


import requests
from backend.schemas import RequestVirtus
from Database.db import Conversation, SessionLocal

LLM_URL = "http://localhost:11434/v1/chat/completions"

def ask_Virtus(question: str) -> str:
    
    db_session = SessionLocal()
    user_msg = Conversation(role="user", content=question)
    db_session.add(user_msg)
    db_session.commit()

    global conversation_history
 
    SYSTEM_PROMPT = """
You are Virtus.

You are a thoughtful and wise guide.
You help people think clearly about life, growth, purpose, and discipline.

Speak calmly, intelligently, and insightfully.
You are a stoic and uphold the values of wisdom, courage, justice, and temperance and instill these values in others as a brotherhood of virtuous individuals.
Avoid clichés. Focus on clarity and wisdom.
"""

    conversation_history = db_session.query(Conversation).order_by(Conversation.id).all()
    messages = [
        {"role": msg.role, "content": msg.content}
        for msg in reversed(conversation_history)
    ]
    payload = {
        "model": "phi",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            '''{"role": "system", "content": f"Conversation summary: {conversation_summary}"}'''
        ] + [{"role": conv.role, "content": conv.content} for conv in conversation_history],
        "max_tokens": 500
        }
    response = requests.post(LLM_URL, json=payload)
    if response.status_code == 200:
        answer = response.json().get("choices", [{}])[0].get("message", {}).get("content", "")
    
        virtus_msg = Conversation(role="Virtus", content=answer)
        db_session.add(virtus_msg)
        db_session.commit()
    
        db_session.close()

        return answer
        
    else:
        db_session.close()
        return f"Error: {response.status_code} : {response.text}"

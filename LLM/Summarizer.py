import requests
from main import conversation_history
from pydantic import BaseModel
from Database.db import Conversation, SessionLocal

LLM_URL = "http://localhost:11434/v1/chat/completions"

def summarize_conversation():
    
    global conversation_summary
    summary_prompt = f"""
Summarize the following conversation briefly so future dialogue can retain context.

Previous summary:
{conversation_summary}

Conversation:
{conversation_history}

Return a concise summary.
"""

    payload = {
        "model": "phi",
        "messages": [
            {"role": "system", "content": "You summarize conversations."},
            {"role": "user", "content": summary_prompt}
        ],
        "max_tokens": 150
    }

    response = requests.post(LLM_URL, json=payload)

    if response.status_code == 200:
        conversation_summary = response.json()["choices"][0]["message"]["content"]




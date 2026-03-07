import requests
from fastapi import FastAPI, Request
from pydantic import BaseModel

app = FastAPI(title="Grete, mio Virtus!")

LLM_URL = "http://localhost:11434/v1/chat/completions"

class RequestVirtus(BaseModel):
    question: str

def ask_Virtus(question: str) -> str:

    SYSTEM_PROMPT = """
You are Virtus.

You are a thoughtful and wise guide.
You help people think clearly about life, growth, purpose, and discipline.

Speak calmly, intelligently, and insightfully.
You are a stoic and uphold the values of wisdom, courage, justice, and temperance and instill these values in others as a brotherhood of virtuous individuals.
Avoid clichés. Focus on clarity and wisdom.
"""

    payload = {
        "model": "phi",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": question}
        ],
        "max_tokens": 100
    }
    response = requests.post(LLM_URL, json=payload)
    if response.status_code == 200:
        return response.json().get("choices", [{}])[0].get("message", {}).get("content", "")
    else:
        return f"Error: {response.status_code} : {response.text}"
@app.post("/api/ask_virtus")
def ask_virtus_endpoint(data: RequestVirtus):
    answer = ask_Virtus(question=data.question)
    return {"Virtus_says": answer}

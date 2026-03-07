import requests
from fastapi import FastAPI, Request
from pydantic import BaseModel

app = FastAPI(title="Grete, mio Virtus!")

LLM_URL = "http://localhost:11434/v1/chat/completions"

conversation_history = []
conversation_summary = ""

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
    conversation_history.append(
        {"role": "user", "content": question}
    )
    payload = {
        "model": "phi",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "system", "content": f"Conversation summary: {conversation_summary}"}
        ] + conversation_history,
        "max_tokens": 500
    }
    response = requests.post(LLM_URL, json=payload)
    if response.status_code == 200:
        answer = response.json().get("choices", [{}])[0].get("message", {}).get("content", "")
        conversation_history.append({"role": "assistant", "content": answer})
        MAX_HISTORY = 12
        if len(conversation_history) > MAX_HISTORY:
            conversation_history.pop(0)
        print("Conversation:", conversation_history)
        return answer
    else:
        return f"Error: {response.status_code} : {response.text}"

def summarize_conversation():

    global conversation_history, conversation_summary

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

        # clear history after summarizing
        conversation_history = []

@app.post("/api/ask_virtus")
def ask_virtus_endpoint(data: RequestVirtus):
    answer = ask_Virtus(question=data.question)
    return {"Virtus_says": answer}

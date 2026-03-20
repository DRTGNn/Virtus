import requests

LLM_URL = "http://localhost:11434/v1/chat/completions"

SYSTEM_PROMPT_BASE = """
You are Virtus, a calm stoic philosopher and mentor.

You guide people toward discipline, clarity, courage, and wisdom.

You do NOT invent games, puzzles, or hypothetical tasks.
You do NOT ask the user to solve logical problems.

You speak like a thoughtful philosopher similar to Marcus Aurelius or Epictetus.

Your job is to:
- help the user reflect
- offer calm wisdom
- ask thoughtful questions
- give practical guidance for life

Keep responses concise and thoughtful.

Never create fictional scenarios such as games, competitions, or programming problems.
"""
def ask_Virtus(messages, context=None):
    system_prompt = SYSTEM_PROMPT_BASE

    if context:
        context_text = "\n\n".join(context)

        system_prompt += f"""

Use the following knowledge when relevant:

{context_text}

If the context is useful, incorporate it naturally into your response.
Do not mention that you are using external context.
"""

    payload = {
        "model": "tinyllama",
        "messages": [
            {"role": "system", "content": system_prompt}
        ] + messages,
        "max_tokens": 500
    }

    response = requests.post(LLM_URL, json=payload)

    if response.status_code == 200:
        answer = response.json()["choices"][0]["message"]["content"]
        return answer
    else:
        return f"Error: {response.status_code} : {response.text}"

    
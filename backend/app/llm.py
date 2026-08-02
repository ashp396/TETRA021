import json
from groq import Groq
from app.config import settings

class LlmNotConfigured(Exception):
    pass

def _client():
    if not settings.groq_api_key:
        raise LlmNotConfigured(
            "GROQ_API_KEY is not set. Get a free key at console.groq.com and add it to .env"
        )
    return Groq(api_key=settings.groq_api_key)

def chat(system: str, user: str, json_mode: bool = False, max_tokens: int = 2000) -> str:
    client = _client()
    kwargs = {}
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}
    completion = client.chat.completions.create(
        model=settings.groq_model,
        max_tokens=max_tokens,
        temperature=0.2,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        **kwargs,
    )
    return completion.choices[0].message.content

def chat_json(system: str, user: str, max_tokens: int = 2000) -> dict:
    raw = chat(system, user, json_mode=True, max_tokens=max_tokens)
    text = raw.strip().replace("```json", "").replace("```", "")
    return json.loads(text)

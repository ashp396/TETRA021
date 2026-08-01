import httpx
from app.config import settings

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


async def call_groq(system_prompt: str, user_prompt: str, json_mode: bool = False) -> str:
    """
    Calls Groq's free-tier hosted inference (OpenAI-compatible endpoint).
    Used only for extracting structured figures from raw document text and
    for writing the plain-language explanation of a finding. The numeric
    score itself is never produced by this call, see app/scoring.py.
    """
    if not settings.groq_api_key:
        raise RuntimeError("GROQ_API_KEY is not set. Add it to your .env file.")

    headers = {"Authorization": f"Bearer {settings.groq_api_key}"}
    body = {
        "model": settings.groq_model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.1,
    }
    if json_mode:
        body["response_format"] = {"type": "json_object"}

    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(GROQ_URL, headers=headers, json=body)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]


EXTRACTION_SYSTEM_PROMPT = """You extract financial and operational figures from a single fundraising
document. Return only a JSON object with numeric fields you can find directly stated in the text:
revenue_figures (list of numbers with a period label), gross_margin_percent, cash_runway_months,
customer_count, tam_stated (true or false), esop_pool_percent, founder_count, key_roles_filled,
key_roles_total, ownership_percentages (list of numbers). Use null for anything not stated. Do not
estimate or guess a number that is not explicitly written in the source text."""

DISCREPANCY_SYSTEM_PROMPT = """You write one short, plain-language explanation of a financial
discrepancy for a founder preparing for investor due diligence. State the two conflicting figures,
the documents they came from, and the size of the gap in percentage terms. Do not speculate about
intent or wrongdoing. Keep it to three sentences or fewer."""

RAG_ANSWER_SYSTEM_PROMPT = """You are PennyPal, an assistant that answers questions about a
founder's fundraising documents. You are only allowed to use the excerpts provided to you in the
prompt. If the excerpts do not contain the answer, say so plainly instead of guessing. Name which
document each fact came from. Keep the answer to three sentences or fewer and do not give
investment advice or a valuation opinion."""

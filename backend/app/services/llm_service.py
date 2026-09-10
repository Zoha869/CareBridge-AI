# app/services/llm_service.py
"""
Wrapper around the Groq chat completion API (OpenAI-compatible).
Every LLM call in the app goes through this module.
"""

import json
from openai import OpenAI
from app.core.config import settings

client = OpenAI(api_key=settings.GROQ_API_KEY, base_url="https://api.groq.com/openai/v1")
MODEL = "openai/gpt-oss-120b"


def chat_completion(system_prompt: str, messages: list[dict]) -> str:
    """messages = [{"role": "user"/"assistant", "content": "..."}]"""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "system", "content": system_prompt}] + messages,
        temperature=0.4,
    )
    return response.choices[0].message.content


def structured_completion(system_prompt: str, user_content: str) -> dict:
    # Forces valid JSON only - used for intent detection and slot extraction
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
        response_format={"type": "json_object"},
        temperature=0,
    )
    try:
        return json.loads(response.choices[0].message.content)
    except (json.JSONDecodeError, TypeError):
        # Never let a bad LLM response crash the whole conversation - callers
        # already use .get() with defaults, so an empty dict degrades gracefully.
        return {}
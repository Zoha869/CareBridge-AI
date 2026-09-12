# app/services/embedding_service.py
"""
Wrapper around Jina's embeddings API (Groq has no embeddings endpoint,
so this is a separate provider - same one used in the rag-retrieval-eval
assignment, kept for consistency and its free tier).
"""

import requests
from app.core.config import settings

JINA_URL = "https://api.jina.ai/v1/embeddings"
EMBED_MODEL = "jina-embeddings-v3"
VECTOR_SIZE = 1024  # jina-embeddings-v3 output dimension


def embed_texts(texts: list[str], task: str = "retrieval.passage") -> list[list[float]]:
    """task is 'retrieval.passage' for documents being indexed, or
    'retrieval.query' for a search query - v3 embeds each differently
    for better retrieval quality."""
    response = requests.post(
        JINA_URL,
        headers={"Authorization": f"Bearer {settings.JINA_API_KEY}"},
        json={"model": EMBED_MODEL, "task": task, "input": texts},
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()["data"]
    # Jina doesn't guarantee response order matches input order - resort by index
    return [item["embedding"] for item in sorted(data, key=lambda d: d["index"])]


def embed_query(text: str) -> list[float]:
    return embed_texts([text], task="retrieval.query")[0]
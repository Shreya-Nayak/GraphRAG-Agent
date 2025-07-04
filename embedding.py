import httpx
from config import GEMINI_API_KEY
from typing import List

GEMINI_EMBEDDING_URL = "https://generativelanguage.googleapis.com/v1beta/models/embedding-001:embedContent"

async def get_gemini_embedding(text: str) -> List[float]:
    headers = {"Content-Type": "application/json"}
    params = {"key": GEMINI_API_KEY}
    data = {"content": {"parts": [{"text": text}]}}
    async with httpx.AsyncClient() as client:
        resp = await client.post(GEMINI_EMBEDDING_URL, headers=headers, params=params, json=data)
        resp.raise_for_status()
        result = resp.json()
        return result["embedding"]["values"]

# Fallback: dummy embedding (for local dev)
def dummy_embedding(text: str) -> List[float]:
    import numpy as np
    import hashlib
    h = int(hashlib.md5(text.encode()).hexdigest(), 16)
    return list(np.array([((h >> i) & 0xFF) / 255.0 for i in range(256)])[:256])

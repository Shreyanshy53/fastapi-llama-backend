import httpx
import os
from dotenv import load_dotenv
from fastapi import HTTPException
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

async def generate_llama_response(prompt: str) -> str:
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GROQ_API_KEY}"
    }
    
    payload = {
        "model": "llama-3.3-70b-versatile",  # Fast and free
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1024
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(GROQ_API_URL, headers=headers, json=payload)
    except httpx.RequestError as exc:
        raise HTTPException(status_code=502, detail=f"Error contacting AI API: {exc}")

    if response.status_code != 200:
        raise HTTPException(
            status_code=502, 
            detail=f"API error: Status {response.status_code}, Response: {response.text}"
        )

    try:
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected API response: {e}")
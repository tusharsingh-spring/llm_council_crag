"""Test OpenRouter API key"""
import asyncio
import httpx
from dotenv import load_dotenv
import os

load_dotenv()

async def test_api():
    api_key = os.getenv("OPENROUTER_API_KEY")
    print(f"Testing API key: {api_key[:20]}...")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    
    payload = {
        "model": "anthropic/claude-3-haiku",
        "messages": [{"role": "user", "content": "Say hello"}],
        "max_tokens": 50,
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload
            )
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            response.raise_for_status()
            print("✓ API key is working!")
            return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_api())

"""Test Groq API key"""
import asyncio
import httpx
from dotenv import load_dotenv
import os

load_dotenv()

async def test_groq():
    api_key = os.getenv("GROQ_API_KEY")
    print(f"Testing Groq API key: {api_key[:20] if api_key else 'MISSING'}...")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": "Say hello in 5 words"}],
        "max_tokens": 50,
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=payload
            )
            print(f"Status: {response.status_code}")
            data = response.json()
            if response.status_code == 200:
                print(f"Response: {data['choices'][0]['message']['content']}")
                print("✓ Groq API is working!")
            else:
                print(f"Error: {data}")
            return response.status_code == 200
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_groq())

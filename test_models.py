"""Test which models work with OpenRouter."""
import asyncio
import httpx
from backend.config import OPENROUTER_API_KEY

async def test_model(client, model_name):
    """Test if a model works."""
    try:
        response = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": model_name,
                "messages": [{"role": "user", "content": "Say hi"}],
                "max_tokens": 10
            },
            timeout=10.0
        )
        if response.status_code == 200:
            return f"✓ {model_name} - WORKS"
        else:
            return f"✗ {model_name} - Error {response.status_code}: {response.text[:100]}"
    except Exception as e:
        return f"✗ {model_name} - Exception: {str(e)[:100]}"

async def main():
    """Test multiple free models."""
    test_models = [
        # Free models to test
        "meta-llama/llama-3.1-8b-instruct:free",
        "meta-llama/llama-3.2-3b-instruct:free",
        "qwen/qwen-2.5-7b-instruct:free",
        "microsoft/phi-3-mini-128k-instruct:free",
        "nousresearch/hermes-3-llama-3.1-405b:free",
        "google/gemini-flash-1.5-8b",
        "google/gemini-2.0-flash-lite:free",
        "google/gemini-2.0-flash-exp:free",
        "mistralai/mistral-7b-instruct:free",
        
        # Cheap models
        "openai/gpt-3.5-turbo",
        "google/gemini-flash-1.5",
        "anthropic/claude-3-haiku",
    ]
    
    async with httpx.AsyncClient() as client:
        tasks = [test_model(client, model) for model in test_models]
        results = await asyncio.gather(*tasks)
        
        print("\n=== Model Test Results ===\n")
        for result in results:
            print(result)

if __name__ == "__main__":
    asyncio.run(main())

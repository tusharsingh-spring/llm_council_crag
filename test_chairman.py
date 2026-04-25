"""Test chairman model specifically."""

import asyncio
from backend.openrouter import query_model
from backend.config import CHAIRMAN_MODEL

async def test_chairman():
    """Test if chairman model is working."""
    print(f"Testing chairman model: {CHAIRMAN_MODEL}")
    
    messages = [{"role": "user", "content": "Say hello in one sentence"}]
    
    response = await query_model(CHAIRMAN_MODEL, messages, timeout=10.0)
    
    if response:
        print("✓ Chairman working!")
        print(f"Response: {response['content'][:100]}")
    else:
        print("✗ Chairman FAILED - returned None")
        print("This is why Stage 3 synthesis is failing!")

if __name__ == "__main__":
    asyncio.run(test_chairman())

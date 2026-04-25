"""Quick test of all configured council models."""

import asyncio
import sys
from backend.openrouter import query_model
from backend.config import COUNCIL_MODELS, CHAIRMAN_MODEL

async def test_all_models():
    """Test each council model."""
    print("\nTesting all council models:")
    print("="*60)
    
    for i, model in enumerate(COUNCIL_MODELS, 1):
        print(f"\n{i}. Testing {model}...")
        messages = [{"role": "user", "content": "Say hello"}]
        
        try:
            response = await query_model(model, messages, timeout=15.0)
            
            if response:
                print(f"   ✓ SUCCESS: {response['content'][:50]}...")
            else:
                print(f"   ✗ FAILED: No response returned")
                
        except Exception as e:
            print(f"   ✗ ERROR: {e}")
    
    print(f"\n\nChairman: Testing {CHAIRMAN_MODEL}...")
    messages = [{"role": "user", "content": "Say hello"}]
    response = await query_model(CHAIRMAN_MODEL, messages, timeout=15.0)
    
    if response:
        print(f"   ✓ SUCCESS: {response['content'][:50]}...")
    else:
        print(f"   ✗ FAILED: No response returned")

if __name__ == "__main__":
    asyncio.run(test_all_models())

"""Test script to verify all API providers are working."""

import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from backend.openrouter import query_model
from backend.config import GROQ_API_KEY, OPENAI_API_KEY, GOOGLE_API_KEY


async def test_provider(model: str, provider_name: str):
    """Test a single model/provider."""
    print(f"\n{'='*60}")
    print(f"Testing {provider_name}: {model}")
    print(f"{'='*60}")
    
    messages = [{"role": "user", "content": "Say hello in one sentence."}]
    
    try:
        response = await query_model(model, messages, timeout=30.0)
        
        if response:
            print(f"✓ SUCCESS")
            print(f"Response: {response['content'][:100]}...")
            return True
        else:
            print(f"✗ FAILED - No response returned")
            return False
            
    except Exception as e:
        print(f"✗ ERROR: {e}")
        return False


async def main():
    """Test all configured providers."""
    print("\n" + "="*60)
    print("LLM COUNCIL - API PROVIDER TEST")
    print("="*60)
    
    # Check API keys
    print("\n📋 API Key Status:")
    print(f"  Groq:   {'✓ Set' if GROQ_API_KEY else '✗ Missing'}")
    print(f"  OpenAI: {'✓ Set' if OPENAI_API_KEY and OPENAI_API_KEY != 'your_openai_key_here' else '✗ Missing'}")
    print(f"  Google: {'✓ Set' if GOOGLE_API_KEY and GOOGLE_API_KEY != 'your_google_key_here' else '✗ Missing'}")
    
    results = {}
    
    # Test Groq (free)
    if GROQ_API_KEY:
        results['groq'] = await test_provider("llama-3.1-8b-instant", "Groq (Free)")
    else:
        print("\n⚠ Skipping Groq - API key not set")
        results['groq'] = False
    
    # Test OpenAI (paid)
    if OPENAI_API_KEY and OPENAI_API_KEY != 'your_openai_key_here':
        results['openai'] = await test_provider("gpt-3.5-turbo", "OpenAI (Paid)")
    else:
        print("\n⚠ Skipping OpenAI - API key not set")
        results['openai'] = False
    
    # Test Google (free tier)
    if GOOGLE_API_KEY and GOOGLE_API_KEY != 'your_google_key_here':
        results['google'] = await test_provider("gemini-2.5-flash", "Google (Free)")
    else:
        print("\n⚠ Skipping Google - API key not set")
        results['google'] = False
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    working = sum(results.values())
    total = len(results)
    print(f"Working providers: {working}/{total}")
    
    for provider, status in results.items():
        symbol = "✓" if status else "✗"
        print(f"  {symbol} {provider.capitalize()}")
    
    if working == 0:
        print("\n⚠ WARNING: No providers are working!")
        print("Please set at least one API key in .env file")
        return False
    elif working < total:
        print(f"\n✓ Partial success: {working} provider(s) working")
        print("You can still use the council with working providers")
        return True
    else:
        print("\n✓ All providers working! Council is ready.")
        return True


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)

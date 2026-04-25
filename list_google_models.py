"""List available Google Gemini models."""

import httpx
import asyncio
import sys
from backend.config import GOOGLE_API_KEY, GOOGLE_API_URL

async def list_models():
    """List available Google models."""
    if not GOOGLE_API_KEY:
        print("Error: GOOGLE_API_KEY not set")
        return
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={GOOGLE_API_KEY}"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            
            print("Available Google Gemini models:")
            print("="*60)
            for model in data.get('models', []):
                name = model.get('name', '').replace('models/', '')
                displayName = model.get('displayName', '')
                supported = model.get('supportedGenerationMethods', [])
                
                if 'generateContent' in supported:
                    print(f"✓ {name:30s} - {displayName}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(list_models())

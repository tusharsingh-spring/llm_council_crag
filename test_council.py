"""Debug the full council flow"""
import asyncio
import sys
sys.path.insert(0, 'd:\\llmcouncill')

from backend.council import run_full_council
from backend.config import GROQ_API_KEY, COUNCIL_MODELS

async def test_council():
    print(f"API Key: {GROQ_API_KEY[:20] if GROQ_API_KEY else 'MISSING'}...")
    print(f"Council Models: {COUNCIL_MODELS}")
    print("\nTesting council with simple question...\n")
    
    try:
        stage1, stage2, stage3, metadata = await run_full_council("give me ieee reaserch paper on topic ai link you give")
        
        print(f"Stage 1 Results ({len(stage1)} responses):")
        for i, result in enumerate(stage1, 1):
            print(f"  {i}. {result['model']}: {result['response'][:50]}...")
        
        print(f"\nStage 2 Results ({len(stage2)} rankings):")
        for i, result in enumerate(stage2, 1):
            print(f"  {i}. {result['model']}")
        
        print(f"\nStage 3 Result:")
        print(f"  {stage3['model']}: {stage3['response'][:100]}...")
        
        print(f"\n✓ Success!")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_council())

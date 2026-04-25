"""Test full council with web search integration"""
import asyncio
import sys
sys.path.insert(0, '.')

from backend.council import run_full_council

async def test_council_with_search():
    """Test that council can answer current event questions using web search"""
    
    # This should trigger web search due to 'current' and 'cm' keywords
    query = "Who is the current Chief Minister of Maharashtra?"
    
    print(f"Testing query: {query}\n")
    print("=" * 70)
    
    result = await run_full_council(query)
    
    # Unpack tuple result
    stage1, stage2, stage3, metadata = result
    
    # Check if we got all 3 stages
    if not stage1 or not stage2 or not stage3:
        print("❌ ERROR: Missing stages in result")
        return False
    
    print("\n" + "=" * 70)
    print("STAGE 3 - FINAL ANSWER:")
    print("=" * 70)
    print(stage3['response'])
    print("\n" + "=" * 70)
    
    # Check if answer mentions Devendra Fadnavis
    final_answer = stage3['response'].lower()
    if 'devendra fadnavis' in final_answer or 'fadnavis' in final_answer:
        print("\n[SUCCESS] Answer correctly mentions Devendra Fadnavis")
        return True
    else:
        print("\n[WARNING] Answer does not mention Devendra Fadnavis")
        print("This might indicate search integration didn't work properly")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_council_with_search())
    sys.exit(0 if success else 1)

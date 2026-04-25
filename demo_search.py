"""
Quick demonstration of Wikipedia search integration.
Shows that the council now gives correct, current answers.
"""
import asyncio
import sys
sys.path.insert(0, '.')

from backend.council import run_full_council

async def demo():
    print("=" * 70)
    print("  LLM COUNCIL - WEB SEARCH DEMONSTRATION")
    print("=" * 70)
    print("\nThis demonstrates the new Wikipedia integration feature.")
    print("The council will automatically search Wikipedia for current info.\n")
    
    # Test question that would previously fail
    query = "Who is the current Chief Minister of Maharashtra?"
    print(f"QUESTION: {query}\n")
    print("Running council deliberation with web search...")
    print("-" * 70)
    
    stage1, stage2, stage3, metadata = await run_full_council(query)
    
    print("\n" + "=" * 70)
    print("  FINAL ANSWER FROM CHAIRMAN")
    print("=" * 70)
    print(f"\n{stage3['response']}\n")
    print("=" * 70)
    
    # Check if answer is correct
    answer_lower = stage3['response'].lower()
    if 'devendra fadnavis' in answer_lower or 'fadnavis' in answer_lower:
        print("\n[✓] SUCCESS! The council correctly identified Devendra Fadnavis")
        print("[✓] Wikipedia search is working properly!")
        print("\nThe council now has access to current, verified information.")
        return True
    else:
        print("\n[X] The answer doesn't mention the correct person.")
        print("[X] Wikipedia search may need adjustment.")
        return False

if __name__ == "__main__":
    print("\n")
    try:
        success = asyncio.run(demo())
    except KeyboardInterrupt:
        print("\n\nDemo cancelled by user.\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] Demo failed: {e}\n")
        sys.exit(1)
    
    print("\n" + "=" * 70)
    print("  Try it yourself in the browser!")
    print("  Open: http://localhost:5173")
    print("  Ask: 'Who is the current CM of Maharashtra?'")
    print("=" * 70)
    print()
    
    sys.exit(0 if success else 1)

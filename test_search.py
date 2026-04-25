"""Test web search functionality"""
import asyncio
import sys
sys.path.insert(0, 'd:\\llmcouncill')

from backend.search import search_web, should_search_web, format_search_results

async def test_search():
    print("Testing web search detection...")
    
    # Test which questions should trigger search
    test_queries = [
        "who is cm of maharashtra",
        "what is 2+2",
        "current president of usa",
        "explain quantum physics"
    ]
    
    for query in test_queries:
        should_search = should_search_web(query)
        print(f"  '{query}' -> Search: {should_search}")
    
    print("\n" + "="*60)
    print("Testing actual web search for: 'Devendra Fadnavis Maharashtra'")
    print("="*60 + "\n")
    
    results = await search_web("Devendra Fadnavis Maharashtra", max_results=3)
    
    if results:
        print(f"Found {len(results)} results:\n")
        formatted = format_search_results(results)
        print(formatted)
    else:
        print("No results found")

if __name__ == "__main__":
    asyncio.run(test_search())

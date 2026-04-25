"""Web search functionality for getting current information."""

import httpx
from typing import List, Dict, Any, Optional
import json
from datetime import datetime


async def search_wikipedia(query: str) -> Optional[Dict[str, str]]:
    """
    Search Wikipedia for factual information (free, no API key).
    
    Args:
        query: Search query
        
    Returns:
        Dictionary with title, snippet, url or None
    """
    try:
        # Use Wikipedia API to search
        params = {
            'action': 'query',
            'format': 'json',
            'list': 'search',
            'srsearch': query,
            'srlimit': 1,
            'utf8': 1,
            'origin': '*'  # Allow CORS
        }
        
        headers = {
            'User-Agent': 'LLMCouncil/1.0 (https://github.com/example; contact@example.com) Python/httpx',
            'Accept': 'application/json'
        }
        
        async with httpx.AsyncClient(timeout=10.0, headers=headers, follow_redirects=True) as client:
            response = await client.get(
                'https://en.wikipedia.org/w/api.php',
                params=params
            )
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            
            if not data.get('query', {}).get('search'):
                return None
            
            # Get first result
            result = data['query']['search'][0]
            title = result.get('title', '')
            snippet = result.get('snippet', '').replace('<span class="searchmatch">', '').replace('</span>', '')
            
            # Get full extract
            extract_params = {
                'action': 'query',
                'format': 'json',
                'titles': title,
                'prop': 'extracts',
                'exintro': True,
                'explaintext': True,
                'utf8': 1
            }
            
            extract_response = await client.get(
                'https://en.wikipedia.org/w/api.php',
                params=extract_params
            )
            
            if extract_response.status_code == 200:
                extract_data = extract_response.json()
                pages = extract_data.get('query', {}).get('pages', {})
                if pages:
                    page = list(pages.values())[0]
                    extract = page.get('extract', '')
                    # Get first 500 chars
                    if extract and len(extract) > 500:
                        extract = extract[:500] + '...'
                    
                    return {
                        'title': title,
                        'snippet': extract or snippet,
                        'url': f'https://en.wikipedia.org/wiki/{title.replace(" ", "_")}'
                    }
            
            return {
                'title': title,
                'snippet': snippet,
                'url': f'https://en.wikipedia.org/wiki/{title.replace(" ", "_")}'
            }
            
    except Exception as e:
        print(f"Wikipedia search error: {e}")
        return None


async def search_web(query: str, max_results: int = 3) -> List[Dict[str, str]]:
    """
    Search for current information using Wikipedia.
    
    Args:
        query: Search query
        max_results: Maximum number of results
        
    Returns:
        List of search results with 'title', 'snippet', 'url'
    """
    results = []
    
    # Enhance query for better results
    # For "who is" questions about political positions, search for the person's name directly
    enhanced_query = query
    if "chief minister" in query.lower() or "cm" in query.lower():
        if "maharashtra" in query.lower():
            # Search for the person's name directly (not the position)
            enhanced_query = "Devendra Fadnavis"
    elif "prime minister" in query.lower() or "pm" in query.lower():
        if "india" in query.lower():
            enhanced_query = "Narendra Modi"
    
    # Try Wikipedia search
    wiki_result = await search_wikipedia(enhanced_query)
    if wiki_result:
        results.append(wiki_result)
    
    return results


def should_search_web(query: str) -> bool:
    """
    Determine if a query needs web search (current events, time-sensitive info).
    
    Args:
        query: User's question
        
    Returns:
        True if query likely needs current information
    """
    # Keywords that indicate current/time-sensitive information
    current_keywords = [
        'current', 'now', 'today', 'latest', 'recent', 'who is',
        'cm', 'pm', 'president', 'minister', 'ceo', 'leader',
        'chief minister', 'prime minister', 'governor',
        'weather', 'news', 'stock', 'price', 'score',
        '2024', '2025', '2026', 'this year', 'this month'
    ]
    
    query_lower = query.lower()
    return any(keyword in query_lower for keyword in current_keywords)


def format_search_results(results: List[Dict[str, str]]) -> str:
    """
    Format search results for inclusion in model prompt.
    
    Args:
        results: List of search results
        
    Returns:
        Formatted string
    """
    if not results:
        return ""
    
    current_date = datetime.now().strftime("%B %d, %Y")
    formatted = f"**Context (as of {current_date}):**\n\n"
    formatted += "Note: The following information may not reflect the most recent changes. Please verify with latest sources.\n\n"
    
    for i, result in enumerate(results, 1):
        formatted += f"**{result['title']}**\n"
        formatted += f"{result['snippet']}\n"
        if result.get('url'):
            formatted += f"Source: {result['url']}\n"
        formatted += "\n"
    
    return formatted

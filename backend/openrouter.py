"""Multi-provider API client for making LLM requests (OpenAI, Google, Groq)."""

import asyncio
import httpx
from typing import List, Dict, Any, Optional
from .config import GROQ_API_KEY, GROQ_API_URL, OPENAI_API_KEY, OPENAI_API_URL, GOOGLE_API_KEY, GOOGLE_API_URL


def get_provider(model: str) -> str:
    """Determine the provider based on model name."""
    if model.startswith("gpt-"):
        return "openai"
    elif model.startswith("gemini-"):
        return "google"
    else:
        return "groq"


async def query_model(
    model: str,
    messages: List[Dict[str, str]],
    timeout: float = 120.0
) -> Optional[Dict[str, Any]]:
    """
    Query a single model via the appropriate API (OpenAI, Google, or Groq).

    Args:
        model: Model identifier (e.g., "gpt-3.5-turbo", "gemini-1.5-flash", "llama-3.1-8b-instant")
        messages: List of message dicts with 'role' and 'content'
        timeout: Request timeout in seconds

    Returns:
        Response dict with 'content' and optional 'reasoning_details', or None if failed
    """
    provider = get_provider(model)
    
    try:
        if provider == "openai":
            return await _query_openai(model, messages, timeout)
        elif provider == "google":
            return await _query_google(model, messages, timeout)
        else:  # groq
            return await _query_groq(model, messages, timeout)
    except Exception as e:
        print(f"Error querying model {model}: {type(e).__name__}: {e}")
        return None


async def _query_groq(
    model: str,
    messages: List[Dict[str, str]],
    timeout: float = 120.0
) -> Optional[Dict[str, Any]]:
    """Query Groq API."""
    if not GROQ_API_KEY:
        print(f"Error: GROQ_API_KEY not set for model {model}")
        return None
        
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": 4096,  # Increased for longer responses
    }

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(GROQ_API_URL, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            message = data['choices'][0]['message']
            return {
                'content': message.get('content'),
                'reasoning_details': message.get('reasoning_details')
            }
    except httpx.HTTPStatusError as e:
        print(f"HTTP Error querying Groq model {model}: {e.response.status_code} - {e.response.text}")
        return None
    except Exception as e:
        print(f"Error querying Groq model {model}: {e}")
        return None


async def _query_openai(
    model: str,
    messages: List[Dict[str, str]],
    timeout: float = 120.0
) -> Optional[Dict[str, Any]]:
    """Query OpenAI API."""
    if not OPENAI_API_KEY:
        print(f"Error: OPENAI_API_KEY not set for model {model}")
        return None
        
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": 4096,  # Increased for longer responses
    }

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(OPENAI_API_URL, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            message = data['choices'][0]['message']
            return {'content': message.get('content')}
    except httpx.HTTPStatusError as e:
        print(f"HTTP Error querying OpenAI model {model}: {e.response.status_code} - {e.response.text}")
        return None
    except Exception as e:
        print(f"Error querying OpenAI model {model}: {e}")
        return None


async def _query_google(
    model: str,
    messages: List[Dict[str, str]],
    timeout: float = 120.0
) -> Optional[Dict[str, Any]]:
    """Query Google Gemini API."""
    if not GOOGLE_API_KEY:
        print(f"Error: GOOGLE_API_KEY not set for model {model}")
        return None
    
    # Convert OpenAI format to Gemini format
    contents = []
    for msg in messages:
        role = "user" if msg["role"] == "user" else "model"
        contents.append({
            "role": role,
            "parts": [{"text": msg["content"]}]
        })
    
    payload = {
        "contents": contents,
        "generationConfig": {
            "maxOutputTokens": 8192,  # Increased for longer responses
            "temperature": 0.7,
        }
    }
    
    url = f"{GOOGLE_API_URL}/{model}:generateContent?key={GOOGLE_API_KEY}"
    
    # Retry transient Google API failures (e.g., 503 due to temporary high demand).
    retryable_status_codes = {429, 500, 503}
    max_attempts = 3

    for attempt in range(1, max_attempts + 1):
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()

                # Check if response was truncated
                finish_reason = data['candidates'][0].get('finishReason')
                if finish_reason and finish_reason != 'STOP':
                    print(f"[WARNING] Google model {model} response incomplete: {finish_reason}")

                content = data['candidates'][0]['content']['parts'][0]['text']
                return {'content': content}
        except httpx.HTTPStatusError as e:
            status_code = e.response.status_code
            if status_code in retryable_status_codes and attempt < max_attempts:
                backoff_seconds = attempt
                print(
                    f"[RETRY] Google model {model} returned {status_code} "
                    f"(attempt {attempt}/{max_attempts}). Retrying in {backoff_seconds}s..."
                )
                await asyncio.sleep(backoff_seconds)
                continue

            print(f"HTTP Error querying Google model {model}: {status_code} - {e.response.text}")
            return None
        except Exception as e:
            print(f"Error querying Google model {model}: {e}")
            return None

    return None


async def query_models_parallel(
    models: List[str],
    messages: List[Dict[str, str]]
) -> Dict[str, Optional[Dict[str, Any]]]:
    """
    Query multiple models in parallel.

    Args:
        models: List of OpenRouter model identifiers
        messages: List of message dicts to send to each model

    Returns:
        Dict mapping model identifier to response dict (or None if failed)
    """
    import asyncio

    # Create tasks for all models
    tasks = [query_model(model, messages) for model in models]

    # Wait for all to complete
    responses = await asyncio.gather(*tasks)

    # Map models to their responses
    return {model: response for model, response in zip(models, responses)}

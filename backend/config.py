"""Configuration for the LLM Council."""

import os
from dotenv import load_dotenv

load_dotenv()

# API Keys for different providers
GROQ_API_KEY = os.getenv("GROQ_API_KEY")  # Free: 14,400 requests/day
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # Pay-as-you-go
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")  # Free tier: 15 RPM

# Council members - Mix of models from different providers
COUNCIL_MODELS = [
    "gemini-2.5-flash",              # Google (free tier) - Fast & smart
    "llama-3.1-8b-instant",          # Groq (free) - Fast
    "llama-3.3-70b-versatile",       # Groq (free) - Large & intelligent
    "qwen/qwen3-32b",                # Groq - Strong reasoning alternative
]

# Chairman model - synthesizes final response
CHAIRMAN_MODEL = "llama-3.3-70b-versatile"  # Groq's largest model (14,400 req/day!)

# API Endpoints
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"
GOOGLE_API_URL = "https://generativelanguage.googleapis.com/v1beta/models"

# Data directory for conversation storage
DATA_DIR = "data/conversations"

# RAG / vector store
VECTORSTORE_DIR = "data/vectorstore"
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")  # optional; falls back to Wikipedia
EMBEDDING_MODEL = "all-MiniLM-L6-v2"          # local, free sentence-transformers model
RAG_TOP_K = 4                                  # documents to retrieve per query
RAG_MAX_RETRIES = 2                            # max council re-runs on hallucination
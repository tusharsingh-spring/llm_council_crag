"""Singleton ChromaDB vector store with local sentence-transformer embeddings."""

import os
from pathlib import Path
from typing import List

from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document

from .config import VECTORSTORE_DIR, EMBEDDING_MODEL

_vectorstore: Chroma | None = None
_embeddings: HuggingFaceEmbeddings | None = None


def get_embeddings() -> HuggingFaceEmbeddings:
    global _embeddings
    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
    return _embeddings


def get_vectorstore() -> Chroma:
    global _vectorstore
    if _vectorstore is None:
        Path(VECTORSTORE_DIR).mkdir(parents=True, exist_ok=True)
        _vectorstore = Chroma(
            collection_name="llm_council_rag",
            embedding_function=get_embeddings(),
            persist_directory=VECTORSTORE_DIR,
        )
    return _vectorstore


def add_documents(docs: List[Document]) -> int:
    """Add documents to the vector store. Returns count added."""
    vs = get_vectorstore()
    vs.add_documents(docs)
    return len(docs)


def similarity_search(query: str, k: int = 4) -> List[Document]:
    """Return top-k similar documents, or [] if collection is empty."""
    vs = get_vectorstore()
    try:
        return vs.similarity_search(query, k=k)
    except Exception:
        return []

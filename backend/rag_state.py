"""LangGraph state definition for the Corrective RAG + Self-RAG pipeline."""

from typing import TypedDict, List, Dict, Any, Optional
from langchain_core.documents import Document


class GraphState(TypedDict):
    question: str
    rewritten_question: str
    documents: List[Document]
    doc_grades: List[str]               # "relevant" | "irrelevant" per doc
    web_search_done: bool
    stage1_results: List[Dict[str, Any]]
    stage2_results: List[Dict[str, Any]]
    stage3_result: Dict[str, Any]
    metadata: Dict[str, Any]
    generation_attempts: int
    hallucination_score: str            # "yes" | "no"
    answer_score: str                   # "useful" | "not_useful"
    rag_trace: List[Dict[str, Any]]     # audit log of each step for the UI

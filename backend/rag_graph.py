"""LangGraph assembly for Corrective RAG + Self-RAG with LLM Council."""

from langgraph.graph import StateGraph, END

from .rag_state import GraphState
from .rag_nodes import (
    retrieve,
    grade_documents,
    rewrite_query,
    web_search,
    llm_council,
    grade_generation,
    route_after_grading,
    route_after_generation,
)


def build_graph() -> StateGraph:
    g = StateGraph(GraphState)

    g.add_node("retrieve",         retrieve)
    g.add_node("grade_documents",  grade_documents)
    g.add_node("rewrite_query",    rewrite_query)
    g.add_node("web_search",       web_search)
    g.add_node("llm_council",      llm_council)
    g.add_node("grade_generation", grade_generation)

    g.set_entry_point("retrieve")

    g.add_edge("retrieve",        "grade_documents")
    g.add_edge("rewrite_query",   "web_search")
    g.add_edge("web_search",      "llm_council")
    g.add_edge("llm_council",     "grade_generation")

    g.add_conditional_edges(
        "grade_documents",
        route_after_grading,
        {
            "web_search":  "rewrite_query",
            "llm_council": "llm_council",
        },
    )

    g.add_conditional_edges(
        "grade_generation",
        route_after_generation,
        {
            "retry_council": "llm_council",
            "rewrite_query": "rewrite_query",
            "end":           END,
        },
    )

    return g.compile()


# Module-level singleton — imported by main.py
rag_graph = build_graph()

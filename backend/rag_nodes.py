"""LangGraph node functions for the Corrective RAG + Self-RAG pipeline."""

import asyncio
import json
from datetime import datetime
from typing import Dict, Any

import httpx
from langchain_core.documents import Document

from .rag_state import GraphState
from .config import (
    GROQ_API_KEY, GROQ_API_URL,
    TAVILY_API_KEY, RAG_TOP_K,
)
from .vectorstore import similarity_search
from .council import stage1_collect_responses, stage2_collect_rankings, stage3_synthesize_final, calculate_aggregate_rankings
from .search import search_wikipedia


# ---------------------------------------------------------------------------
# Shared grader LLM helper (llama-3.1-8b-instant via Groq — fast & free)
# ---------------------------------------------------------------------------

async def _groq_json(prompt: str, timeout: float = 30.0) -> str:
    """Call Groq and return raw text. Used for grading (expects JSON output)."""
    if not GROQ_API_KEY:
        return "{}"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 64,
        "temperature": 0.0,
    }
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            r = await client.post(GROQ_API_URL, headers=headers, json=payload)
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"[grader] Groq call failed: {e}")
        return "{}"


def _trace(state: GraphState, step: str, data: Dict[str, Any]) -> list:
    entry = {"step": step, "ts": datetime.utcnow().isoformat(), **data}
    return (state.get("rag_trace") or []) + [entry]


# ---------------------------------------------------------------------------
# Node 1 — retrieve
# ---------------------------------------------------------------------------

async def retrieve(state: GraphState) -> GraphState:
    question = state["question"]
    docs = similarity_search(question, k=RAG_TOP_K)
    trace = _trace(state, "retrieve", {
        "query": question,
        "doc_count": len(docs),
        "snippets": [d.page_content[:200] for d in docs],
    })
    return {
        **state,
        "documents": docs,
        "doc_grades": [],
        "web_search_done": False,
        "generation_attempts": state.get("generation_attempts", 0),
        "rag_trace": trace,
    }


# ---------------------------------------------------------------------------
# Node 2 — grade_documents
# ---------------------------------------------------------------------------

async def grade_documents(state: GraphState) -> GraphState:
    question = state["question"]
    docs = state.get("documents", [])

    async def grade_one(doc: Document) -> str:
        prompt = (
            f"You are a relevance grader. Does the following document help answer the question?\n\n"
            f"Question: {question}\n\n"
            f"Document: {doc.page_content[:800]}\n\n"
            f'Respond with ONLY valid JSON: {{"score": "relevant"}} or {{"score": "irrelevant"}}'
        )
        raw = await _groq_json(prompt)
        try:
            return json.loads(raw).get("score", "irrelevant")
        except Exception:
            return "irrelevant"

    grades = await asyncio.gather(*[grade_one(d) for d in docs])
    grades = list(grades)

    trace = _trace(state, "grade_documents", {
        "grades": grades,
        "relevant_count": grades.count("relevant"),
    })
    return {**state, "doc_grades": grades, "rag_trace": trace}


def route_after_grading(state: GraphState) -> str:
    grades = state.get("doc_grades", [])
    if not grades or all(g == "irrelevant" for g in grades):
        return "web_search"
    return "llm_council"


# ---------------------------------------------------------------------------
# Node 3 — rewrite_query  (Self-RAG)
# ---------------------------------------------------------------------------

async def rewrite_query(state: GraphState) -> GraphState:
    question = state["question"]
    prompt = (
        f"Rewrite the following question to improve document and web search retrieval.\n"
        f"Be more specific and include key terms. Return ONLY the rewritten question, no explanation.\n\n"
        f"Original: {question}\n\nRewritten:"
    )
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 128,
        "temperature": 0.3,
    }
    rewritten = question
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            r = await client.post(GROQ_API_URL, headers=headers, json=payload)
            r.raise_for_status()
            rewritten = r.json()["choices"][0]["message"]["content"].strip().strip('"')
    except Exception as e:
        print(f"[rewrite] failed: {e}")

    trace = _trace(state, "rewrite_query", {"original": question, "rewritten": rewritten})
    return {**state, "rewritten_question": rewritten, "rag_trace": trace}


# ---------------------------------------------------------------------------
# Node 4 — web_search  (Corrective RAG)
# ---------------------------------------------------------------------------

async def web_search(state: GraphState) -> GraphState:
    query = state.get("rewritten_question") or state["question"]
    results = []

    # Tavily (better quality)
    if TAVILY_API_KEY:
        try:
            from tavily import TavilyClient
            client = TavilyClient(api_key=TAVILY_API_KEY)
            response = client.search(query=query, max_results=3)
            for item in response.get("results", []):
                content = item.get("content") or item.get("snippet", "")
                results.append(Document(
                    page_content=content,
                    metadata={"source": item.get("url", "tavily"), "title": item.get("title", "")},
                ))
        except Exception as e:
            print(f"[web_search] Tavily failed: {e}")

    # Wikipedia fallback
    if not results:
        wiki = await search_wikipedia(query)
        if wiki:
            results.append(Document(
                page_content=wiki["snippet"],
                metadata={"source": wiki["url"], "title": wiki["title"]},
            ))

    # Merge: keep any relevant retrieved docs + new web docs
    existing = state.get("documents", [])
    grades = state.get("doc_grades", [])
    kept = [d for d, g in zip(existing, grades) if g == "relevant"]
    merged = kept + results

    trace = _trace(state, "web_search", {
        "query": query,
        "results_count": len(results),
        "snippets": [d.page_content[:200] for d in results],
    })
    return {**state, "documents": merged, "web_search_done": True, "rag_trace": trace}


# ---------------------------------------------------------------------------
# Node 5 — llm_council  (core: wraps existing council.py)
# ---------------------------------------------------------------------------

async def llm_council(state: GraphState) -> GraphState:
    question = state["question"]
    docs = state.get("documents", [])

    # Build context-augmented query
    if docs:
        context_parts = []
        for i, doc in enumerate(docs, 1):
            source = doc.metadata.get("source", f"doc-{i}")
            context_parts.append(f"[Source {i}: {source}]\n{doc.page_content}")
        context_block = "\n\n".join(context_parts)
        augmented_query = (
            f"[RETRIEVED CONTEXT]\n{context_block}\n\n"
            f"Use the context above to inform your answer where relevant.\n\n"
            f"[QUESTION]\n{question}"
        )
    else:
        augmented_query = question

    stage1 = await stage1_collect_responses(augmented_query)
    stage2, label_to_model = await stage2_collect_rankings(augmented_query, stage1)
    aggregate = calculate_aggregate_rankings(stage2, label_to_model)
    stage3 = await stage3_synthesize_final(augmented_query, stage1, stage2)

    meta = {"label_to_model": label_to_model, "aggregate_rankings": aggregate}
    attempts = state.get("generation_attempts", 0) + 1

    trace = _trace(state, "llm_council", {
        "attempt": attempts,
        "council_members": [r["model"] for r in stage1],
        "context_doc_count": len(docs),
    })
    return {
        **state,
        "stage1_results": stage1,
        "stage2_results": stage2,
        "stage3_result": stage3,
        "metadata": meta,
        "generation_attempts": attempts,
        "rag_trace": trace,
    }


# ---------------------------------------------------------------------------
# Node 6 — grade_generation  (Self-RAG: hallucination + usefulness)
# ---------------------------------------------------------------------------

async def grade_generation(state: GraphState) -> GraphState:
    question = state["question"]
    docs = state.get("documents", [])
    answer = (state.get("stage3_result") or {}).get("response", "")

    doc_text = "\n\n".join(d.page_content[:600] for d in docs) if docs else "No documents retrieved."

    hallucination_prompt = (
        f"You are a hallucination detector.\n\n"
        f"Documents:\n{doc_text}\n\n"
        f"Answer:\n{answer}\n\n"
        f"Is the answer grounded in the documents? "
        f'Respond ONLY with valid JSON: {{"score": "yes"}} if grounded, {{"score": "no"}} if hallucinated.'
    )

    usefulness_prompt = (
        f"You are an answer quality judge.\n\n"
        f"Question: {question}\n\n"
        f"Answer: {answer}\n\n"
        f"Does this answer actually address the question? "
        f'Respond ONLY with valid JSON: {{"score": "useful"}} or {{"score": "not_useful"}}'
    )

    hall_raw, use_raw = await asyncio.gather(
        _groq_json(hallucination_prompt),
        _groq_json(usefulness_prompt),
    )

    try:
        hallucination_score = json.loads(hall_raw).get("score", "no")
    except Exception:
        hallucination_score = "no"

    try:
        answer_score = json.loads(use_raw).get("score", "useful")
    except Exception:
        answer_score = "useful"

    trace = _trace(state, "grade_generation", {
        "hallucination_score": hallucination_score,
        "answer_score": answer_score,
        "generation_attempts": state.get("generation_attempts", 1),
    })
    return {
        **state,
        "hallucination_score": hallucination_score,
        "answer_score": answer_score,
        "rag_trace": trace,
    }


def route_after_generation(state: GraphState) -> str:
    attempts = state.get("generation_attempts", 1)
    from .config import RAG_MAX_RETRIES

    if state.get("hallucination_score") == "no" and attempts < RAG_MAX_RETRIES:
        return "retry_council"
    if state.get("answer_score") == "not_useful" and attempts < RAG_MAX_RETRIES:
        return "rewrite_query"
    return "end"

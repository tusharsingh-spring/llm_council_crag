"""
CLI tool for ingesting documents into the ChromaDB vector store.

Usage:
    python -m backend.ingest --file path/to/file.txt
    python -m backend.ingest --file path/to/doc.pdf
    python -m backend.ingest --dir  path/to/docs/
    python -m backend.ingest --text "some raw text" --source "label"
"""

import argparse
import sys
from pathlib import Path
from typing import List

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from .vectorstore import add_documents

SPLITTER = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)


def _load_txt(path: Path) -> List[Document]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    chunks = SPLITTER.split_text(text)
    return [Document(page_content=c, metadata={"source": str(path)}) for c in chunks]


def _load_pdf(path: Path) -> List[Document]:
    try:
        from langchain_community.document_loaders import PyPDFLoader
        loader = PyPDFLoader(str(path))
        pages = loader.load()
        docs = []
        for p in pages:
            for chunk in SPLITTER.split_text(p.page_content):
                docs.append(Document(page_content=chunk, metadata={**p.metadata, "source": str(path)}))
        return docs
    except ImportError:
        print("pypdf not installed — run: uv add pypdf")
        return []


def ingest_file(path: str) -> int:
    p = Path(path)
    if not p.exists():
        print(f"File not found: {path}")
        return 0
    suffix = p.suffix.lower()
    if suffix == ".pdf":
        docs = _load_pdf(p)
    else:
        docs = _load_txt(p)
    if docs:
        add_documents(docs)
        print(f"Ingested {len(docs)} chunks from {p.name}")
    return len(docs)


def ingest_directory(dir_path: str) -> int:
    total = 0
    for p in Path(dir_path).rglob("*"):
        if p.suffix.lower() in {".txt", ".md", ".pdf"}:
            total += ingest_file(str(p))
    return total


def ingest_text(text: str, source: str = "manual") -> int:
    chunks = SPLITTER.split_text(text)
    docs = [Document(page_content=c, metadata={"source": source}) for c in chunks]
    add_documents(docs)
    return len(docs)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest documents into LLM Council RAG store")
    parser.add_argument("--file",   help="Path to a single file (.txt, .md, .pdf)")
    parser.add_argument("--dir",    help="Directory to ingest recursively")
    parser.add_argument("--text",   help="Raw text string to ingest")
    parser.add_argument("--source", default="manual", help="Source label for raw text")
    args = parser.parse_args()

    if args.file:
        ingest_file(args.file)
    elif args.dir:
        total = ingest_directory(args.dir)
        print(f"Total chunks ingested: {total}")
    elif args.text:
        n = ingest_text(args.text, args.source)
        print(f"Ingested {n} chunks")
    else:
        parser.print_help()
        sys.exit(1)

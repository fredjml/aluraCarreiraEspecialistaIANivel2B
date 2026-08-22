"""Pipeline RAG demonstrativa e determinística para políticas fictícias do Bytebank."""
from __future__ import annotations

import argparse
import csv
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    class RecursiveCharacterTextSplitter:
        def __init__(self, chunk_size: int = 500, chunk_overlap: int = 100):
            self.chunk_size = chunk_size
            self.chunk_overlap = chunk_overlap

        def split_text(self, text: str) -> list[str]:
            if len(text) <= self.chunk_size:
                return [text]
            chunks = []
            start = 0
            while start < len(text):
                end = min(start + self.chunk_size, len(text))
                chunks.append(text[start:end])
                if end == len(text):
                    break
                start = end - self.chunk_overlap
            return chunks


@dataclass(frozen=True)
class Document:
    page_content: str
    metadata: dict[str, str | int]


KEYWORDS = {
    "tarifas": ("tarifa", "anuidade", "juros", "taxa"),
    "seguranca": ("segurança", "senha", "token", "fraude", "lgpd", "autenticação"),
    "abertura": ("abrir", "abertura", "solicitar"),
    "cartao": ("cartão", "platinum", "gold", "silver", "fatura"),
    "rh": ("colaborador", "férias", "home office", "trabalho remoto"),
    "suporte": ("chamado", "ouvidoria", "atendimento", "reclamação"),
}


def semantic_category(text: str, domain: str) -> str:
    normalized = text.lower()
    for category, words in KEYWORDS.items():
        if any(word in normalized for word in words):
            return category
    return domain


def load_documents(csv_path: Path) -> list[Document]:
    with csv_path.open(encoding="utf-8", newline="") as handle:
        rows = csv.DictReader(handle)
        documents = []
        for row in rows:
            content = row["conteudo"]
            metadata = {
                "id": int(row["id"]),
                "dominio": row["dominio"],
                "secao": row["secao"],
                "nivel_acesso": row["nivel_acesso"],
                "categoria_semantica": semantic_category(content, row["dominio"]),
                "origem": str(csv_path),
            }
            documents.append(Document(content, metadata))
        return documents


def split_documents(documents: Iterable[Document]) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    chunks = []
    for document in documents:
        for index, content in enumerate(splitter.split_text(document.page_content)):
            metadata = {**document.metadata, "chunk_index": index}
            chunks.append(Document(content, metadata))
    return chunks


def build_chroma_store(chunks: list[Document], persist_directory: str = "chroma_db"):
    """Cria um índice Chroma opcional; o modo local não depende desta integração."""
    from langchain_community.embeddings import HuggingFaceEmbeddings
    from langchain_community.vectorstores import Chroma
    from langchain_core.documents import Document as LangChainDocument

    langchain_documents = [
        LangChainDocument(page_content=item.page_content, metadata=item.metadata)
        for item in chunks
    ]
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    return Chroma.from_documents(
        documents=langchain_documents,
        embedding=embeddings,
        persist_directory=persist_directory,
    )


def terms(text: str) -> set[str]:
    return set(re.findall(r"[\wÀ-ÿ]+", text.lower()))


def score(query: str, document: Document) -> float:
    query_terms = terms(query)
    document_terms = terms(document.page_content)
    if not query_terms or not document_terms:
        return 0.0
    overlap = len(query_terms & document_terms)
    return overlap / math.sqrt(len(query_terms) * len(document_terms))


def retrieve(query: str, chunks: list[Document], k: int = 4) -> list[Document]:
    return sorted(chunks, key=lambda item: score(query, item), reverse=True)[:k]


def rerank(query: str, chunks: list[Document], candidates: int = 8, selected: int = 4) -> list[Document]:
    return retrieve(query, chunks, k=candidates)[:selected]


def answer(query: str, documents: list[Document]) -> str:
    if not documents or score(query, documents[0]) == 0:
        return "Não encontrei evidência suficiente nas políticas fictícias para responder com segurança."
    excerpts = " ".join(document.page_content for document in documents[:2])
    sources = ", ".join(f"id={item.metadata['id']}" for item in documents[:2])
    return f"Com base nas políticas recuperadas ({sources}): {excerpts}"


def query(csv_path: Path, question: str) -> dict[str, object]:
    chunks = split_documents(load_documents(csv_path))
    retrieved = retrieve(question, chunks, k=4)
    candidates = retrieve(question, chunks, k=8)
    selected = rerank(question, chunks)
    return {
        "question": question,
        "answer": answer(question, selected),
        "source_documents": selected,
        "retrieved_k4": retrieved,
        "reranked_candidates": len(candidates),
        "reranked_selected": len(selected),
        "mode": "local_deterministic",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--question", default="Quais são as regras para abrir uma conta?")
    parser.add_argument("--csv", type=Path, default=Path("data/politicas_bytebank.csv"))
    args = parser.parse_args()
    result = query(args.csv, args.question)
    print(result["answer"])
    print("Fontes:")
    for document in result["source_documents"]:
        print(document.metadata)
    print(f"Reranking: {result['reranked_candidates']} candidatos -> {result['reranked_selected']} selecionados")


if __name__ == "__main__":
    main()

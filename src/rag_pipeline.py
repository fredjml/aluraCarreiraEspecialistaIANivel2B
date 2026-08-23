"""Pipeline RAG demonstrativa e determinística para políticas fictícias do Bytebank."""
from __future__ import annotations

import argparse
import csv
import math
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from .gemini_integration import GeminiIntegration, resolve_mode

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
    """Indexa os chunks no Chroma com embeddings locais e IDs estáveis."""
    import chromadb
    from sentence_transformers import SentenceTransformer

    model_name = os.getenv(
        "BYTEBANK_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
    )
    local_only = os.getenv("BYTEBANK_HF_LOCAL_ONLY", "1").strip() != "0"
    model = SentenceTransformer(model_name, local_files_only=local_only)
    client = chromadb.PersistentClient(path=persist_directory)
    collection = client.get_or_create_collection(
        name="bytebank_politicas_v1",
        metadata={"hnsw:space": "cosine", "embedding_model": model_name},
    )
    ids = [f"policy-{item.metadata['id']}-chunk-{item.metadata['chunk_index']}" for item in chunks]
    texts = [item.page_content for item in chunks]
    embeddings = model.encode(texts, normalize_embeddings=True).tolist()
    collection.upsert(
        ids=ids,
        documents=texts,
        embeddings=embeddings,
        metadatas=[item.metadata for item in chunks],
    )
    return ChromaPolicyStore(collection, model, persist_directory, model_name)


@dataclass
class ChromaPolicyStore:
    """Adaptador mínimo para recuperar políticas do índice persistente."""

    collection: Any
    model: Any
    persist_directory: str
    model_name: str

    def search(self, question: str, k: int, allowed_levels: set[str]) -> list[Document]:
        query_embedding = self.model.encode(
            [question], normalize_embeddings=True
        ).tolist()
        where = {"nivel_acesso": {"$in": sorted(allowed_levels)}}
        result = self.collection.query(
            query_embeddings=query_embedding,
            n_results=k,
            where=where,
            include=["documents", "metadatas", "distances"],
        )
        documents = result.get("documents", [[]])[0]
        metadatas = result.get("metadatas", [[]])[0]
        distances = result.get("distances", [[]])[0]
        return [
            Document(text, {**metadata, "distancia_vetorial": round(float(distance), 6)})
            for text, metadata, distance in zip(documents, metadatas, distances)
        ]


_CHROMA_CACHE: dict[tuple[str, str], ChromaPolicyStore] = {}


def get_chroma_store(
    csv_path: Path, persist_directory: str = "outputs/chroma_db"
) -> ChromaPolicyStore:
    """Constrói o índice uma vez por processo e o reutiliza nas consultas."""
    cache_key = (str(csv_path.resolve()), str(Path(persist_directory).resolve()))
    if cache_key not in _CHROMA_CACHE:
        _CHROMA_CACHE[cache_key] = build_chroma_store(
            split_documents(load_documents(csv_path)), persist_directory
        )
    return _CHROMA_CACHE[cache_key]


def terms(text: str) -> set[str]:
    return set(re.findall(r"[\wÀ-ÿ]+", text.lower()))


def score(query: str, document: Document) -> float:
    query_terms = terms(query)
    document_terms = terms(document.page_content)
    if not query_terms or not document_terms:
        return 0.0
    overlap = len(query_terms & document_terms)
    return overlap / math.sqrt(len(query_terms) * len(document_terms))


def filter_by_access(
    chunks: Iterable[Document], allowed_levels: set[str]
) -> list[Document]:
    """Aplica autorização antes do retriever, evitando vazamento por contexto."""
    return [
        item for item in chunks if str(item.metadata["nivel_acesso"]) in allowed_levels
    ]


def retrieve(
    query: str,
    chunks: list[Document],
    k: int = 4,
    allowed_levels: set[str] | None = None,
) -> list[Document]:
    authorized = filter_by_access(chunks, allowed_levels or {"publico"})
    return sorted(authorized, key=lambda item: score(query, item), reverse=True)[:k]


def hybrid_candidates(
    semantic: list[Document], lexical: list[Document], k: int = 8
) -> list[Document]:
    """Funde rankings por reciprocidade para melhorar consultas em português."""
    by_id: dict[tuple[int, int], Document] = {}
    fusion: dict[tuple[int, int], float] = {}
    for ranking in (semantic, lexical):
        for position, document in enumerate(ranking, start=1):
            key = (
                int(document.metadata["id"]),
                int(document.metadata.get("chunk_index", 0)),
            )
            by_id[key] = document
            fusion[key] = fusion.get(key, 0.0) + 1.0 / (60 + position)
    ordered = sorted(fusion, key=lambda key: (-fusion[key], key))
    return [by_id[key] for key in ordered[:k]]


def rerank(query: str, chunks: list[Document], candidates: int = 8, selected: int = 4) -> list[Document]:
    return retrieve(query, chunks, k=candidates)[:selected]


def answer(query: str, documents: list[Document]) -> str:
    if not documents or score(query, documents[0]) == 0:
        return "Não encontrei evidência suficiente nas políticas fictícias para responder com segurança."
    excerpts = " ".join(document.page_content for document in documents)
    sources = ", ".join(f"id={item.metadata['id']}" for item in documents)
    return f"Com base nas políticas recuperadas ({sources}): {excerpts}"


def query(
    csv_path: Path,
    question: str,
    llm_mode: str = "local",
    gemini: Any | None = None,
    retrieval_backend: str = "auto",
    allowed_levels: set[str] | None = None,
    vector_store: Any | None = None,
    persist_directory: str = "outputs/chroma_db",
) -> dict[str, object]:
    """Executa recuperação, reranking e geração com fallback rastreável.

    A API pública permanece local por padrão para não provocar chamadas externas
    inesperadas. A CLI e a avaliação usam ``auto`` e ativam Gemini apenas quando
    a chave está configurada ou quando o modo ``gemini`` é solicitado.
    """
    if retrieval_backend not in {"auto", "chroma", "lexical"}:
        raise ValueError("retrieval_backend deve ser auto, chroma ou lexical")
    access = allowed_levels or {"publico"}
    chunks = split_documents(load_documents(csv_path))
    fallbacks: list[str] = []
    retrieval_mode = "lexical_deterministic"
    store = vector_store
    if retrieval_backend in {"auto", "chroma"} and store is None:
        try:
            store = get_chroma_store(csv_path, persist_directory)
        except Exception as exc:
            if retrieval_backend == "chroma":
                raise
            fallbacks.append(f"recuperação Chroma: {type(exc).__name__}: {exc}")
    if store is not None and retrieval_backend != "lexical":
        semantic = store.search(question, k=8, allowed_levels=access)
        lexical = retrieve(question, chunks, k=8, allowed_levels=access)
        retrieved = semantic[:4]
        candidates = hybrid_candidates(semantic, lexical, k=8)
        retrieval_mode = "chroma_embeddings+lexical_hybrid"
    else:
        retrieved = retrieve(question, chunks, k=4, allowed_levels=access)
        candidates = retrieve(question, chunks, k=8, allowed_levels=access)
    selected = rerank(question, candidates, candidates=8, selected=4)
    rerank_mode = "local_deterministic"
    generation_mode = "local_deterministic"

    requested_mode = resolve_mode(llm_mode)
    client = gemini if requested_mode == "gemini" else None
    if requested_mode == "gemini" and client is None:
        client, reason = GeminiIntegration.create_from_env("gemini")
        if reason:
            fallbacks.append(f"inicialização Gemini: {reason}")

    if client is not None:
        try:
            ranking = client.rerank(question, candidates)
            selected = [candidates[index] for index in ranking[:4]]
            rerank_mode = "gemini"
        except Exception as exc:  # API externa: fallback é parte do contrato
            fallbacks.append(f"reranking Gemini: {type(exc).__name__}: {exc}")

    response = answer(question, selected)
    if client is not None:
        try:
            response = client.answer_with_rag(question, selected)
            generation_mode = "gemini"
        except Exception as exc:  # API externa: nunca inventar sucesso
            fallbacks.append(f"geração RAG Gemini: {type(exc).__name__}: {exc}")

    if rerank_mode == generation_mode == "gemini":
        mode = "gemini"
    elif "gemini" in {rerank_mode, generation_mode}:
        mode = "hybrid_with_fallback"
    else:
        mode = "local_deterministic"
    return {
        "question": question,
        "answer": response,
        "source_documents": selected,
        "retrieved_k4": retrieved,
        "reranked_candidates": len(candidates),
        "reranked_selected": len(selected),
        "mode": mode,
        "rerank_mode": rerank_mode,
        "generation_mode": generation_mode,
        "retrieval_mode": retrieval_mode,
        "allowed_levels": sorted(access),
        "fallbacks": fallbacks,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--question", default="Quais são as regras para abrir uma conta?")
    parser.add_argument("--csv", type=Path, default=Path("data/politicas_bytebank.csv"))
    parser.add_argument(
        "--mode",
        choices=("auto", "local", "gemini"),
        default=None,
        help="sobrescreve BYTEBANK_LLM_MODE; auto usa Gemini quando há chave",
    )
    parser.add_argument(
        "--retrieval",
        choices=("auto", "chroma", "lexical"),
        default="auto",
        help="Chroma usa embeddings locais; auto registra fallback se indisponível",
    )
    args = parser.parse_args()
    result = query(
        args.csv, args.question, llm_mode=args.mode, retrieval_backend=args.retrieval
    )
    print(result["answer"])
    print("Fontes:")
    for document in result["source_documents"]:
        print(document.metadata)
    print(f"Reranking: {result['reranked_candidates']} candidatos -> {result['reranked_selected']} selecionados")
    print(
        f"Modos: recuperação={result['retrieval_mode']}; reranking={result['rerank_mode']}; "
        f"geração={result['generation_mode']}"
    )
    for fallback in result["fallbacks"]:
        print(f"Fallback: {fallback}")


if __name__ == "__main__":
    main()

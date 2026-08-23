"""Avaliação comparativa RAG com Gemini e fallback local determinístico."""
from __future__ import annotations

import argparse
import csv
import re
import unicodedata
from pathlib import Path
from typing import Any

from .gemini_integration import GeminiIntegration, JudgeDecision, resolve_mode
from .rag_pipeline import query


VALIDATION = [
    ("Quais documentos são necessários para abrir conta?", "CPF válido, comprovante de residência e documento de identidade"),
    ("Quanto custa a TED adicional?", "R$9,90"),
    ("Qual é a anuidade do cartão Platinum?", "R$59,90"),
    ("Qual o limite máximo do cartão Gold?", "R$20.000"),
    ("Como contestar uma transação não reconhecida?", "em até 48 horas pelo aplicativo"),
    ("Qual o prazo para excluir dados pessoais?", "15 dias úteis"),
    ("Qual o prazo de resposta da ouvidoria?", "10 dias úteis"),
    ("Qual o limite do Pix noturno?", "R$1.000 por transação"),
]


def _normalize(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text.lower())
    without_accents = "".join(char for char in decomposed if not unicodedata.combining(char))
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", without_accents)).strip()


def _clean_output(text: str) -> str:
    """Remove espaços finais de respostas multiline antes de versionar o CSV."""
    return "\n".join(line.rstrip() for line in text.splitlines()).strip()


def local_baseline() -> str:
    return (
        "Modo local determinístico: resposta sem RAG indisponível, pois não há "
        "modelo externo configurado e nenhuma política foi consultada."
    )


def local_judge(expected: str, answer: str, require_source: bool) -> JudgeDecision:
    expected_terms = set(_normalize(expected).split())
    answer_terms = set(_normalize(answer).split())
    fact_present = expected_terms.issubset(answer_terms)
    source_present = bool(re.search(r"(?:\[)?id=\d+", answer, flags=re.IGNORECASE))
    correct = fact_present and (source_present or not require_source)
    reasons = ["fato do gabarito encontrado" if fact_present else "fato do gabarito ausente"]
    if require_source:
        reasons.append("fonte citada" if source_present else "fonte não citada")
    return JudgeDecision(
        correct=correct,
        score=100 if correct else 0,
        rationale="; ".join(reasons),
        mode="local_deterministic",
    )


def _judge(
    gemini: Any | None,
    question: str,
    expected: str,
    answer: str,
    require_source: bool,
) -> tuple[JudgeDecision, str | None]:
    if gemini is not None:
        try:
            return gemini.judge(question, expected, answer, require_source), None
        except Exception as exc:
            reason = f"juiz Gemini: {type(exc).__name__}: {exc}"
            return local_judge(expected, answer, require_source), reason
    return local_judge(expected, answer, require_source), None


def evaluate(
    csv_path: Path,
    llm_mode: str | None = None,
    gemini: Any | None = None,
    retrieval_backend: str = "auto",
) -> list[dict[str, str]]:
    requested_mode = resolve_mode(llm_mode)
    initialization_reason: str | None = None
    client = gemini if requested_mode == "gemini" else None
    if requested_mode == "gemini" and client is None:
        client, initialization_reason = GeminiIntegration.create_from_env("gemini")

    rows = []
    for question, expected in VALIDATION:
        fallbacks = [initialization_reason] if initialization_reason else []
        without_rag = local_baseline()
        baseline_mode = "local_deterministic"
        if client is not None:
            try:
                without_rag = client.answer_without_rag(question)
                baseline_mode = "gemini"
            except Exception as exc:
                fallbacks.append(f"geração sem RAG Gemini: {type(exc).__name__}: {exc}")

        result = query(
            csv_path,
            question,
            llm_mode="gemini" if client is not None else "local",
            gemini=client,
            retrieval_backend=retrieval_backend,
        )
        without_rag = _clean_output(without_rag)
        with_rag = _clean_output(str(result["answer"]))
        fallbacks.extend(str(item) for item in result["fallbacks"])

        judge_without, judge_without_error = _judge(
            client, question, expected, without_rag, require_source=False
        )
        judge_with, judge_with_error = _judge(
            client, question, expected, with_rag, require_source=True
        )
        if judge_without_error:
            fallbacks.append(judge_without_error)
        if judge_with_error:
            fallbacks.append(judge_with_error)

        sources = ", ".join(
            f"id={document.metadata['id']}" for document in result["source_documents"]
        )
        judge_modes = sorted({judge_without.mode, judge_with.mode})
        rows.append({
            "pergunta": question,
            "gabarito": expected,
            "resposta_sem_rag": without_rag,
            "resposta_com_rag": with_rag,
            "fontes_rag": sources,
            "modo_sem_rag": baseline_mode,
            "modo_reranking": str(result["rerank_mode"]),
            "modo_recuperacao": str(result["retrieval_mode"]),
            "modo_com_rag": str(result["generation_mode"]),
            "modo_juiz": "+".join(judge_modes),
            "acerto_sem_rag": "sim" if judge_without.correct else "não",
            "nota_sem_rag": str(judge_without.score),
            "justificativa_sem_rag": judge_without.rationale,
            "acerto_com_rag": "sim" if judge_with.correct else "não",
            "nota_com_rag": str(judge_with.score),
            "justificativa_com_rag": judge_with.rationale,
            "fallbacks": " | ".join(dict.fromkeys(item for item in fallbacks if item)),
        })
    return rows


def summarize(rows: list[dict[str, str]]) -> dict[str, float | int]:
    total = len(rows)
    without_hits = sum(row["acerto_sem_rag"] == "sim" for row in rows)
    with_hits = sum(row["acerto_com_rag"] == "sim" for row in rows)
    return {
        "total": total,
        "acertos_sem_rag": without_hits,
        "acertos_com_rag": with_hits,
        "percentual_sem_rag": round(100 * without_hits / total, 2) if total else 0.0,
        "percentual_com_rag": round(100 * with_hits / total, 2) if total else 0.0,
    }


def write_report(
    csv_path: Path,
    output_path: Path,
    llm_mode: str | None = None,
    retrieval_backend: str = "auto",
) -> dict[str, float | int]:
    rows = evaluate(
        csv_path, llm_mode=llm_mode, retrieval_backend=retrieval_backend
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    return summarize(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", type=Path, default=Path("data/politicas_bytebank.csv"))
    parser.add_argument("--output", type=Path, default=Path("outputs/avaliacao_rag.csv"))
    parser.add_argument(
        "--mode",
        choices=("auto", "local", "gemini"),
        default=None,
        help="sobrescreve BYTEBANK_LLM_MODE",
    )
    parser.add_argument(
        "--retrieval",
        choices=("auto", "chroma", "lexical"),
        default="auto",
    )
    args = parser.parse_args()

    summary = write_report(
        args.csv, args.output, llm_mode=args.mode, retrieval_backend=args.retrieval
    )
    print(f"Relatório criado em {args.output}")
    print(
        "Acurácia: "
        f"sem RAG={summary['acertos_sem_rag']}/{summary['total']} "
        f"({summary['percentual_sem_rag']}%); "
        f"com RAG={summary['acertos_com_rag']}/{summary['total']} "
        f"({summary['percentual_com_rag']}%)."
    )
    print("Consulte as colunas de modo e fallbacks antes de atribuir o resultado ao Gemini.")


if __name__ == "__main__":
    main()

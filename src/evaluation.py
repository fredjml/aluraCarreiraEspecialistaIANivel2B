"""Avaliação comparativa RAG com Gemini e fallback local determinístico."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import unicodedata
from pathlib import Path
from typing import Any

from .gemini_integration import GeminiIntegration, JudgeDecision, resolve_mode
from .rag_pipeline import query


DEFAULT_VALIDATION_PATH = Path("data/avaliacao_rag.csv")


def load_validation_cases(path: Path = DEFAULT_VALIDATION_PATH) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        cases = list(csv.DictReader(handle))
    required = {"id", "tipo", "pergunta", "gabarito", "exige_fonte", "nivel_acesso"}
    if not cases or not required.issubset(cases[0]):
        raise ValueError("dataset de avaliação não atende ao contrato")
    return cases


def _load_state(path: Path | None) -> dict[str, dict[str, str]]:
    if path is None or not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _save_state(path: Path | None, state: dict[str, dict[str, str]]) -> None:
    if path is None:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


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


def _client_metadata(client: Any | None) -> tuple[str, str, str]:
    if client is None:
        return "local_deterministic", "-", "requests=0; retries=0; latency_ms=0"
    snapshot = getattr(client, "metrics_snapshot", lambda: {})()
    provider = str(snapshot.get("provider", "gemini"))
    model = str(snapshot.get("model", "configured"))
    metrics = (
        f"requests={snapshot.get('requests', 'n/a')}; "
        f"retries={snapshot.get('retries', 'n/a')}; "
        f"latency_ms={snapshot.get('latency_ms', 'n/a')}"
    )
    return provider, model, metrics


def evaluate(
    csv_path: Path,
    llm_mode: str | None = None,
    gemini: Any | None = None,
    judge: Any | None = None,
    retrieval_backend: str = "auto",
    validation_path: Path = DEFAULT_VALIDATION_PATH,
    cache_path: Path | None = None,
    checkpoint_path: Path | None = None,
) -> list[dict[str, str]]:
    requested_mode = resolve_mode(llm_mode)
    initialization_reason: str | None = None
    client = gemini if requested_mode == "gemini" else None
    judge_client = judge if requested_mode == "gemini" else None
    judge_initialization_reason: str | None = None
    if requested_mode == "gemini" and client is None:
        client, initialization_reason = GeminiIntegration.create_from_env(
            "gemini", model_variable="BYTEBANK_GENERATOR_MODEL"
        )
    if requested_mode == "gemini" and judge_client is None:
        judge_client, judge_initialization_reason = GeminiIntegration.create_from_env(
            "gemini", model_variable="BYTEBANK_JUDGE_MODEL"
        )
    if judge is None and gemini is not None:
        # Mantém compatibilidade com injeções de teste; produção cria clientes separados.
        judge_client = gemini

    cases = load_validation_cases(validation_path)
    cache = _load_state(cache_path)
    checkpoint = _load_state(checkpoint_path)
    rows = []
    for case in cases:
        question = case["pergunta"]
        expected = case["gabarito"]
        require_source = case["exige_fonte"].strip().lower() == "sim"
        cache_key = hashlib.sha256(
            json.dumps(
                {"case": case, "mode": requested_mode, "retrieval": retrieval_backend},
                sort_keys=True,
            ).encode("utf-8")
        ).hexdigest()
        cached = checkpoint.get(cache_key) or cache.get(cache_key)
        if cached is not None:
            rows.append(cached)
            continue
        fallbacks = [item for item in (initialization_reason, judge_initialization_reason) if item]
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
            judge_client, question, expected, without_rag, require_source=False
        )
        judge_with, judge_with_error = _judge(
            judge_client, question, expected, with_rag, require_source=require_source
        )
        if judge_without_error:
            fallbacks.append(judge_without_error)
        if judge_with_error:
            fallbacks.append(judge_with_error)

        sources = ", ".join(
            f"id={document.metadata['id']}" for document in result["source_documents"]
        )
        judge_modes = sorted({judge_without.mode, judge_with.mode})
        generator_provider, generator_model, generator_metrics = _client_metadata(client)
        judge_provider, judge_model, judge_metrics = _client_metadata(judge_client)
        row = {
            "id_caso": case["id"],
            "tipo_caso": case["tipo"],
            "nivel_acesso": case["nivel_acesso"],
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
            "provedor_gerador": generator_provider,
            "modelo_gerador": generator_model,
            "metricas_gerador": generator_metrics,
            "provedor_juiz": judge_provider,
            "modelo_juiz": judge_model,
            "metricas_juiz": judge_metrics,
            "acerto_sem_rag": "sim" if judge_without.correct else "não",
            "nota_sem_rag": str(judge_without.score),
            "justificativa_sem_rag": judge_without.rationale,
            "acerto_com_rag": "sim" if judge_with.correct else "não",
            "nota_com_rag": str(judge_with.score),
            "justificativa_com_rag": judge_with.rationale,
            "fallbacks": " | ".join(dict.fromkeys(item for item in fallbacks if item)),
        }
        rows.append(row)
        cache[cache_key] = row
        checkpoint[cache_key] = row
        _save_state(cache_path, cache)
        _save_state(checkpoint_path, checkpoint)
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
    validation_path: Path = DEFAULT_VALIDATION_PATH,
    cache_path: Path | None = Path("outputs/avaliacao_cache.json"),
    checkpoint_path: Path | None = Path("outputs/avaliacao_checkpoint.json"),
) -> dict[str, float | int]:
    rows = evaluate(
        csv_path,
        llm_mode=llm_mode,
        retrieval_backend=retrieval_backend,
        validation_path=validation_path,
        cache_path=cache_path,
        checkpoint_path=checkpoint_path,
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
    parser.add_argument("--cases", type=Path, default=DEFAULT_VALIDATION_PATH)
    parser.add_argument("--cache", type=Path, default=Path("outputs/avaliacao_cache.json"))
    parser.add_argument("--checkpoint", type=Path, default=Path("outputs/avaliacao_checkpoint.json"))
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
        args.csv,
        args.output,
        llm_mode=args.mode,
        retrieval_backend=args.retrieval,
        validation_path=args.cases,
        cache_path=args.cache,
        checkpoint_path=args.checkpoint,
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

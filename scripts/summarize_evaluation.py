"""Resume a avaliação sem imprimir respostas ou informações sensíveis."""
from __future__ import annotations

import csv
import re
from collections import Counter
from pathlib import Path


def main() -> None:
    path = Path("outputs/avaliacao_rag.csv")
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    for field in (
        "modo_sem_rag",
        "modo_recuperacao",
        "modo_reranking",
        "modo_com_rag",
        "modo_juiz",
    ):
        print(f"{field}={dict(Counter(row[field] for row in rows))}")
    print(f"fallbacks={sum(bool(row['fallbacks']) for row in rows)}/{len(rows)}")
    kinds = Counter()
    for row in rows:
        for fallback in row["fallbacks"].split(" | ") if row["fallbacks"] else []:
            parts = fallback.split(":", 2)
            kinds[": ".join(parts[:2])] += 1
    print(f"tipos_fallback={dict(kinds)}")
    statuses = Counter(
        match.group(1)
        for row in rows
        for match in re.finditer(r"ClientError:\s+(\d+)", row["fallbacks"])
    )
    print(f"status_http_fallback={dict(statuses)}")
    print(
        "falhas_com_rag="
        + " | ".join(row["pergunta"] for row in rows if row["acerto_com_rag"] != "sim")
    )


if __name__ == "__main__":
    main()

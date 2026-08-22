"""Avaliação estruturada; não simula nota de LLM sem credencial."""
from __future__ import annotations

import csv
from pathlib import Path
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


def evaluate(csv_path: Path) -> list[dict[str, str]]:
    rows = []
    for question, expected in VALIDATION:
        result = query(csv_path, question)
        response = str(result["answer"])
        rows.append({
            "pergunta": question,
            "gabarito": expected,
            "resposta_sem_rag": "PENDENTE: requer LLM configurado",
            "resposta_com_rag": response,
            "criterio": "resposta deve conter o gabarito e citar fonte",
            "resultado": "manual: verificar" if expected.lower() not in response.lower() else "compatível com gabarito local",
        })
    return rows


def write_report(csv_path: Path, output_path: Path) -> None:
    rows = evaluate(csv_path)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    output = Path("outputs/avaliacao_rag.csv")
    output.parent.mkdir(exist_ok=True)
    write_report(Path("data/politicas_bytebank.csv"), output)
    print(f"Relatório criado em {output}; julgamento de LLM permanece pendente.")

"""Valida estrutura, dados, sintaxe e contratos do projeto."""
from __future__ import annotations

import csv
import importlib.util
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
REQUIRED = [
    "README.md", "PLANO_EXECUCAO.md", ".env.example",
    ".github/instructions/bytebank.instructions.md",
    ".github/skills/validar-entregaveis-bytebank/SKILL.md",
    "data/politicas_bytebank.csv", "data/composicao_time.csv", "data/carreira_y.csv",
    "data/glossario_rag.csv", "data/agent_cards.csv",
    "Docs/01-governanca.md", "Docs/02-arquitetura-rag.md",
    "Docs/04-arquitetura-multiagente.md", "Docs/05-avaliacao-rag.md",
    "Docs/relatorio_levantamento_bytebank.md", "Docs/relatorio_levantamento_bytebank.docx",
    "Docs/relatorio_implementacao_bytebank.md", "Docs/relatorio_implementacao_bytebank.docx",
    "Docs/analises/01-cobertura-requisitos.md", "Docs/analises/02-execucao-tecnica.md",
    "Docs/analises/03-riscos-residuais.md", "Docs/revisoes/01-revisao-funcional.md",
    "Docs/revisoes/02-revisao-seguranca.md", "Docs/revisoes/03-revisao-entrega.md",
    "diagrams/rag.mmd", "diagrams/rag.svg", "diagrams/multiagente.mmd", "diagrams/multiagente.svg",
    "src/rag_pipeline.py", "src/gemini_integration.py", "src/evaluation.py",
    "src/multiagent_graph.py", "src/app.py",
]


def check_files() -> list[str]:
    errors = []
    for relative in REQUIRED:
        path = ROOT / relative
        if not path.exists() or path.stat().st_size == 0:
            errors.append(f"arquivo ausente ou vazio: {relative}")
    return errors


def check_csvs() -> list[str]:
    errors = []
    policy_path = ROOT / "data/politicas_bytebank.csv"
    with policy_path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 50:
        errors.append(f"dataset esperado com 50 registros, encontrado: {len(rows)}")
    expected = {"id", "dominio", "secao", "conteudo", "nivel_acesso"}
    if set(rows[0]) != expected:
        errors.append("cabeçalho do dataset não corresponde ao contrato")
    if len(list(csv.DictReader((ROOT / "data/glossario_rag.csv").open(encoding="utf-8")))) < 15:
        errors.append("glossário tem menos de 15 termos")
    return errors


def check_python() -> list[str]:
    result = subprocess.run(
        [sys.executable, "-m", "compileall", "-q", "src", "tests", "scripts"],
        cwd=ROOT, capture_output=True, text=True,
    )
    return [result.stderr.strip()] if result.returncode else []


def check_contracts() -> list[str]:
    errors = []
    if importlib.util.find_spec("langgraph"):
        from src.multiagent_graph import build_graph
        result = build_graph().invoke({"mensagem": "Qual a anuidade do cartão?"})
        if result.get("classificacao") != "cartao_credito":
            errors.append("roteamento de cartão inválido")
    from src.rag_pipeline import load_documents, query, split_documents
    documents = load_documents(ROOT / "data/politicas_bytebank.csv")
    chunks = split_documents(documents)
    required = {"id", "dominio", "secao", "nivel_acesso", "categoria_semantica"}
    if not required.issubset(chunks[0].metadata):
        errors.append("metadados obrigatórios não preservados")
    result = query(
        ROOT / "data/politicas_bytebank.csv",
        "Qual o limite do Pix noturno?",
        llm_mode="local", retrieval_backend="lexical",
    )
    if result["reranked_candidates"] != 8 or result["reranked_selected"] != 4:
        errors.append("contrato de reranking 8 para 4 não atendido")
    return errors


def main() -> int:
    checks = check_files() + check_csvs() + check_python() + check_contracts()
    if checks:
        print("CONFORMIDADE=FALHA")
        print("\n".join(f"- {item}" for item in checks))
        return 1
    print("CONFORMIDADE=OK")
    print("Arquivos, CSVs, sintaxe Python, metadados, roteamento e reranking validados.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

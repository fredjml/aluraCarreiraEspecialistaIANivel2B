"""Servidor MCP stdio para o protótipo fictício do Bytebank.

Recursos locais funcionam sem configuração externa. As ferramentas que chamam
um core bancário exigem endpoint, token e aprovação humana explícita.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")
mcp = FastMCP("bytebank-nivel2")


def _policies() -> list[dict[str, str]]:
    import csv

    with (ROOT / "data" / "politicas_bytebank.csv").open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _external_request(method: str, path: str, payload: dict | None = None) -> dict:
    base_url = os.getenv("BYTEBANK_CORE_API_BASE_URL", "").rstrip("/")
    token = os.getenv("BYTEBANK_CORE_API_TOKEN", "")
    if not base_url or not token:
        return {
            "status": "not_configured",
            "message": "Configure BYTEBANK_CORE_API_BASE_URL e BYTEBANK_CORE_API_TOKEN no .env.",
        }
    body = json.dumps(payload).encode("utf-8") if payload else None
    request = Request(
        f"{base_url}/{path.lstrip('/')}",
        data=body,
        method=method,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    )
    try:
        with urlopen(request, timeout=10) as response:
            return {"status": "ok", "http_status": response.status, "data": json.loads(response.read())}
    except HTTPError as error:
        return {"status": "http_error", "http_status": error.code, "message": error.read().decode("utf-8", "replace")}
    except URLError as error:
        return {"status": "network_error", "message": str(error.reason)}


@mcp.resource("bytebank://policies/public")
def public_policies() -> str:
    """Políticas fictícias de acesso público para consulta local."""
    return json.dumps([row for row in _policies() if row["nivel_acesso"] == "publico"], ensure_ascii=False)


@mcp.resource("bytebank://clientes/{cliente_referencia}/saldo")
def saldo_resource(cliente_referencia: str) -> str:
    """Recurso de leitura de saldo; depende do core externo configurado."""
    return json.dumps(
        _external_request("GET", f"clientes/{cliente_referencia}/saldo"),
        ensure_ascii=False,
    )


@mcp.resource("bytebank://clientes/{cliente_referencia}/fatura")
def fatura_resource(cliente_referencia: str) -> str:
    """Recurso de leitura de fatura; depende do core externo configurado."""
    return json.dumps(
        _external_request("GET", f"clientes/{cliente_referencia}/fatura"),
        ensure_ascii=False,
    )


@mcp.tool()
def consultar_politicas(pergunta: str, nivel_acesso: str = "publico") -> dict:
    """Consulta políticas fictícias locais por termos, respeitando nível de acesso."""
    terms = {term for term in pergunta.lower().split() if len(term) > 2}
    matches = []
    for row in _policies():
        if row["nivel_acesso"] != nivel_acesso:
            continue
        text = row["conteudo"].lower()
        if terms & set(text.split()):
            matches.append(row)
    return {"status": "ok", "count": len(matches[:4]), "source_documents": matches[:4]}


@mcp.tool()
def consultar_saldo(cliente_referencia: str) -> dict:
    """Lê saldo no core externo configurado; não usa dados reais sem configuração local."""
    return _external_request("GET", f"clientes/{cliente_referencia}/saldo")


@mcp.tool()
def consultar_fatura(cliente_referencia: str) -> dict:
    """Lê fatura no core externo configurado; não usa dados reais sem configuração local."""
    return _external_request("GET", f"clientes/{cliente_referencia}/fatura")


@mcp.tool()
def criar_conta(
    cliente_referencia: str,
    tipo: str = "corrente",
    aprovado_por_humano: bool = False,
) -> dict:
    """Cria conta somente após HITL; nunca executa mutação sem aprovação."""
    if not aprovado_por_humano:
        return {
            "status": "human_approval_required",
            "message": "Aprovação humana obrigatória antes de criar conta.",
        }
    return _external_request(
        "POST",
        "contas",
        {"cliente_referencia": cliente_referencia, "tipo": tipo},
    )


@mcp.tool()
def solicitar_cartao(cliente_referencia: str, modalidade: str, aprovado_por_humano: bool = False) -> dict:
    """Solicita cartão somente após aprovação humana explícita e configuração do core externo."""
    if not aprovado_por_humano:
        return {"status": "human_approval_required", "message": "Aprovação humana obrigatória antes de solicitar cartão."}
    return _external_request("POST", "cartoes/solicitacoes", {"cliente_referencia": cliente_referencia, "modalidade": modalidade})


@mcp.prompt()
def resposta_fundamentada(pergunta: str) -> str:
    """Prompt para uma resposta RAG rastreável."""
    return f"Responda à pergunta '{pergunta}' somente com as políticas recuperadas e cite id, domínio e seção."


if __name__ == "__main__":
    mcp.run(transport="stdio")

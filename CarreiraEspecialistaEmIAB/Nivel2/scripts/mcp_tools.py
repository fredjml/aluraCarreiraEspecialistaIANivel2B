"""Servidor MCP local demonstrativo para o cenário fictício Bytebank.

O protocolo é JSON sobre stdin/stdout para permitir teste sem SDK ou rede.
Ferramentas mutam; recursos apenas leem; prompts são templates.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

TOOLS = {
    "criar_conta": "mutacao",
    "solicitar_cartao": "mutacao",
}
RESOURCES = {
    "consultar_saldo": "leitura",
    "consultar_fatura": "leitura",
}
PROMPTS = {
    "resposta_fundamentada": "Responda somente com base nas políticas recuperadas e cite as fontes.",
    "aprovacao_platinum": "Pause antes da mutação e solicite decisão humana auditável.",
}


def handle(request: dict) -> dict:
    operation = request.get("operation")
    name = request.get("name")
    if operation == "list":
        return {"tools": TOOLS, "resources": RESOURCES, "prompts": PROMPTS}
    if operation == "call_tool" and name in TOOLS:
        return {"status": "simulated", "kind": "mutation", "name": name, "requires_human_approval": name == "solicitar_cartao"}
    if operation == "read_resource" and name in RESOURCES:
        return {"status": "simulated", "kind": "read", "name": name, "data": "Dado fictício não conectado a sistemas reais."}
    if operation == "get_prompt" and name in PROMPTS:
        return {"status": "ok", "kind": "prompt", "name": name, "template": PROMPTS[name]}
    return {"status": "error", "message": "Operação MCP inválida ou capacidade inexistente."}


def main() -> None:
    for line in sys.stdin:
        if line.strip():
            print(json.dumps(handle(json.loads(line)), ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()

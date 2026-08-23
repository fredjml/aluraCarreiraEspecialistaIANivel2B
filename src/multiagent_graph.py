"""Protótipo multiagente com LangGraph, classificação Gemini e fallback local."""
from __future__ import annotations

import argparse
from typing import Any, TypedDict

from .gemini_integration import GeminiIntegration, resolve_mode

try:
    from langgraph.graph import END, START, StateGraph
except ImportError:
    END = "__end__"
    START = "__start__"

    class StateGraph:
        def __init__(self, state_type):
            self.nodes = {}
            self.edges = {}
            self.conditional = None

        def add_node(self, name, function):
            self.nodes[name] = function

        def add_edge(self, source, target):
            self.edges[source] = target

        def add_conditional_edges(self, source, router):
            self.conditional = (source, router)

        def compile(self):
            graph = self
            class Compiled:
                def invoke(self, state):
                    current = graph.edges[START]
                    while current != END:
                        state = {**state, **graph.nodes[current](state)}
                        if graph.conditional and graph.conditional[0] == current:
                            current = graph.conditional[1](state)
                        else:
                            current = graph.edges.get(current, END)
                    return state
            return Compiled()


class AgentState(TypedDict, total=False):
    mensagem: str
    classificacao: str
    resposta_agente: str
    resposta_final: str
    modo_classificacao: str
    fallbacks: list[str]
    requer_aprovacao_humana: bool


def classify_local(message: str) -> str:
    """Classificador determinístico usado em testes e fallback auditável."""
    message = message.lower()
    if any(word in message for word in ("cartão", "cartao", "fatura", "platinum", "anuidade")):
        return "cartao_credito"
    if any(word in message for word in ("conta", "pix", "ted", "saldo", "empréstimo", "emprestimo")):
        return "conta_corrente"
    return "suporte"


def make_classifier(client: Any | None = None):
    def classify(state: AgentState) -> AgentState:
        message = state["mensagem"]
        fallbacks = list(state.get("fallbacks", []))
        if client is not None:
            try:
                return {
                    "classificacao": client.classify_intent(message),
                    "modo_classificacao": "gemini",
                    "fallbacks": fallbacks,
                }
            except Exception as exc:
                fallbacks.append(
                    f"classificação Gemini: {type(exc).__name__}: {exc}"
                )
        return {
            "classificacao": classify_local(message),
            "modo_classificacao": "local_deterministic",
            "fallbacks": fallbacks,
        }

    return classify


def classify(state: AgentState) -> AgentState:
    """Compatibilidade pública: executa o classificador local."""
    message = state["mensagem"].lower()
    return {
        "classificacao": classify_local(message),
        "modo_classificacao": "local_deterministic",
        "fallbacks": list(state.get("fallbacks", [])),
    }


def conta_corrente(state: AgentState) -> AgentState:
    return {"resposta_agente": "Agente conta_corrente: consultei regras de conta e pagamentos."}


def cartao_credito(state: AgentState) -> AgentState:
    platinum = "platinum" in state["mensagem"].lower()
    status = (
        "solicitação pausada até aprovação humana (HITL)"
        if platinum
        else "consulta de regras concluída"
    )
    return {
        "resposta_agente": f"Agente cartao_credito: {status}.",
        "requer_aprovacao_humana": platinum,
    }


def suporte(state: AgentState) -> AgentState:
    return {"resposta_agente": "Agente suporte: encaminho o atendimento pelos canais e SLAs oficiais."}


def route(state: AgentState) -> str:
    return state["classificacao"]


def synthesize(state: AgentState) -> AgentState:
    return {"resposta_final": f"[{state['classificacao']}] {state['resposta_agente']}"}


def build_graph(llm_mode: str = "local", gemini: Any | None = None):
    requested_mode = resolve_mode(llm_mode)
    client = gemini if requested_mode == "gemini" else None
    initialization_fallback: list[str] = []
    if requested_mode == "gemini" and client is None:
        client, reason = GeminiIntegration.create_from_env("gemini")
        if reason:
            initialization_fallback.append(f"inicialização Gemini: {reason}")

    graph = StateGraph(AgentState)
    classifier = make_classifier(client)

    def classify_with_initialization(state: AgentState) -> AgentState:
        return classifier({**state, "fallbacks": initialization_fallback})

    graph.add_node("classificar", classify_with_initialization)
    graph.add_node("conta_corrente", conta_corrente)
    graph.add_node("cartao_credito", cartao_credito)
    graph.add_node("suporte", suporte)
    graph.add_node("sintese", synthesize)
    graph.add_edge(START, "classificar")
    graph.add_conditional_edges("classificar", route)
    graph.add_edge("conta_corrente", "sintese")
    graph.add_edge("cartao_credito", "sintese")
    graph.add_edge("suporte", "sintese")
    graph.add_edge("sintese", END)
    return graph.compile()


def draw_mermaid() -> str:
    return """graph TD\n    START --> classificar\n    classificar -->|conta_corrente| conta_corrente\n    classificar -->|cartao_credito| cartao_credito\n    classificar -->|suporte| suporte\n    conta_corrente --> sintese\n    cartao_credito --> sintese\n    suporte --> sintese\n    sintese --> END\n"""


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("auto", "local", "gemini"), default="auto")
    args = parser.parse_args()
    app = build_graph(llm_mode=args.mode)
    for message in ("Como faço um Pix?", "Qual a regra do cartão Platinum?", "Quais canais de suporte existem?"):
        result = app.invoke({"mensagem": message})
        print(
            result["classificacao"],
            f"({result['modo_classificacao']})",
            "->",
            result["resposta_final"],
        )
        for fallback in result.get("fallbacks", []):
            print("Fallback:", fallback)
    print(draw_mermaid())

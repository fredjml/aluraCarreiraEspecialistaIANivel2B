"""Protótipo multiagente local, com LangGraph opcional e roteamento exato."""
from __future__ import annotations

from typing import TypedDict

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


def classify(state: AgentState) -> AgentState:
    message = state["mensagem"].lower()
    if any(word in message for word in ("cartão", "cartao", "fatura", "platinum", "anuidade")):
        intent = "cartao_credito"
    elif any(word in message for word in ("conta", "pix", "ted", "saldo", "empréstimo", "emprestimo")):
        intent = "conta_corrente"
    else:
        intent = "suporte"
    return {"classificacao": intent}


def conta_corrente(state: AgentState) -> AgentState:
    return {"resposta_agente": "Agente conta_corrente: consultei regras de conta e pagamentos."}


def cartao_credito(state: AgentState) -> AgentState:
    return {"resposta_agente": "Agente cartao_credito: consultei regras de cartão; Platinum exige análise e pode requerer HITL."}


def suporte(state: AgentState) -> AgentState:
    return {"resposta_agente": "Agente suporte: encaminho o atendimento pelos canais e SLAs oficiais."}


def route(state: AgentState) -> str:
    return state["classificacao"]


def synthesize(state: AgentState) -> AgentState:
    return {"resposta_final": f"[{state['classificacao']}] {state['resposta_agente']}"}


def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("classificar", classify)
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
    app = build_graph()
    for message in ("Como faço um Pix?", "Qual a regra do cartão Platinum?", "Quais canais de suporte existem?"):
        result = app.invoke({"mensagem": message})
        print(result["classificacao"], "->", result["resposta_final"])
    print(draw_mermaid())

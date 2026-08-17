"""Validação inicial da conexão do GeoAI Mentor com a API da OpenAI."""

from __future__ import annotations

import os
import sys

from dotenv import load_dotenv
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI


PERGUNTAS = [
    (
        "Eu sou geofísico e quero migrar para a área de dados. "
        "Qual linguagem de programação devo aprender primeiro?"
    ),
    (
        "E que tipo de projeto de portfólio eu poderia criar usando "
        "essa linguagem?"
    ),
]

memoria_sessoes: dict[str, InMemoryChatMessageHistory] = {}


def carregar_configuracao() -> None:
    """Carrega o arquivo .env e valida as configurações obrigatórias."""
    load_dotenv()

    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError(
            "OPENAI_API_KEY não configurada. Preencha o arquivo .env antes "
            "de iniciar o GeoAI Mentor."
        )


def criar_modelo() -> ChatOpenAI:
    """Cria o cliente do modelo após validar a configuração local."""
    carregar_configuracao()
    return ChatOpenAI(model="gpt-5.6-sol", temperature=0.7)


def criar_chain(modelo: ChatOpenAI) -> Runnable:
    """Cria a cadeia LCEL que define a personalidade do GeoAI Mentor."""
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Você é o 'GeoAI Mentor', um assistente especializado em "
                "ajudar geocientistas a migrar para a área de Ciência de "
                "Dados. Seja amigável e didático.",
            ),
            ("placeholder", "{historico}"),
            ("human", "{query}"),
        ]
    )

    return prompt | modelo | StrOutputParser()


def obter_historico_por_sessao(session_id: str) -> InMemoryChatMessageHistory:
    """Obtém a instância única de histórico associada a uma sessão."""
    if session_id not in memoria_sessoes:
        memoria_sessoes[session_id] = InMemoryChatMessageHistory()

    return memoria_sessoes[session_id]


def criar_cadeia_com_memoria(chain: Runnable) -> RunnableWithMessageHistory:
    """Envelopa a cadeia LCEL com gerenciamento de histórico por sessão."""
    return RunnableWithMessageHistory(
        runnable=chain,
        get_session_history=obter_historico_por_sessao,
        input_messages_key="query",
        history_messages_key="historico",
    )


def executar_perguntas(
    cadeia_com_memoria: RunnableWithMessageHistory,
    perguntas: list[str],
    session_id: str,
) -> None:
    """Envia as perguntas compartilhando o histórico da mesma sessão."""
    for pergunta in perguntas:
        resposta = cadeia_com_memoria.invoke(
            {"query": pergunta},
            config={"configurable": {"session_id": session_id}},
        )
        print(f"\nPergunta: {pergunta}")
        print(f"Resposta: {resposta}")


def main() -> None:
    """Executa as duas perguntas de validação da conexão com a API."""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    modelo = criar_modelo()
    chain = criar_chain(modelo)
    cadeia_com_memoria = criar_cadeia_com_memoria(chain)
    executar_perguntas(cadeia_com_memoria, PERGUNTAS, session_id="sessao_demo")


if __name__ == "__main__":
    main()

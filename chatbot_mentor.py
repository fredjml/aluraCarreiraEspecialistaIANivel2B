"""Validação inicial da conexão do GeoAI Mentor com a API da OpenAI."""

from __future__ import annotations

import os

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
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


def executar_perguntas(chain: Runnable, perguntas: list[str]) -> None:
    """Envia cada pergunta pela cadeia, ainda sem preencher o histórico."""
    for pergunta in perguntas:
        resposta = chain.invoke({"historico": [], "query": pergunta})
        print(f"\nPergunta: {pergunta}")
        print(f"Resposta: {resposta}")


def main() -> None:
    """Executa as duas perguntas de validação da conexão com a API."""
    modelo = criar_modelo()
    chain = criar_chain(modelo)
    executar_perguntas(chain, PERGUNTAS)


if __name__ == "__main__":
    main()

"""Testes do adaptador LangChain com histórico persistente e sem OpenAI."""

import pytest
from langchain_core.runnables import RunnableLambda

from geoai_mentor.infrastructure.langchain_gateway import LangChainMentorGateway
from geoai_mentor.infrastructure.sqlite_repository import SQLiteConversationRepository


def criar_gateway_fake() -> tuple[LangChainMentorGateway, SQLiteConversationRepository]:
    repository = SQLiteConversationRepository(":memory:")
    gateway = LangChainMentorGateway(
        RunnableLambda(
            lambda entrada: f"historico={len(entrada['historico'])}; query={entrada['query']}"
        ),
        repository,
    )
    return gateway, repository


def test_gateway_preserva_contexto_e_isola_conversas() -> None:
    gateway, repository = criar_gateway_fake()
    primeira = gateway.responder("conversa-a", "Primeira pergunta")
    segunda = gateway.responder("conversa-a", "Segunda pergunta")
    independente = gateway.responder("conversa-b", "Nova conversa")
    assert "historico=0" in primeira
    assert "historico=2" in segunda
    assert "historico=0" in independente
    assert len(repository.listar_mensagens("conversa-a")) == 4


def test_gateway_limpa_somente_a_conversa_informada() -> None:
    gateway, repository = criar_gateway_fake()
    gateway.responder("conversa-a", "Pergunta A")
    gateway.responder("conversa-b", "Pergunta B")
    gateway.limpar("conversa-a")
    assert repository.listar_mensagens("conversa-a") == []
    assert len(repository.listar_mensagens("conversa-b")) == 2


def test_gateway_nao_persiste_pergunta_quando_pipeline_falha() -> None:
    repository = SQLiteConversationRepository(":memory:")
    gateway = LangChainMentorGateway(
        RunnableLambda(lambda entrada: (_ for _ in ()).throw(RuntimeError("falha"))),
        repository,
    )
    with pytest.raises(RuntimeError, match="falha"):
        gateway.responder("conversa-a", "Pergunta")
    assert repository.listar_mensagens("conversa-a") == []


def test_gateway_inclui_fontes_recuperadas_no_contexto() -> None:
    class RetrieverFake:
        def buscar(self, query, limite=3):
            from geoai_mentor.domain.models import KnowledgeChunk
            return [KnowledgeChunk("fonte.md", "Evidência controlada", 1.0)]

    repository = SQLiteConversationRepository(":memory:")
    gateway = LangChainMentorGateway(
        RunnableLambda(lambda entrada: entrada["contexto"]),
        repository,
        RetrieverFake(),
    )

    resposta = gateway.responder("conversa-a", "Pergunta")

    assert "Fonte: fonte.md" in resposta
    assert "Evidência controlada" in resposta


def test_gateway_sinaliza_contexto_sem_evidencia() -> None:
    class RetrieverVazio:
        def buscar(self, query, limite=3):
            return []

    repository = SQLiteConversationRepository(":memory:")
    gateway = LangChainMentorGateway(
        RunnableLambda(lambda entrada: entrada["contexto"]),
        repository,
        RetrieverVazio(),
    )

    assert "Nenhuma evidência" in gateway.responder("conversa-a", "Pergunta")

"""Testes unitários do serviço de aplicação."""

from dataclasses import dataclass, field

import pytest

from geoai_mentor.application.mentor_service import MentorService
from geoai_mentor.domain.errors import EmptyQuestionError, MentorUnavailableError


@dataclass
class FakeGateway:
    resposta: str = "resposta de teste"
    chamadas: list[tuple[str, str]] = field(default_factory=list)
    limpezas: list[str] = field(default_factory=list)
    falha: Exception | None = None

    def responder(self, session_id: str, mensagem: str) -> str:
        self.chamadas.append((session_id, mensagem))
        if self.falha:
            raise self.falha
        return self.resposta

    def limpar(self, session_id: str) -> None:
        self.limpezas.append(session_id)


def test_servico_encaminha_mensagem_normalizada() -> None:
    gateway = FakeGateway()
    service = MentorService(gateway)

    assert service.enviar_mensagem("sessao-a", "  minha pergunta  ") == "resposta de teste"
    assert gateway.chamadas == [("sessao-a", "minha pergunta")]


def test_servico_rejeita_pergunta_vazia() -> None:
    service = MentorService(FakeGateway())

    with pytest.raises(EmptyQuestionError, match="vazia"):
        service.enviar_mensagem("sessao-a", "   ")


def test_servico_converte_falha_tecnica_em_erro_seguro() -> None:
    service = MentorService(FakeGateway(falha=RuntimeError("segredo interno")))

    with pytest.raises(MentorUnavailableError) as erro:
        service.enviar_mensagem("sessao-a", "pergunta")
    assert "segredo interno" not in str(erro.value)


def test_servico_rejeita_identificador_vazio() -> None:
    service = MentorService(FakeGateway())

    with pytest.raises(ValueError, match="session_id"):
        service.enviar_mensagem("   ", "pergunta")


def test_servico_preserva_erro_de_dominio() -> None:
    falha = EmptyQuestionError("erro conhecido")
    service = MentorService(FakeGateway(falha=falha))

    with pytest.raises(EmptyQuestionError, match="erro conhecido"):
        service.enviar_mensagem("sessao-a", "pergunta")


def test_servico_limpa_conversa_existente() -> None:
    gateway = FakeGateway()
    service = MentorService(gateway)

    service.limpar_conversa("sessao-a")

    assert gateway.limpezas == ["sessao-a"]


def test_servico_ignora_limpeza_sem_identificador() -> None:
    gateway = FakeGateway()
    service = MentorService(gateway)

    service.limpar_conversa("")

    assert gateway.limpezas == []

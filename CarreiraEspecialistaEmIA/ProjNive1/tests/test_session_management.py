"""Testes dos casos de uso de gerenciamento de conversas."""

import pytest

from geoai_mentor.application.mentor_service import MentorService
from geoai_mentor.infrastructure.sqlite_repository import SQLiteConversationRepository


class FakeGateway:
    def responder(self, session_id: str, mensagem: str) -> str:
        return "resposta"

    def limpar(self, session_id: str) -> None:
        return None


def criar_servico() -> MentorService:
    return MentorService(FakeGateway(), SQLiteConversationRepository(":memory:"))


def test_servico_cria_lista_reabre_renomeia_e_exclui() -> None:
    service = criar_servico()
    service.criar_conversa("conversa-a", "  Minha conversa  ")

    assert service.listar_conversas()[0].title == "Minha conversa"
    assert service.obter_mensagens("conversa-a") == []

    service.renomear_conversa("conversa-a", "Novo título")
    assert service.listar_conversas()[0].title == "Novo título"

    service.excluir_conversa("conversa-a")
    assert service.listar_conversas() == []


def test_servico_rejeita_titulo_vazio() -> None:
    service = criar_servico()
    service.criar_conversa("conversa-a")

    with pytest.raises(ValueError, match="título"):
        service.renomear_conversa("conversa-a", "   ")


def test_gerenciamento_exige_repositorio() -> None:
    service = MentorService(FakeGateway())

    with pytest.raises(RuntimeError, match="não configurado"):
        service.listar_conversas()


def test_servico_aplica_retencao_e_cria_backup() -> None:
    repository = SQLiteConversationRepository(":memory:")
    service = MentorService(FakeGateway(), repository)
    repository.salvar_interacao("conversa-a", "Pergunta", "Resposta")
    destino = "data/test_service_backup.db"
    from pathlib import Path
    Path(destino).unlink(missing_ok=True)
    try:
        assert service.aplicar_retencao(90) == 0
        assert service.criar_backup(destino).endswith("test_service_backup.db")
    finally:
        Path(destino).unlink(missing_ok=True)


@pytest.mark.parametrize("dias", [0, -1])
def test_servico_rejeita_retencao_invalida(dias) -> None:
    with pytest.raises(ValueError, match="retenção"):
        criar_servico().aplicar_retencao(dias)


def test_servico_rejeita_destino_de_backup_vazio() -> None:
    with pytest.raises(ValueError, match="backup"):
        criar_servico().criar_backup("   ")

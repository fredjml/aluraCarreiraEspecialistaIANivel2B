"""Testes de persistência e transação do repositório SQLite."""

import sqlite3
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from geoai_mentor.infrastructure.sqlite_repository import SQLiteConversationRepository


def test_interacao_sobrevive_a_nova_instancia() -> None:
    banco = Path("data/test_geoai_repository.db")
    banco.unlink(missing_ok=True)
    try:
        primeiro = SQLiteConversationRepository(str(banco))
        primeiro.salvar_interacao("conversa-a", "Pergunta", "Resposta")
        primeiro.fechar()
        segundo = SQLiteConversationRepository(str(banco))
        mensagens = segundo.listar_mensagens("conversa-a")
        segundo.fechar()
        assert [(m.role, m.content) for m in mensagens] == [
            ("user", "Pergunta"),
            ("assistant", "Resposta"),
        ]
    finally:
        banco.unlink(missing_ok=True)


def test_conversas_ficam_isoladas() -> None:
    repository = SQLiteConversationRepository(":memory:")
    repository.salvar_interacao("conversa-a", "A", "Resposta A")
    repository.salvar_interacao("conversa-b", "B", "Resposta B")
    assert [m.content for m in repository.listar_mensagens("conversa-a")] == ["A", "Resposta A"]
    assert [m.content for m in repository.listar_mensagens("conversa-b")] == ["B", "Resposta B"]


def test_limpeza_remove_conversa_por_cascata() -> None:
    repository = SQLiteConversationRepository(":memory:")
    repository.salvar_interacao("conversa-a", "Pergunta", "Resposta")
    repository.limpar_conversa("conversa-a")
    assert repository.listar_mensagens("conversa-a") == []


def test_interacao_e_atomica_quando_segunda_mensagem_falha() -> None:
    repository = SQLiteConversationRepository(":memory:")
    repository._connection.execute(
        """
        CREATE TRIGGER falhar_resposta BEFORE INSERT ON messages
        WHEN NEW.role = 'assistant'
        BEGIN SELECT RAISE(ABORT, 'falha simulada'); END;
        """
    )
    with pytest.raises(sqlite3.IntegrityError):
        repository.salvar_interacao("conversa-a", "Pergunta", "Resposta")
    assert repository.listar_mensagens("conversa-a") == []


def test_ciclo_completo_de_gerenciamento_de_conversas() -> None:
    repository = SQLiteConversationRepository(":memory:")

    criada = repository.criar_conversa("conversa-a", "Plano de carreira")
    assert criada.title == "Plano de carreira"
    assert [c.id for c in repository.listar_conversas()] == ["conversa-a"]

    repository.renomear_conversa("conversa-a", "Projetos de portfólio")
    assert repository.listar_conversas()[0].title == "Projetos de portfólio"

    repository.limpar_conversa("conversa-a")
    assert repository.listar_conversas() == []


def test_renomear_conversa_inexistente_falha() -> None:
    repository = SQLiteConversationRepository(":memory:")

    with pytest.raises(KeyError, match="não encontrada"):
        repository.renomear_conversa("inexistente", "Título")


def test_primeira_interacao_cria_titulo_automatico() -> None:
    repository = SQLiteConversationRepository(":memory:")
    repository.salvar_interacao("conversa-a", "Como começo em Python?", "Resposta")

    assert repository.listar_conversas()[0].title == "Como começo em Python?"


def test_backup_preserva_conversas_e_mensagens() -> None:
    repository = SQLiteConversationRepository(":memory:")
    repository.salvar_interacao("conversa-a", "Pergunta", "Resposta")
    destino = Path("data/test_backup_geoai.db")
    destino.unlink(missing_ok=True)
    try:
        caminho = repository.criar_backup(str(destino))
        restaurado = SQLiteConversationRepository(caminho)
        assert [m.content for m in restaurado.listar_mensagens("conversa-a")] == [
            "Pergunta", "Resposta"
        ]
        restaurado.fechar()
    finally:
        destino.unlink(missing_ok=True)


def test_retencao_remove_somente_conversa_expirada() -> None:
    repository = SQLiteConversationRepository(":memory:")
    repository.salvar_interacao("antiga", "A", "RA")
    repository.salvar_interacao("recente", "B", "RB")
    antiga = (datetime.now(timezone.utc) - timedelta(days=120)).isoformat()
    repository._connection.execute(
        "UPDATE conversations SET updated_at = ? WHERE id = 'antiga'", (antiga,)
    )

    removidas = repository.expirar_conversas(
        datetime.now(timezone.utc) - timedelta(days=90)
    )

    assert removidas == 1
    assert [c.id for c in repository.listar_conversas()] == ["recente"]


def test_gravacoes_concorrentes_permanecem_integras() -> None:
    repository = SQLiteConversationRepository(":memory:")

    with ThreadPoolExecutor(max_workers=4) as executor:
        list(
            executor.map(
                lambda indice: repository.salvar_interacao(
                    f"conversa-{indice}", f"P{indice}", f"R{indice}"
                ),
                range(12),
            )
        )

    assert len(repository.listar_conversas()) == 12
    assert all(
        len(repository.listar_mensagens(f"conversa-{indice}")) == 2
        for indice in range(12)
    )

"""Testes da configuração centralizada."""

import pytest

from geoai_mentor.config.settings import Settings
from geoai_mentor.domain.errors import ConfigurationError


def test_settings_le_valores_do_ambiente(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "chave-de-teste")
    monkeypatch.setenv("OPENAI_MODEL", "modelo-teste")
    monkeypatch.setenv("OPENAI_TEMPERATURE", "0.4")
    monkeypatch.setenv("GEOAI_DATABASE_PATH", "banco/teste.db")
    monkeypatch.setenv("GEOAI_KNOWLEDGE_PATH", "base/teste")
    monkeypatch.setenv("OPENAI_REQUEST_TIMEOUT", "12.5")
    monkeypatch.setenv("OPENAI_MAX_OUTPUT_TOKENS", "500")
    monkeypatch.setenv("GEOAI_RETENTION_DAYS", "30")

    settings = Settings.from_env()

    assert settings.openai_api_key == "chave-de-teste"
    assert settings.model_name == "modelo-teste"
    assert settings.temperature == 0.4
    assert settings.database_path == "banco/teste.db"
    assert settings.knowledge_path == "base/teste"
    assert settings.request_timeout == 12.5
    assert settings.max_output_tokens == 500
    assert settings.retention_days == 30


def test_settings_rejeita_chave_ausente(monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setattr("geoai_mentor.config.settings.load_dotenv", lambda: None)

    with pytest.raises(ConfigurationError, match="OPENAI_API_KEY"):
        Settings.from_env()


def test_settings_rejeita_caminho_de_banco_vazio(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "chave-de-teste")
    monkeypatch.setenv("GEOAI_DATABASE_PATH", "   ")

    with pytest.raises(ConfigurationError, match="GEOAI_DATABASE_PATH"):
        Settings.from_env()


def test_settings_rejeita_caminho_de_conhecimento_vazio(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "chave-de-teste")
    monkeypatch.setenv("GEOAI_KNOWLEDGE_PATH", "   ")

    with pytest.raises(ConfigurationError, match="GEOAI_KNOWLEDGE_PATH"):
        Settings.from_env()


@pytest.mark.parametrize(
    ("variavel", "valor"),
    [
        ("OPENAI_REQUEST_TIMEOUT", "texto"),
        ("OPENAI_MAX_OUTPUT_TOKENS", "0"),
        ("GEOAI_RETENTION_DAYS", "-1"),
    ],
)
def test_settings_rejeita_limites_operacionais_invalidos(monkeypatch, variavel, valor) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "chave-de-teste")
    monkeypatch.setenv(variavel, valor)

    with pytest.raises(ConfigurationError, match="Limites operacionais"):
        Settings.from_env()


@pytest.mark.parametrize("valor", ["texto", "-0.1", "2.1"])
def test_settings_rejeita_temperatura_invalida(monkeypatch, valor) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "chave-de-teste")
    monkeypatch.setenv("OPENAI_TEMPERATURE", valor)

    with pytest.raises(ConfigurationError, match="OPENAI_TEMPERATURE"):
        Settings.from_env()

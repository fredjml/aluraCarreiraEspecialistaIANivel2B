"""Leitura centralizada das configurações do GeoAI Mentor."""

import os
from dataclasses import dataclass

from dotenv import load_dotenv

from geoai_mentor.domain.errors import ConfigurationError


@dataclass(frozen=True, slots=True)
class Settings:
    """Configurações necessárias para construir o back-end."""

    openai_api_key: str
    model_name: str = "gpt-5.6-sol"
    temperature: float = 0.7
    database_path: str = "data/geoai_mentor.db"
    knowledge_path: str = "knowledge_base"
    request_timeout: float = 30.0
    max_output_tokens: int = 1200
    retention_days: int = 90

    @classmethod
    def from_env(cls) -> "Settings":
        """Carrega o .env e valida os valores obrigatórios."""
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if not api_key:
            raise ConfigurationError(
                "OPENAI_API_KEY não configurada. Preencha o arquivo .env antes "
                "de iniciar o GeoAI Mentor."
            )
        model_name = os.getenv("OPENAI_MODEL", "gpt-5.6-sol").strip()
        try:
            temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
        except ValueError as exc:
            raise ConfigurationError("OPENAI_TEMPERATURE deve ser um número.") from exc
        if not 0 <= temperature <= 2:
            raise ConfigurationError("OPENAI_TEMPERATURE deve estar entre 0 e 2.")
        database_path = os.getenv(
            "GEOAI_DATABASE_PATH", "data/geoai_mentor.db"
        ).strip()
        if not database_path:
            raise ConfigurationError("GEOAI_DATABASE_PATH não pode estar vazio.")
        knowledge_path = os.getenv("GEOAI_KNOWLEDGE_PATH", "knowledge_base").strip()
        if not knowledge_path:
            raise ConfigurationError("GEOAI_KNOWLEDGE_PATH não pode estar vazio.")
        try:
            request_timeout = float(os.getenv("OPENAI_REQUEST_TIMEOUT", "30"))
            max_output_tokens = int(os.getenv("OPENAI_MAX_OUTPUT_TOKENS", "1200"))
            retention_days = int(os.getenv("GEOAI_RETENTION_DAYS", "90"))
        except ValueError as exc:
            raise ConfigurationError("Limites operacionais devem ser numéricos.") from exc
        if request_timeout <= 0 or max_output_tokens <= 0 or retention_days <= 0:
            raise ConfigurationError("Limites operacionais devem ser maiores que zero.")
        return cls(
            api_key,
            model_name,
            temperature,
            database_path,
            knowledge_path,
            request_timeout,
            max_output_tokens,
            retention_days,
        )

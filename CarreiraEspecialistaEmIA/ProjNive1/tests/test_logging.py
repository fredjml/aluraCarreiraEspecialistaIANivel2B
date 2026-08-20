"""Testes de privacidade dos logs operacionais."""

import logging

from geoai_mentor.config.logging import RedactingFilter, configurar_logging


def test_filtro_remove_chave_e_variavel_sensivel() -> None:
    record = logging.LogRecord(
        "geoai", logging.ERROR, __file__, 1,
        "falha sk-chave123 OPENAI_API_KEY=segredo", (), None,
    )

    assert RedactingFilter().filter(record)
    assert "sk-chave123" not in record.msg
    assert "segredo" not in record.msg
    assert record.msg.count("[REDACTED]") == 2


def test_configuracao_instala_filtro() -> None:
    configurar_logging()

    assert any(
        isinstance(filtro, RedactingFilter)
        for handler in logging.getLogger().handlers
        for filtro in handler.filters
    )

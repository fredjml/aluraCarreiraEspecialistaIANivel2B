"""Configuração de logs operacionais sem conteúdo conversacional."""

import logging
import re


PADROES_SENSIVEIS = (
    re.compile(r"sk-[A-Za-z0-9_-]+"),
    re.compile(r"OPENAI_API_KEY\s*[=:]\s*\S+", re.IGNORECASE),
)


class RedactingFilter(logging.Filter):
    """Remove formatos conhecidos de credenciais antes da emissão do log."""

    def filter(self, record: logging.LogRecord) -> bool:
        mensagem = record.getMessage()
        for padrao in PADROES_SENSIVEIS:
            mensagem = padrao.sub("[REDACTED]", mensagem)
        record.msg = mensagem
        record.args = ()
        return True


def configurar_logging(level: int = logging.INFO) -> None:
    handler = logging.StreamHandler()
    handler.addFilter(RedactingFilter())
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
    logging.basicConfig(level=level, handlers=[handler], force=True)

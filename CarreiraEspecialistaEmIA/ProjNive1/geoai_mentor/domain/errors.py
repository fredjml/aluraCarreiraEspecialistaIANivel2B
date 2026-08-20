"""Erros estáveis expostos pelas camadas internas."""


class MentorError(Exception):
    """Erro conhecido que pode ser convertido em mensagem segura."""


class ConfigurationError(MentorError):
    """Configuração obrigatória ausente ou inválida."""


class EmptyQuestionError(MentorError):
    """A pergunta recebida não possui conteúdo."""


class MentorUnavailableError(MentorError):
    """O provedor de IA não pôde responder no momento."""

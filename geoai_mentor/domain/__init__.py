"""Modelos, contratos e erros do domínio."""

from geoai_mentor.domain.errors import ConfigurationError, EmptyQuestionError, MentorError, MentorUnavailableError
from geoai_mentor.domain.models import Message
from geoai_mentor.domain.ports import ConversationRepository, MentorGateway

__all__ = ["ConfigurationError", "ConversationRepository", "EmptyQuestionError", "MentorError", "MentorGateway", "MentorUnavailableError", "Message"]

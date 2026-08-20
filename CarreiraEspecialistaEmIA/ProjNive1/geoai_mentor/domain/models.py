"""Modelos persistentes independentes da tecnologia de armazenamento."""

from dataclasses import dataclass
from datetime import datetime
from typing import Literal


MessageRole = Literal["user", "assistant"]


@dataclass(frozen=True, slots=True)
class Message:
    """Mensagem armazenada em uma conversa."""

    role: MessageRole
    content: str
    created_at: datetime


@dataclass(frozen=True, slots=True)
class Conversation:
    """Metadados de uma conversa persistida."""

    id: str
    title: str
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True, slots=True)
class KnowledgeChunk:
    """Trecho recuperado de uma fonte local aprovada."""

    source: str
    content: str
    score: float

"""Adaptadores de tecnologias externas."""

from geoai_mentor.infrastructure.langchain_gateway import LangChainMentorGateway
from geoai_mentor.infrastructure.sqlite_repository import SQLiteConversationRepository

__all__ = ["LangChainMentorGateway", "SQLiteConversationRepository"]

"""Composição das dependências concretas da aplicação."""

from geoai_mentor.application.mentor_service import MentorService
from geoai_mentor.config.settings import Settings
from geoai_mentor.infrastructure.langchain_gateway import LangChainMentorGateway
from geoai_mentor.infrastructure.local_knowledge import LocalMarkdownKnowledgeRetriever
from geoai_mentor.infrastructure.sqlite_repository import SQLiteConversationRepository


def criar_mentor_service(settings: Settings | None = None) -> MentorService:
    """Monta o serviço com o adaptador LangChain/OpenAI."""
    configuracao = settings or Settings.from_env()
    repository = SQLiteConversationRepository(configuracao.database_path)
    retriever = LocalMarkdownKnowledgeRetriever(configuracao.knowledge_path)
    gateway = LangChainMentorGateway.from_settings(configuracao, repository, retriever)
    return MentorService(gateway, repository)

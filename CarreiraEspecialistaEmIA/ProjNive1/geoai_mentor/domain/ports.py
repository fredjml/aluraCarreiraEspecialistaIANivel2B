"""Contratos independentes das tecnologias externas."""

from datetime import datetime
from typing import Protocol

from geoai_mentor.domain.models import Conversation, KnowledgeChunk, Message


class MentorGateway(Protocol):
    """Porta utilizada pelo serviço para conversar e limpar contexto."""

    def responder(self, session_id: str, mensagem: str) -> str: ...

    def limpar(self, session_id: str) -> None: ...


class ConversationRepository(Protocol):
    """Contrato da fonte oficial do histórico de conversas."""

    def listar_mensagens(self, conversation_id: str) -> list[Message]: ...

    def salvar_interacao(
        self,
        conversation_id: str,
        pergunta: str,
        resposta: str,
    ) -> None: ...

    def limpar_conversa(self, conversation_id: str) -> None: ...

    def criar_conversa(self, conversation_id: str, title: str) -> Conversation: ...

    def listar_conversas(self) -> list[Conversation]: ...

    def renomear_conversa(self, conversation_id: str, title: str) -> None: ...

    def expirar_conversas(self, antes_de: datetime) -> int: ...

    def criar_backup(self, destination_path: str) -> str: ...


class KnowledgeRetriever(Protocol):
    """Contrato para recuperação em fontes previamente autorizadas."""

    def buscar(self, query: str, limite: int = 3) -> list[KnowledgeChunk]: ...

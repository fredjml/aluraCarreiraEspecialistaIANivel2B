"""Serviço de aplicação consumido por qualquer interface."""

from datetime import datetime, timedelta, timezone

from geoai_mentor.domain.errors import EmptyQuestionError, MentorError, MentorUnavailableError
from geoai_mentor.domain.models import Conversation, Message
from geoai_mentor.domain.ports import ConversationRepository, MentorGateway


class MentorService:
    """Coordena os casos de uso sem conhecer Streamlit ou LangChain."""

    def __init__(
        self,
        gateway: MentorGateway,
        repository: ConversationRepository | None = None,
    ) -> None:
        self._gateway = gateway
        self._repository = repository

    def enviar_mensagem(self, session_id: str, mensagem: str) -> str:
        """Valida e envia uma mensagem ao back-end conversacional."""
        pergunta = mensagem.strip()
        if not pergunta:
            raise EmptyQuestionError("A pergunta não pode estar vazia.")
        if not session_id.strip():
            raise ValueError("session_id não pode estar vazio.")
        try:
            return self._gateway.responder(session_id, pergunta)
        except MentorError:
            raise
        except Exception as exc:
            raise MentorUnavailableError(
                "Não consegui consultar o modelo agora. Tente novamente em instantes."
            ) from exc

    def limpar_conversa(self, session_id: str) -> None:
        """Solicita a remoção do contexto temporário da conversa."""
        if session_id:
            self._gateway.limpar(session_id)

    def criar_conversa(self, session_id: str, titulo: str = "Nova conversa") -> Conversation:
        repository = self._obter_repository()
        return repository.criar_conversa(session_id, titulo.strip() or "Nova conversa")

    def listar_conversas(self) -> list[Conversation]:
        return self._obter_repository().listar_conversas()

    def obter_mensagens(self, session_id: str) -> list[Message]:
        return self._obter_repository().listar_mensagens(session_id)

    def renomear_conversa(self, session_id: str, titulo: str) -> None:
        titulo_normalizado = titulo.strip()
        if not titulo_normalizado:
            raise ValueError("O título não pode estar vazio.")
        self._obter_repository().renomear_conversa(session_id, titulo_normalizado)

    def excluir_conversa(self, session_id: str) -> None:
        self._obter_repository().limpar_conversa(session_id)

    def aplicar_retencao(self, retention_days: int) -> int:
        if retention_days <= 0:
            raise ValueError("O período de retenção deve ser maior que zero.")
        limite = datetime.now(timezone.utc) - timedelta(days=retention_days)
        return self._obter_repository().expirar_conversas(limite)

    def criar_backup(self, destination_path: str) -> str:
        if not destination_path.strip():
            raise ValueError("O destino do backup não pode estar vazio.")
        return self._obter_repository().criar_backup(destination_path)

    def _obter_repository(self) -> ConversationRepository:
        if self._repository is None:
            raise RuntimeError("Gerenciamento de conversas não configurado.")
        return self._repository

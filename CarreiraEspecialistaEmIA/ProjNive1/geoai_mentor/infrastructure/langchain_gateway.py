"""Adaptador LangChain/OpenAI do GeoAI Mentor."""

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
from langchain_openai import ChatOpenAI

from geoai_mentor.config.settings import Settings
from geoai_mentor.domain.models import Message
from geoai_mentor.domain.ports import ConversationRepository, KnowledgeRetriever


PROMPT_SISTEMA = (
    "Você é o 'GeoAI Mentor', um assistente especializado em ajudar "
    "geocientistas a migrar para a área de Ciência de Dados. Seja amigável e didático."
)


def criar_pipeline(modelo: Runnable) -> Runnable:
    """Cria a cadeia LCEL sem gerenciar estado ou interface."""
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", PROMPT_SISTEMA),
            ("system", "Use a base abaixo quando ela trouxer evidência. Cite os nomes das fontes. Se a base estiver vazia ou não responder à pergunta, diga claramente que não encontrou evidência na base aprovada.\n\nBase aprovada:\n{contexto}"),
            ("placeholder", "{historico}"),
            ("human", "{query}"),
        ]
    )
    return prompt | modelo | StrOutputParser()


class LangChainMentorGateway:
    """Implementa a conversa usando LangChain e um repositório persistente."""

    def __init__(
        self,
        chain: Runnable,
        repository: ConversationRepository,
        retriever: KnowledgeRetriever | None = None,
    ) -> None:
        self._chain = chain
        self._repository = repository
        self._retriever = retriever

    @classmethod
    def from_settings(
        cls,
        settings: Settings,
        repository: ConversationRepository,
        retriever: KnowledgeRetriever | None = None,
    ) -> "LangChainMentorGateway":
        """Constrói o adaptador real a partir da configuração validada."""
        modelo = ChatOpenAI(
            api_key=settings.openai_api_key,
            model=settings.model_name,
            temperature=settings.temperature,
            timeout=settings.request_timeout,
            max_tokens=settings.max_output_tokens,
        )
        return cls(criar_pipeline(modelo), repository, retriever)

    @staticmethod
    def _converter_historico(mensagens: list[Message]) -> list[BaseMessage]:
        """Converte modelos persistidos em mensagens aceitas pelo LangChain."""
        historico: list[BaseMessage] = []
        for mensagem in mensagens:
            if mensagem.role == "user":
                historico.append(HumanMessage(content=mensagem.content))
            else:
                historico.append(AIMessage(content=mensagem.content))
        return historico

    def responder(self, session_id: str, mensagem: str) -> str:
        """Invoca a cadeia com o contexto associado à sessão."""
        mensagens = self._repository.listar_mensagens(session_id)
        trechos = self._retriever.buscar(mensagem) if self._retriever else []
        contexto = "\n\n".join(
            f"Fonte: {trecho.source}\n{trecho.content}" for trecho in trechos
        ) or "Nenhuma evidência recuperada da base aprovada."
        resposta = self._chain.invoke(
            {
                "query": mensagem,
                "historico": self._converter_historico(mensagens),
                "contexto": contexto,
            }
        )
        self._repository.salvar_interacao(session_id, mensagem, resposta)
        return resposta

    def limpar(self, session_id: str) -> None:
        """Remove a conversa persistida e todas as mensagens associadas."""
        self._repository.limpar_conversa(session_id)

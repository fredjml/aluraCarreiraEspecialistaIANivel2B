"""Front-end Streamlit do GeoAI Mentor."""

import logging
from uuid import uuid4

import streamlit as st

from geoai_mentor.application.mentor_service import MentorService
from geoai_mentor.bootstrap import criar_mentor_service
from geoai_mentor.domain.errors import MentorError


LOGGER = logging.getLogger(__name__)
MENSAGEM_INICIAL = (
    "Olá! Sou o GeoAI Mentor. Posso ajudar você a planejar sua transição "
    "de geociências para Ciência de Dados. Por onde quer começar?"
)


@st.cache_resource(show_spinner=False)
def obter_servico() -> MentorService:
    """Cria o serviço sem expor as tecnologias do back-end à interface."""
    return criar_mentor_service()


def inicializar_sessao() -> None:
    """Inicializa somente o estado visual pertencente ao navegador."""
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid4())
    if "mensagens" not in st.session_state:
        st.session_state.mensagens = [
            {"role": "assistant", "content": MENSAGEM_INICIAL}
        ]


def iniciar_nova_conversa() -> None:
    """Inicia uma conversa sem excluir o histórico anterior."""
    st.session_state.session_id = str(uuid4())
    st.session_state.mensagens = [
        {"role": "assistant", "content": MENSAGEM_INICIAL}
    ]


def carregar_conversa(session_id: str) -> None:
    """Reabre no estado visual uma conversa persistida."""
    mensagens = obter_servico().obter_mensagens(session_id)
    st.session_state.session_id = session_id
    st.session_state.mensagens = [
        {"role": mensagem.role, "content": mensagem.content}
        for mensagem in mensagens
    ] or [{"role": "assistant", "content": MENSAGEM_INICIAL}]


def main() -> None:
    """Monta a interface e encaminha mensagens ao serviço de aplicação."""
    st.set_page_config(page_title="GeoAI Mentor", page_icon="🌍", layout="centered")
    inicializar_sessao()
    st.title("🌍 GeoAI Mentor")
    st.caption("Orientação para geocientistas em transição para Ciência de Dados")

    with st.sidebar:
        st.subheader("Conversas")
        st.button(
            "Nova conversa",
            type="primary",
            use_container_width=True,
            on_click=iniciar_nova_conversa,
        )
        conversas = obter_servico().listar_conversas()
        if conversas:
            opcoes = {conversa.id: conversa.title for conversa in conversas}
            conversa_escolhida = st.selectbox(
                "Histórico",
                options=list(opcoes),
                format_func=opcoes.get,
                index=None,
                placeholder="Selecione uma conversa",
            )
            if conversa_escolhida and conversa_escolhida != st.session_state.session_id:
                carregar_conversa(conversa_escolhida)
                st.rerun()

            novo_titulo = st.text_input("Renomear conversa", max_chars=80)
            col_renomear, col_excluir = st.columns(2)
            if col_renomear.button("Renomear", use_container_width=True):
                obter_servico().renomear_conversa(
                    st.session_state.session_id, novo_titulo
                )
                st.rerun()
            if col_excluir.button("Excluir", use_container_width=True):
                obter_servico().excluir_conversa(st.session_state.session_id)
                iniciar_nova_conversa()
                st.rerun()
        st.caption("O histórico é persistido localmente e não armazena sua chave de API.")

    for mensagem in st.session_state.mensagens:
        with st.chat_message(mensagem["role"]):
            st.markdown(mensagem["content"])

    query = st.chat_input("Digite sua pergunta para o GeoAI Mentor")
    if not query:
        return
    st.session_state.mensagens.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):
        with st.spinner("O GeoAI Mentor está analisando sua pergunta..."):
            try:
                resposta = obter_servico().enviar_mensagem(
                    st.session_state.session_id, query
                )
            except MentorError as exc:
                LOGGER.exception("Falha conhecida ao consultar o mentor")
                resposta = str(exc)
                st.error(resposta)
            except Exception:
                LOGGER.exception("Falha inesperada ao consultar o mentor")
                resposta = "Ocorreu uma falha inesperada. Tente novamente em instantes."
                st.error(resposta)
            else:
                st.markdown(resposta)
    st.session_state.mensagens.append({"role": "assistant", "content": resposta})

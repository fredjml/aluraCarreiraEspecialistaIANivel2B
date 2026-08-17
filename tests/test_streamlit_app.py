"""Teste estrutural da interface Streamlit sem consumo da API."""

from pathlib import Path

from streamlit.testing.v1 import AppTest

from geoai_mentor.domain.models import Message
from geoai_mentor.interfaces import streamlit_app as interface

from datetime import datetime, timezone


APP = Path(__file__).parents[1] / "streamlit_app.py"


def test_interface_inicial_exibe_componentes_principais(monkeypatch) -> None:
    monkeypatch.setenv("GEOAI_DATABASE_PATH", ":memory:")
    app = AppTest.from_file(str(APP)).run(timeout=20)

    assert not app.exception
    assert app.title[0].value.endswith("GeoAI Mentor")
    assert "geocientistas" in app.caption[0].value
    assert app.button[0].label == "Nova conversa"
    assert app.chat_input[0].placeholder.startswith("Digite sua pergunta")
    assert any(
        "Por onde quer começar?" in elemento.value for elemento in app.markdown
    )


def test_nova_conversa_mantem_interface_pronta(monkeypatch) -> None:
    monkeypatch.setenv("GEOAI_DATABASE_PATH", ":memory:")
    app = AppTest.from_file(str(APP)).run(timeout=20)
    app.button[0].click().run(timeout=20)

    assert not app.exception
    assert len(app.chat_message) == 1
    assert any(
        "Por onde quer começar?" in elemento.value for elemento in app.markdown
    )


def test_carregar_conversa_reconstroi_estado_visual(monkeypatch) -> None:
    class Estado(dict):
        __getattr__ = dict.__getitem__
        __setattr__ = dict.__setitem__

    class ServicoFake:
        def obter_mensagens(self, session_id):
            return [Message("user", "Pergunta recuperada", datetime.now(timezone.utc))]

    estado = Estado()
    monkeypatch.setattr(interface.st, "session_state", estado)
    monkeypatch.setattr(interface, "obter_servico", lambda: ServicoFake())

    interface.carregar_conversa("conversa-a")

    assert estado["session_id"] == "conversa-a"
    assert estado["mensagens"] == [
        {"role": "user", "content": "Pergunta recuperada"}
    ]

    monkeypatch.setattr(ServicoFake, "obter_mensagens", lambda self, session_id: [])
    interface.carregar_conversa("conversa-vazia")
    assert estado["mensagens"][0]["content"] == interface.MENSAGEM_INICIAL

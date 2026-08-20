"""Testes de fronteira entre front-end e back-end."""

from pathlib import Path


RAIZ = Path(__file__).parents[1]


def test_frontend_nao_importa_langchain_ou_openai() -> None:
    fonte = (RAIZ / "geoai_mentor" / "interfaces" / "streamlit_app.py").read_text(
        encoding="utf-8"
    ).lower()

    assert "langchain" not in fonte
    assert "chatopenai" not in fonte
    assert "from openai" not in fonte


def test_pontos_de_entrada_permanecem_minimos() -> None:
    terminal = (RAIZ / "chatbot_mentor.py").read_text(encoding="utf-8")
    web = (RAIZ / "streamlit_app.py").read_text(encoding="utf-8")

    assert "geoai_mentor.interfaces.cli" in terminal
    assert "geoai_mentor.interfaces.streamlit_app" in web
    assert len(terminal.splitlines()) <= 12
    assert len(web.splitlines()) <= 10

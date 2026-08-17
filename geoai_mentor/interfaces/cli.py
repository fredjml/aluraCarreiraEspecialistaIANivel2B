"""Interface de terminal do GeoAI Mentor."""

import sys

from geoai_mentor.bootstrap import criar_mentor_service


PERGUNTAS = [
    "Eu sou geofísico e quero migrar para a área de dados. Qual linguagem de programação devo aprender primeiro?",
    "E que tipo de projeto de portfólio eu poderia criar usando essa linguagem?",
]


def main() -> None:
    """Executa a demonstração pela mesma camada usada pelo front-end."""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    service = criar_mentor_service()
    for pergunta in PERGUNTAS:
        resposta = service.enviar_mensagem("sessao_demo", pergunta)
        print(f"\nPergunta: {pergunta}")
        print(f"Resposta: {resposta}")

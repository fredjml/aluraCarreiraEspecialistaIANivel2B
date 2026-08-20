"""Recuperação local, auditável e sem envio de documentos a terceiros."""

from __future__ import annotations

import re
from pathlib import Path

from geoai_mentor.domain.models import KnowledgeChunk


PALAVRAS_COMUNS = {
    "a", "as", "com", "como", "da", "das", "de", "do", "dos", "e", "em",
    "o", "os", "para", "por", "que", "um", "uma",
}


def _termos(texto: str) -> set[str]:
    return {
        termo
        for termo in re.findall(r"[a-záàâãéêíóôõúç0-9]+", texto.lower())
        if len(termo) > 2 and termo not in PALAVRAS_COMUNS
    }


class LocalMarkdownKnowledgeRetriever:
    """Busca por sobreposição lexical somente em Markdown local aprovado."""

    def __init__(self, directory: str, min_score: float = 0.08) -> None:
        self._directory = Path(directory).resolve()
        self._min_score = min_score

    def buscar(self, query: str, limite: int = 3) -> list[KnowledgeChunk]:
        termos_query = _termos(query)
        if not termos_query or not self._directory.is_dir():
            return []
        resultados: list[KnowledgeChunk] = []
        for arquivo in sorted(self._directory.glob("*.md")):
            conteudo = arquivo.read_text(encoding="utf-8")
            for trecho in self._segmentar(conteudo):
                termos_trecho = _termos(trecho)
                score = len(termos_query & termos_trecho) / len(termos_query)
                if score >= self._min_score:
                    resultados.append(KnowledgeChunk(arquivo.name, trecho, score))
        return sorted(resultados, key=lambda item: (-item.score, item.source))[:limite]

    @staticmethod
    def _segmentar(conteudo: str) -> list[str]:
        return [trecho.strip() for trecho in re.split(r"\n\s*\n", conteudo) if trecho.strip()]

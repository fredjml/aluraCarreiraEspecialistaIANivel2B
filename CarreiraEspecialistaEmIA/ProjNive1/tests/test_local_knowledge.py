"""Avaliação determinística do piloto RAG local."""

from geoai_mentor.infrastructure.local_knowledge import LocalMarkdownKnowledgeRetriever


def test_recupera_fonte_pertinente_para_python() -> None:
    retriever = LocalMarkdownKnowledgeRetriever("Analise/docsgeo")

    resultados = retriever.buscar("Como aprender funções, módulos e exceções em Python?")

    assert resultados
    assert resultados[0].source == "01_python_fundamentos.md"
    assert any("funções" in item.content.lower() for item in resultados)


def test_nao_inventa_evidencia_fora_da_base() -> None:
    retriever = LocalMarkdownKnowledgeRetriever("Analise/docsgeo", min_score=0.2)

    assert retriever.buscar("Qual é a previsão meteorológica de Saturno?") == []


def test_diretorio_inexistente_e_consulta_vazia_nao_recuperam() -> None:
    assert LocalMarkdownKnowledgeRetriever("diretorio-inexistente").buscar("python") == []
    assert LocalMarkdownKnowledgeRetriever("Analise/docsgeo").buscar("a e o") == []

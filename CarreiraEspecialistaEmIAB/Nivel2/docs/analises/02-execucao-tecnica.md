# Análise 2: execução técnica

O carregamento cria 50 documentos; o splitter preserva metadados; Chroma usa
embeddings normalizados e filtro de acesso antes da busca. O ranking híbrido
combina oito candidatos semânticos e lexicais, e o reranker seleciona quatro.
A suíte cobre acesso público, caminho vetorial, classificação Gemini, fallback
multiagente e bloqueio HITL no MCP.

**Conclusão:** 13 testes unitários passaram. A rodada real obteve 8/8 com RAG;
cinco casos registraram fallback parcial por cota 429, sem mascarar o evento.

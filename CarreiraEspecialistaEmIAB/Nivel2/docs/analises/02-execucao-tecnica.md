# Análise 2: execução técnica

O modo padrão é local e determinístico. O carregamento cria 50 documentos, o splitter preserva os metadados e a recuperação executa `k=4`. O fluxo de reranking recupera oito candidatos e seleciona quatro. O grafo multiagente executa três intenções e possui fallback quando LangGraph não está instalado.

**Conclusão:** o caminho sem credenciais é reproduzível e adequado para demonstração; ChromaDB/HuggingFace, LLM e juiz automático são integrações opcionais.

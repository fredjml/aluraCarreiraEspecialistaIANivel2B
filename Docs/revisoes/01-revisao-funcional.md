# Revisão 1: funcional

**Escopo:** carga do dataset, chunking, metadados, recuperação, reranking e roteamento.

**Resultado:** aprovada. Foram confirmados 50 registros, metadados, filtro de
acesso, índice Chroma, fusão de rankings, fluxo 8→4, classificação estruturada,
três rotas e bloqueio HITL. A avaliação terminou com 8/8 no caminho RAG.

**Evidência:** `python -m unittest discover -s tests -v` aprovou 14 testes; o
validador de conformidade é executado na etapa final.

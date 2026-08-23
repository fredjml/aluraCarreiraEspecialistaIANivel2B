# Relatório de levantamento · Bytebank Nível 2

**Data:** 22/08/2026

**Escopo:** quatro etapas do desafio Especialista em IA Nível 2

## Objetivo do levantamento

Identificar o que cada entregável exige, localizar as evidências existentes e transformar lacunas em critérios verificáveis, sem usar dados reais ou expor credenciais.

## Requisitos consolidados

| Entregável | Conteúdo obrigatório | Critério de conclusão |
|---|---|---|
| Governança | papéis, responsabilidades, senioridade, carreira em Y, ética, LGPD e LLM Ops | texto versionado + três abas preenchidas na planilha Google |
| Arquitetura RAG | fluxo ponta a ponta, embeddings, vector store, filtros, metadados e glossário | Mermaid + SVG legível + ADR + 15 termos |
| Pipeline RAG | 50 políticas, chunking, metadados, embeddings, Chroma, recuperação, reranking e avaliação | índice persistente, testes e CSV comparativo |
| Multiagente | supervisor, três agentes, A2A, MCP, memórias, HITL e portfólio | grafo executável, servidor MCP, diagrama e README |

## Inventário inicial e lacunas

O repositório já continha dataset fictício, documentos de arquitetura, protótipos Python, Mermaid e CSVs de governança. As lacunas que impediam avaliação completa eram:

1. a planilha Google tinha três abas vazias e nomes genéricos;
2. `query()` ainda usava somente sobreposição lexical, apesar da função Chroma existir isolada;
3. o filtro `nivel_acesso` não era aplicado antes da recuperação;
4. o supervisor classificava somente por palavras-chave;
5. o MCP não implementava `criar_conta` nem recursos URI para saldo/fatura;
6. diagramas não tinham exportação visual incorporada ao README;
7. a avaliação Gemini não tinha dependência instalada nem evidência atual;
8. faltava relatório de levantamento e o DOCX existente não possuía hierarquia/tabelas nativas adequadas;
9. análises e revisões descreviam pendências externas já superadas.

## Decisões do levantamento

- Manter todo conteúdo bancário fictício e usar acesso `publico` como padrão.
- Integrar Chroma nativamente ao caminho principal e persistir em `outputs/chroma_db`.
- Usar embeddings locais offline e fusão de rankings para melhor cobertura em português.
- Ativar Gemini somente por `.env`, registrando modelo, modos e fallbacks.
- Usar classificação Gemini estruturada no supervisor, com fallback determinístico.
- Separar A2A (agente-agente) de MCP (agente-capacidade) e bloquear mutações com HITL.
- Versionar o CSV de avaliação, mas não o banco Chroma nem a credencial.
- Publicar diagramas em SVG para leitura direta no GitHub e Pages.

## Riscos e controles

| Risco | Controle aplicado |
|---|---|
| Exposição de chave | `.env` ignorado; nenhuma saída imprime o valor |
| Política interna em resposta pública | filtro de metadata antes do retriever + teste dedicado |
| Alucinação | contexto exclusivo, citações, fontes e resposta segura |
| Quota/indisponibilidade Gemini | fallback identificado por componente no CSV |
| Mutação bancária indevida | aprovação humana obrigatória + core não configurado por padrão |
| Documento inconsistente | geração DOCX a partir do Markdown e inspeção visual de todas as páginas |

## Critério de saída

O levantamento é encerrado quando os quatro entregáveis têm evidência local e externa, os testes passam, a planilha está preenchida e verificada, os relatórios estão disponíveis em Markdown e DOCX e a entrega está pronta para revisão em PR sem merge automático.

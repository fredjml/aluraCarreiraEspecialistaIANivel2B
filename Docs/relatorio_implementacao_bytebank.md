# Relatório de implementação · Bytebank Nível 2

**Data:** 22/08/2026

**Repositório:** https://github.com/fredjml/aluraCarreiraEspecialistaIANivel2B

**Branch:** `codex/finalizar-entregaveis-nivel2`

## Resumo executivo

Os quatro entregáveis foram implementados e preparados para avaliação. A solução inclui governança e carreira em Y, arquitetura RAG, pipeline Chroma funcional com avaliação, grafo multiagente, servidor MCP com HITL, documentação de portfólio, diagramas exportados e planilha Google verificada.

## Implementação realizada

### 1. Governança e time

O documento de governança cobre LGPD, imparcialidade, transparência, explicabilidade, reprodutibilidade, responsabilidade, alucinações e os quatro pilares de LLM Ops. A planilha Google foi renomeada e preenchida com as abas `Composição do time`, `Carreira em Y` e `Glossário RAG`, incluindo cabeçalhos fixos, filtros, quebra de texto e larguras adequadas.

### 2. RAG e dados

As 50 políticas CSV são carregadas como documentos com `id`, `dominio`, `secao`, `nivel_acesso`, `categoria_semantica`, `origem` e `chunk_index`. O chunking usa 500 caracteres e overlap 100. O modelo `all-MiniLM-L6-v2` gera embeddings normalizados; Chroma persiste o índice com IDs estáveis. O filtro de acesso ocorre antes do ranking. A recuperação híbrida combina Chroma e ranking lexical, seguida de reranking 8→4.

### 3. Gemini e avaliação

A integração usa a SDK `google-genai`, saídas estruturadas Pydantic e `gemini-3.5-flash-lite`. A rodada de oito casos obteve 1/8 sem RAG e 8/8 com RAG. A recuperação Chroma+híbrida operou nos oito casos. A cota HTTP 429 fez cinco casos usarem ao menos um fallback local; cada ocorrência está registrada, portanto a evidência não é apresentada como rodada integralmente Gemini.

### 4. Multiagente, A2A, MCP e HITL

O LangGraph contém supervisor, agentes `conta_corrente`, `cartao_credito` e `suporte`, roteamento condicional e síntese. A classificação usa Gemini quando disponível e fallback local rastreável. O servidor FastMCP expõe políticas, saldo, fatura, prompt fundamentado e ferramentas `criar_conta`/`solicitar_cartao`. As mutações exigem `aprovado_por_humano`; Platinum marca pausa HITL no estado.

## Evidências de aceite

| ID | Evidência | Resultado |
|---|---|---|
| E1 | `Docs/01-governanca.md` + planilha Google | concluído |
| E2 | `diagrams/rag.mmd` + `diagrams/rag.svg` + glossário | concluído |
| E3 | `src/rag_pipeline.py` + Chroma + 50 políticas | concluído |
| E4 | `outputs/avaliacao_rag.csv` | RAG 8/8; fallbacks 429 registrados |
| E5 | `src/multiagent_graph.py` + Agent Cards | concluído |
| E6 | `scripts/bytebank_mcp_server.py` + testes HITL | concluído |
| E7 | README de portfólio + dois SVGs | concluído |
| E8 | relatórios Markdown/DOCX + análises/revisões | concluído |
| E9 | testes unitários e validador de conformidade | aprovado |
| E10 | Google Sheets e GitHub Pages | verificados |

## Segurança

- `.env` e o índice Chroma permanecem fora do Git.
- A chave nunca é impressa nem copiada para documentação.
- O retriever público não recebe chunks internos.
- Erros de API não são convertidos em sucesso silencioso.
- Ferramentas de mutação requerem aprovação humana e configuração explícita do core.
- Nenhum merge ou remoção externa faz parte da automação.

## Limites conhecidos

O banco, clientes e políticas são fictícios. O modelo de embeddings compacto não é específico para português, motivo da fusão lexical. A API do core bancário não foi fornecida e permanece desabilitada. A cota Gemini impediu uma rodada 100% externa, mas a avaliação terminou com fallbacks rastreáveis e 100% de acerto RAG.

## Reprodução

```powershell
.\.venv\Scripts\Activate.ps1
python scripts/setup_runtime.py
python -m unittest discover -s tests -v
python scripts/validate_project.py
python -m src.rag_pipeline --mode local --retrieval chroma
python -m src.evaluation --mode gemini --retrieval chroma
python -m src.multiagent_graph --mode auto
```

## Publicação

A branch de correção é enviada para revisão por Pull Request e não é mesclada automaticamente. O GitHub Pages público foi validado por HTTP; o endereço e a planilha estão disponíveis no README.

**Pull Request:** https://github.com/fredjml/aluraCarreiraEspecialistaIANivel2B/pull/1

**Repositório:** https://github.com/fredjml/aluraCarreiraEspecialistaIANivel2B

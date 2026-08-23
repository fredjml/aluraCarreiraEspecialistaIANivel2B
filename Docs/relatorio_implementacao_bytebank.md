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

## Tabela final de critérios de aceite

| ID | Critério de aceite | Evidência principal | Status |
|---|---|---|---|
| 1.1 | Planilha com cargos, responsabilidades, nível e relação com agentes de IA; mínimo de cinco papéis | `data/composicao_time.csv` e planilha Google | FEITO |
| 1.2 | Aba de carreira em Y com caminhos de gestão e especialista | `data/carreira_y.csv` e planilha Google | FEITO |
| 1.3 | Princípios de privacidade/LGPD, imparcialidade, transparência, explicabilidade, reprodutibilidade e responsabilidade | `Docs/01-governanca.md` | FEITO |
| 1.4 | Três causas de alucinação e ao menos duas técnicas de mitigação | `Docs/01-governanca.md` | FEITO |
| 1.5 | Quatro pilares de LLM Ops aplicados ao contexto bancário | `Docs/01-governanca.md` | FEITO |
| 1.6 | README narrativo e publicação no GitHub Pages | `README.md`, `index.md` e site publicado | FEITO |
| 2.1 | Diagrama RAG completo: fonte, carga, chunking, overlap, embeddings, vector store, retriever, reranking, LLM e fontes | `diagrams/rag.mmd` e `diagrams/rag.svg` | FEITO |
| 2.2 | Comparação FAISS, ChromaDB e Supabase com escolha justificada | `Docs/02-arquitetura-rag.md` | FEITO |
| 2.3 | Glossário com os 15 termos obrigatórios e exemplos Bytebank | `data/glossario_rag.csv` e planilha Google | FEITO |
| 2.4 | ADR comparando RAG e fine-tuning, critérios de embeddings e estratégia de metadados | `Docs/02-arquitetura-rag.md` | FEITO |
| 3.1 | Carga do CSV em documentos com `id`, `dominio`, `secao` e `nivel_acesso` | `src/rag_pipeline.py` e 50 políticas | FEITO |
| 3.2 | Chunking recursivo 500/100 e categoria semântica enriquecida | `src/rag_pipeline.py` e testes de metadados | FEITO |
| 3.3 | Embeddings locais, Chroma persistente e retriever por similaridade com `k=4` | `src/rag_pipeline.py` e testes vetoriais | FEITO |
| 3.4 | Recuperação de oito candidatos, reranking e seleção dos quatro melhores | `src/rag_pipeline.py` e validador de conformidade | FEITO |
| 3.5 | Comparação da mesma pergunta sem RAG e com RAG | `src/evaluation.py` e `outputs/avaliacao_rag.csv` | FEITO |
| 3.6 | Dataset de validação com oito perguntas e gabaritos | `src/evaluation.py` | FEITO |
| 3.7 | Avaliação estruturada, percentual de acertos e tabela Markdown por caso | `Docs/05-avaliacao-rag.md` e CSV de avaliação | FEITO |
| 3.8 | Rastreabilidade de modos, fontes e fallbacks sem mascarar falhas externas | `outputs/avaliacao_rag.csv` e `Docs/05-avaliacao-rag.md` | FEITO |
| 4.1 | Diagrama com front-end, BFA, três agentes, Agent Cards, A2A, MCP, HITL e snapshots | `diagrams/multiagente.mmd` e SVG | FEITO |
| 4.2 | Comparação A2A/MCP e conectividade por polling, SSE e webhook | `Docs/04-arquitetura-multiagente.md` | FEITO |
| 4.3 | Memórias semântica, episódica e procedural no contexto bancário | `Docs/04-arquitetura-multiagente.md` | FEITO |
| 4.4 | Fluxo HITL Platinum com interrupção, snapshot, decisão e retomada/cancelamento | `Docs/04-arquitetura-multiagente.md` e testes | FEITO |
| 4.5 | `StateGraph`, estado tipado, classificação, três agentes, rota condicional e síntese | `src/multiagent_graph.py` | FEITO |
| 4.6 | Grafo Mermaid e testes das três rotas | `diagrams/multiagente.mmd` e `tests/test_multiagent_graph.py` | FEITO |
| 4.7 | Interface Gradio exibindo resposta e classificação | `src/app.py` | FEITO |
| 4.8 | MCP separando recursos, ferramentas e prompts, com bloqueio de mutações por HITL | `scripts/bytebank_mcp_server.py` e testes MCP | FEITO |
| 4.9 | README final com arquitetura, tecnologias, desafios e aprendizados | `README.md` | FEITO |
| V.1 | Suíte unitária local | 14 testes executados em 23/08/2026 | FEITO |
| V.2 | Validador estrutural, de dados, sintaxe e contratos | `python scripts/validate_project.py`: `CONFORMIDADE=OK` | FEITO |
| V.3 | Integridade do histórico Git local | `git log` e `git fsck --full` após recuperação do objeto `8f2a23a…` | FEITO |

Todos os critérios marcados como `FEITO` possuem evidência local ou externa
indicada na mesma linha. A rodada Gemini permanece qualificada: três casos
concluíram geração e julgamento externos; cinco acionaram fallback por HTTP 429.

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
python -m unittest discover -s tests -v  # 14 testes aprovados em 23/08/2026
python scripts/validate_project.py
python -m src.rag_pipeline --mode local --retrieval chroma
python -m src.evaluation --mode gemini --retrieval chroma
python -m src.multiagent_graph --mode auto
```

## Publicação

A branch de correção é enviada para revisão por Pull Request e não é mesclada automaticamente. O GitHub Pages público foi validado por HTTP; o endereço e a planilha estão disponíveis no README.

**Pull Request:** https://github.com/fredjml/aluraCarreiraEspecialistaIANivel2B/pull/1

**Repositório:** https://github.com/fredjml/aluraCarreiraEspecialistaIANivel2B

# Relatório de implementação - Bytebank Nivel 2

**Data UTC:** 2026-08-22T23:50:08.574548+00:00  
**Repositório:** https://github.com/fredjml/aluraCarreiraEspecialistaIANivel2B

## Objetivo

Implementar as quatro etapas do desafio usando apenas dados fictícios, com documentação, código local, validações e rastreabilidade.

## Passo a passo

1. Levantamento do enunciado e inventário da raiz `Nivel2`.
2. Criação do plano de execução e regras de segurança.
3. Fundação: README, governança, carreira, dataset e ambiente.
4. Arquitetura RAG, ADR, glossário e diagrama.
5. Pipeline local, avaliação estruturada e metadados.
6. Grafo multiagente, A2A, MCP, HITL, Agent Cards e Gradio.
7. Scripts MCP local, validação de conformidade e testes.
8. Três análises, três revisões e geração deste relatório.

## Testes e evidências

- `python -m compileall -q src tests scripts`: aprovado.
- `python -m unittest discover -s tests -v`: aprovado.
- `python scripts/validate_project.py`: aprovado.
- `python -m src.rag_pipeline --question "Qual o limite do Pix noturno?"`: executado com fontes e metadados.
- `python -m src.multiagent_graph`: executado com três domínios.
- `python -m src.evaluation`: relatório de oito perguntas gerado; juiz LLM marcado como pendente.
- `python scripts/mcp_tools.py` com operações JSON: disponível para teste local.

## Critérios de aceite

| ID | Critério | Evidência | Status |
|---|---|---|---|
| E1 | Governança, ética, LGPD, LLM Ops e papéis do time | `docs/01-governanca.md; data/composicao_time.csv` | **feito** |
| E2 | Carreira em Y e estratégia de portfólio | `data/carreira_y.csv; README.md` | **feito** |
| E3 | Diagrama RAG completo e glossário com 15 termos | `diagrams/rag.mmd; data/glossario_rag.csv` | **feito** |
| E4 | ADR de RAG, embeddings, vector store e metadados | `docs/02-arquitetura-rag.md` | **feito** |
| E5 | Dataset fictício com 50 políticas e contrato de campos | `data/politicas_bytebank.csv` | **feito** |
| E6 | Chunking 500/100, categoria semântica e metadados | `src/rag_pipeline.py; tests/test_rag_pipeline.py` | **feito** |
| E7 | Recuperação k=4 e reranking demonstrativo 8 para 4 | `src/rag_pipeline.py` | **feito** |
| E8 | Avaliação com 8 perguntas e rastreabilidade | `src/evaluation.py; docs/05-avaliacao-rag.md` | **feito** |
| E9 | Supervisor, três agentes, TypedDict e roteamento | `src/multiagent_graph.py; tests/test_multiagent_graph.py` | **feito** |
| E10 | A2A, MCP, Agent Cards, memória, HITL e snapshots | `docs/04-arquitetura-multiagente.md; data/agent_cards.csv` | **feito** |
| E11 | Interface Gradio e modo local sem credenciais | `src/app.py; .env.example` | **feito** |
| E12 | Rules, skill, script MCP e validação de conformidade | `.github/; scripts/validate_project.py; scripts/mcp_tools.py` | **feito** |
| E13 | Relatórios de implementação em Markdown e DOCX | `docs/relatorio_implementacao_bytebank.md; .docx` | **feito** |

## Análises

### Análise 1 - cobertura

Os requisitos do enunciado foram mapeados para artefatos E1-E13; o script de conformidade verifica os contratos críticos.

### Análise 2 - execução

O caminho local é determinístico e reproduzível. APIs externas permanecem opcionais e são explicitamente marcadas como pendentes.

### Análise 3 - riscos

Os principais riscos residuais são qualidade semântica do fallback lexical, ausência de juiz LLM e ausência de publicação/Google Sheets/Power BI.

## Revisões

### Revisão 1 - funcional

Testes confirmam carga de 50 documentos, preservação de metadados, reranking 8->4 e três intenções.

### Revisão 2 - segurança

Não há credenciais reais; .env é ignorado; MCP separa mutações, leituras e prompts; conteúdo é fictício.

### Revisão 3 - entrega

README, plano, diagramas, dados, código, testes, skill, rules e relatórios estão presentes; publicação não é alegada como executada.

## Como testar

```powershell
.\.venv\Scripts\Activate.ps1
python scripts/validate_project.py
python -m unittest discover -s tests -v
python -m src.rag_pipeline --question "Qual é a anuidade do cartão Platinum?"
python -m src.multiagent_graph
'{'"operation":"list"'}' | python scripts/mcp_tools.py
python -m src.evaluation
```

## Pendências externas

GitHub Pages, Google Sheets, APIs de LLM, juiz automático, screenshots de Power BI e publicação adicional não foram executados. Requerem credenciais, dados ou ação externa.

## Repositório

https://github.com/fredjml/aluraCarreiraEspecialistaIANivel2B

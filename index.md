---
layout: default
title: Bytebank AI Ecosystem - Nivel 2
---

# Bytebank AI Ecosystem - Nível 2

Projeto fictício sobre governança de IA, RAG auditável e arquitetura multiagente para atendimento bancário digital.

## Sobre Mim

Sou profissional de tecnologia em formação contínua na trilha Especialista em IA da Alura, com foco em soluções de IA rastreáveis, testáveis, seguras e bem documentadas.

## Projeto em Destaque

O Bytebank AI Ecosystem transforma políticas fictícias em respostas com fontes, distribui solicitações entre agentes especializados e exige aprovação humana antes de mutações sensíveis.

## Entregáveis para avaliação

| # | Entregável | Evidências | Status |
|---|---|---|---|
| 1 | Governança e time de IA | [Documento](Docs/01-governanca.md), [composição](data/composicao_time.csv), [carreira em Y](data/carreira_y.csv) e [planilha Google](https://docs.google.com/spreadsheets/d/1jJYN5SKQHZzNuuFBLDupMnQATMTfR3QBgl82MX-CJiE/edit?usp=sharing) | Concluído |
| 2 | Arquitetura RAG e glossário | [ADR](Docs/02-arquitetura-rag.md), [Mermaid](diagrams/rag.mmd), [SVG](diagrams/rag.svg) e [glossário](data/glossario_rag.csv) | Concluído |
| 3 | Pipeline RAG funcional | [Código](src/rag_pipeline.py), [50 políticas](data/politicas_bytebank.csv), [avaliação](outputs/avaliacao_rag.csv) e [testes](tests/test_rag_pipeline.py) | Concluído |
| 4 | Arquitetura multiagente | [Documento](Docs/04-arquitetura-multiagente.md), [SVG](diagrams/multiagente.svg), [grafo](src/multiagent_graph.py) e [MCP](scripts/bytebank_mcp_server.py) | Concluído |

## Resultado validado

- Sem RAG: **1/8 (12,5%)**.
- Com RAG: **8/8 (100%)**.
- Testes locais: **14/14 aprovados**.
- Conformidade estrutural: **OK**.

## Navegação complementar

- [Visão geral completa](README.md)
- [Avaliação do pipeline RAG](Docs/05-avaliacao-rag.md)
- [Integrações MCP e limites externos](Docs/06-integracoes-mcp.md)
- Relatório de levantamento: [Markdown](Docs/relatorio_levantamento_bytebank.md) · [DOCX](Docs/relatorio_levantamento_bytebank.docx)
- Relatório de implementação: [Markdown](Docs/relatorio_implementacao_bytebank.md) · [DOCX](Docs/relatorio_implementacao_bytebank.docx)
- Relatório executivo final: [Markdown](Docs/relatorio_executivo_implementacao_bytebank.md) · [DOCX](Docs/relatorio_executivo_implementacao_bytebank.docx)
- [PR #1 integrado à `main`](https://github.com/fredjml/aluraCarreiraEspecialistaIANivel2B/pull/1)

## Evidências locais

O repositório contém dados fictícios, testes automatizados, diagramas Mermaid e um protótipo Gradio. O servidor MCP local separa recursos de leitura, ferramentas de mutação e prompts; integrações externas só são ativadas por variáveis locais autorizadas.

## Contato

- GitHub: [@fredjml](https://github.com/fredjml)
- Repositório: [aluraCarreiraEspecialistaIANivel2B](https://github.com/fredjml/aluraCarreiraEspecialistaIANivel2B)

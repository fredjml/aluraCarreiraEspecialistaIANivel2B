# Bytebank AI Ecosystem | Nivel 2

Projeto fictício do checkpoint Especialista em IA Nível 2. O objetivo é demonstrar como uma equipe pode estruturar governança, um sistema RAG auditável e uma arquitetura multiagente para atendimento digital bancário.

> **Aviso:** este repositório não usa dados reais de clientes, não representa o Bytebank real e não constitui recomendação financeira ou jurídica.

## Sobre o projeto

A jornada começa com políticas internas fictícias e evolui até um protótipo local de agentes. A documentação conecta decisões de negócio, controles de LGPD, recuperação de conhecimento e intervenção humana.

## Etapas

1. Governança, ética, papéis do time e carreira em Y.
2. Arquitetura RAG, glossário e decisões técnicas.
3. Pipeline de ingestão, metadados, recuperação, reranking e avaliação.
4. Supervisor multiagente, A2A, MCP, HITL, snapshots e interface Gradio.

## Estrutura

- [`docs/`](docs/): governança, ADRs e arquitetura.
- [`data/`](data/): dataset e planilhas reproduzíveis em CSV.
- [`src/`](src/): pipeline RAG e protótipo multiagente.
- [`diagrams/`](diagrams/): diagramas Mermaid versionáveis.
- [`tests/`](tests/): verificações automatizadas locais.
- [`PLANO_EXECUCAO.md`](PLANO_EXECUCAO.md): plano e critérios de validação.

## Execução local

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m src.rag_pipeline --question "Quais são as regras para abrir uma conta?"
python -m src.multiagent_graph
```

O modo padrão é local e determinístico. APIs de LLM, embeddings externos, Google Sheets, GitHub Pages e publicação ficam desabilitados até que sejam configurados conscientemente.

## Portfólio

### Motivação
Atendimento bancário precisa responder com precisão, explicar suas fontes e respeitar limites de acesso.

### Problema resolvido
O projeto organiza políticas dispersas em uma experiência consultável e encaminha intenções para agentes especializados, sem confundir leitura de dados com mutação.

### Desafios técnicos
Chunking com preservação de metadados, avaliação sem mascarar resultados ausentes, roteamento determinístico e pausa humana antes de decisões sensíveis.

### Aprendizados
RAG facilita atualização e rastreabilidade; agentes precisam de contratos claros; e governança não é um anexo, mas parte da arquitetura.

## Limitações e pendências

- O dataset é fictício e não valida regras de um banco real.
- Resultados de LLM e juiz automático permanecem pendentes quando não há credencial.
- Não há screenshots de Power BI no workspace.
- Usuário GitHub, publicação, Google Sheets e GitHub Pages dependem de dados e autorização do usuário.

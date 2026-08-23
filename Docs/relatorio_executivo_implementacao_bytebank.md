# Relatório Executivo de Implementação - Bytebank AI Ecosystem Nível 2

**Data:** 23/08/2026

**Repositório:** https://github.com/fredjml/aluraCarreiraEspecialistaIANivel2B

**Branch verificada:** `main`

**Escopo:** governança de IA, arquitetura RAG, pipeline auditável, avaliação comparativa, arquitetura multiagente, A2A, MCP, Human-in-the-Loop, interface e evidências de entrega.

## Resumo executivo

O projeto implementa um ecossistema fictício de IA para atendimento digital do Bytebank. A entrega cobre as quatro etapas do checkpoint Especialista em IA Nível 2 e conecta governança, dados, recuperação de conhecimento, geração fundamentada, agentes especializados e aprovação humana. O desenho evita que uma demonstração técnica seja confundida com uma integração bancária real: dados são fictícios, mutações são bloqueadas por padrão e integrações externas exigem configuração explícita.

A solução processa 50 políticas, preserva metadados de domínio e acesso, cria chunks de 500 caracteres com overlap 100, indexa embeddings locais no ChromaDB e combina recuperação vetorial com ranking lexical. O fluxo recupera oito candidatos, aplica reranking e entrega quatro evidências à geração. A avaliação versionada contém oito perguntas e compara o mesmo gabarito com e sem RAG.

O resultado observado foi 1/8 sem RAG e 8/8 com RAG. Três casos concluíram geração e julgamento no Gemini; cinco registraram fallback local após HTTP 429. Essa distinção é material: a acurácia do caminho RAG foi 100%, mas a rodada não é apresentada como execução integralmente externa.

| Indicador executivo | Resultado verificado |
|---|---|
| Políticas fictícias processadas | 50 |
| Casos de validação | 8 |
| Acurácia sem RAG | 1/8 - 12,5% |
| Acurácia com RAG | 8/8 - 100% |
| Recuperação com fontes | 8/8 casos |
| Testes unitários | 14/14 aprovados |
| Conformidade do projeto | `CONFORMIDADE=OK` |
| Integridade Git local | `git log` e `git fsck --full` operacionais |

## 1. Contexto, objetivo e fronteiras

### 1.1 Problema de negócio

O cenário exige respostas sobre políticas bancárias com precisão, rastreabilidade e separação de acesso. Um modelo generativo isolado pode responder de forma plausível sem evidência, usar conhecimento desatualizado ou misturar conteúdo público e interno. Além disso, ações como criar conta ou solicitar cartão não podem ser executadas sem autorização, identidade, auditoria e responsabilização.

### 1.2 Objetivo implementado

A implementação cria uma base reproduzível para:

- documentar governança, papéis e controles de IA;
- consultar políticas com RAG e fontes identificáveis;
- comparar respostas com e sem contexto recuperado;
- rotear solicitações para agentes especializados;
- padronizar capacidades por MCP e colaboração por A2A;
- interromper mutações sensíveis antes da execução;
- produzir evidências executáveis, documentais e publicáveis.

### 1.3 Limites de escopo

O Bytebank, seus clientes e suas políticas são fictícios. O protótipo não está conectado a um core bancário de produção. Recursos externos de saldo e fatura retornam `not_configured` sem endpoint e token locais. Ferramentas de mutação exigem `aprovado_por_humano=true` e ainda dependem de uma API de homologação. Nenhum dado real deve ser usado até que identidade, autorização, retenção, observabilidade e resposta a incidentes estejam definidos.

## 2. Entregáveis e organização do repositório

| Entregável | Implementação | Evidência principal |
|---|---|---|
| Governança e composição do time | Princípios, LLM Ops, papéis e carreira em Y | `Docs/01-governanca.md`, `data/composicao_time.csv`, `data/carreira_y.csv` |
| Arquitetura RAG e glossário | ADR, diagrama Mermaid/SVG, comparação de stores e 15 termos | `Docs/02-arquitetura-rag.md`, `diagrams/rag.*`, `data/glossario_rag.csv` |
| Pipeline RAG funcional | Carga, chunking, embeddings, Chroma, fusão, reranking, geração e avaliação | `src/rag_pipeline.py`, `src/evaluation.py`, `outputs/avaliacao_rag.csv` |
| Arquitetura multiagente | Supervisor, três agentes, A2A, MCP, HITL, interface e Agent Cards | `src/multiagent_graph.py`, `scripts/bytebank_mcp_server.py`, `src/app.py` |
| Evidências de entrega | Testes, validador, análises, revisões, relatórios e publicação | `tests/`, `scripts/validate_project.py`, `Docs/`, `README.md` |

O repositório separa dados em `data/`, diagramas em `diagrams/`, documentação em `Docs/`, código em `src/`, automações em `scripts/`, evidências em `outputs/` e contratos de comportamento em `tests/`. Essa topologia reduz acoplamento e permite revisar requisitos sem depender da execução de APIs externas.

## 3. Governança, time e LLM Ops

### 3.1 Princípios aplicados

A governança documenta privacidade e LGPD, imparcialidade, transparência, explicabilidade, reprodutibilidade e responsabilidade. O chatbot deve informar que usa IA, citar fontes e declarar insuficiência de evidência. Dados e prompts precisam de versão, proprietário e trilha de alteração. Decisões sensíveis permanecem sob responsabilidade humana.

### 3.2 Controle de alucinações

Três fontes de risco foram tratadas: lacunas ou desatualização da base; recuperação inadequada; e geração probabilística além das evidências. As mitigações incluem RAG com fontes, filtro de acesso antes da recuperação, limiar de relevância, resposta segura quando não há evidência, validação estruturada, testes de regressão e revisão humana para mutações.

### 3.3 Quatro pilares de LLM Ops

- **Gerenciamento:** inventário de modelos, prompts, datasets, versões, permissões, custos e responsáveis.
- **Otimização:** ajuste de chunking, recuperação, latência, custo e qualidade sem retirar controles.
- **Automação:** ingestão, testes, publicação de índice, rollback, alertas e execução reproduzível.
- **Qualidade:** cobertura, groundedness, relevância, segurança, latência, fallbacks e revisão humana.

### 3.4 Composição do time

Foram modelados engenheiro de dados, analista de dados, cientista de dados, DPO, engenheiro de IA, especialista de segurança e Product Manager de IA. O desenho de carreira em Y registra contribuição técnica, evolução como especialista e caminhos possíveis de gestão. A composição cobre dados, modelagem, produto, privacidade, segurança e operação, evitando concentrar responsabilidade no desenvolvimento do modelo.

## 4. Dados e preparação do conhecimento

### 4.1 Dataset

O arquivo `data/politicas_bytebank.csv` contém 50 políticas fictícias nos domínios conta corrente, cartão de crédito, suporte, RH e segurança.

| Campo | Tipo | Uso no pipeline |
|---|---|---|
| `id` | Inteiro | Identidade estável da política e rastreabilidade |
| `dominio` | Texto | Classificação funcional e filtro |
| `secao` | Texto | Contexto da origem |
| `conteudo` | Texto | Conteúdo convertido em `page_content` |
| `nivel_acesso` | Texto | Autorização: público, interno ou restrito |

Cada documento recebe ainda `categoria_semantica` e `origem`; cada chunk acrescenta `chunk_index`. Os metadados originais não são descartados.

### 4.2 Carga e chunking

`load_documents()` usa UTF-8 e converte cada linha em um `Document`. `split_documents()` aplica `RecursiveCharacterTextSplitter` com `chunk_size=500` e `chunk_overlap=100`. O overlap reduz perda de contexto nas fronteiras, enquanto o tamanho previsível facilita custo e janela. A categoria semântica é inferida por palavras-chave normalizadas para tarifas, segurança, abertura, cartão, RH ou suporte.

### 4.3 Controle de acesso

`filter_by_access()` restringe os chunks antes do ranking lexical. No Chroma, o mesmo controle é aplicado por filtro `where` sobre `nivel_acesso`. A consulta pública usa somente `publico`; conteúdo interno não entra no contexto padrão. Em produção, `allowed_levels` deve ser derivado de identidade e papéis reais, nunca de um valor fornecido livremente pelo cliente.

## 5. Arquitetura e implementação RAG

### 5.1 Decisão RAG versus fine-tuning

RAG foi escolhido para fatos mutáveis porque permite atualizar ou remover documentos sem treinar novamente o modelo, mantém as fontes fora dos pesos e melhora auditoria. Fine-tuning continua útil para estilo e comportamento, mas não substitui a fonte de verdade nem o controle de acesso. A decisão considera custo de atualização, rastreabilidade e sensibilidade dos dados.

### 5.2 Embeddings e vector store

O pipeline usa `sentence-transformers/all-MiniLM-L6-v2` localmente, com vetores normalizados. O modelo compacto reduz dependência externa, mas não é especializado em português; por isso o ranking vetorial é combinado ao lexical. O ChromaDB persiste a coleção `bytebank_politicas_v1` com distância de cosseno e IDs estáveis no formato `policy-{id}-chunk-{chunk_index}`.

FAISS foi considerado simples e rápido, porém exigiria mais infraestrutura para metadados e persistência. Supabase agregaria Postgres e operação gerenciada, mas introduziria dependência externa e decisões adicionais de residência e acesso. Chroma foi selecionado para o protótipo por persistência local, filtros e integração com o ecossistema LangChain.

### 5.3 Fluxo de consulta

1. A pergunta é recebida com níveis de acesso permitidos.
2. O Chroma recupera oito candidatos semânticos.
3. O ranking lexical recupera oito candidatos autorizados.
4. `hybrid_candidates()` combina rankings por Reciprocal Rank Fusion.
5. O reranker ordena oito candidatos e seleciona quatro.
6. A geração responde apenas com os quatro chunks selecionados.
7. A resposta retorna `source_documents`, modos usados e lista de fallbacks.

Quando Gemini está disponível, reranking e geração podem usar saída estruturada. Falhas externas não são convertidas em sucesso silencioso: cada exceção produz um registro de fallback e o caminho local determinístico mantém a execução reproduzível.

### 5.4 Modos operacionais

| Modo | Comportamento |
|---|---|
| `local` | Proíbe chamadas externas e usa recuperação/geração determinísticas |
| `gemini` | Solicita Gemini e registra fallback por componente em caso de falha |
| `auto` | Ativa Gemini apenas quando há configuração local autorizada |
| `lexical` | Executa recuperação determinística sem Chroma |
| `chroma` | Exige índice vetorial e propaga erro de inicialização |
| `auto` de recuperação | Prefere Chroma e registra fallback lexical se necessário |

## 6. Avaliação comparativa

### 6.1 Método

O conjunto de validação contém oito pares de pergunta e gabarito baseados nas políticas. Para cada caso são produzidas uma resposta sem RAG e uma resposta com RAG. O juiz estruturado avalia presença do fato esperado; no caminho RAG, exige também citação de fonte. O CSV registra pergunta, gabarito, respostas, fontes, modo de recuperação, reranking, geração, juiz, notas, justificativas e fallbacks.

### 6.2 Resultado por caso

| # | Tema | Sem RAG | Com RAG | Fontes principais | Execução RAG/juiz |
|---:|---|---:|---:|---|---|
| 1 | Documentos para abrir conta | 100 | 100 | 1, 2, 50, 28 | Gemini/Gemini |
| 2 | Custo da TED adicional | 0 | 100 | 3, 30, 25, 36 | Gemini/Gemini |
| 3 | Anuidade do Platinum | 0 | 100 | 9, 36, 11, 45 | Gemini/Gemini |
| 4 | Limite máximo Gold | 0 | 100 | 11, 9, 7, 13 | Local/Local - 429 |
| 5 | Contestação de transação | 0 | 100 | 30, 9, 46, 1 | Local/Local - 429 |
| 6 | Exclusão de dados pessoais | 0 | 100 | 28, 5, 26, 50 | Local/Local - 429 |
| 7 | Prazo da ouvidoria | 0 | 100 | 15, 37, 5, 28 | Local/Local - 429 |
| 8 | Limite do Pix noturno | 0 | 100 | 32, 31, 11, 29 | Local/Local - 429 |

### 6.3 Interpretação

O ganho de 12,5% para 100% demonstra a contribuição do contexto recuperado neste dataset, não uma garantia de desempenho em produção. Cinco casos acionaram fallback por limite HTTP 429; logo, o resultado deve ser descrito como RAG híbrido rastreável. Uma avaliação produtiva deve ampliar amostra, separar modelo gerador e juiz, incluir revisão humana, medir recall de recuperação e testar consultas adversariais e controles de acesso.

## 7. Arquitetura multiagente

### 7.1 Grafo e estado

O `AgentState` tipado contém mensagem, classificação, resposta do agente, resposta final, modo de classificação, fallbacks e indicador de aprovação humana. O `StateGraph` executa o nó `classificar`, roteia para `conta_corrente`, `cartao_credito` ou `suporte` e converge em `sintese`.

O classificador usa Gemini quando configurado. Em falha, `classify_local()` aplica regras determinísticas rastreáveis. A rota condicional retorna exatamente o nome do nó. Solicitações que mencionam Platinum ativam `requer_aprovacao_humana`.

### 7.2 Agent Cards

| Agente | Responsabilidade | Capacidades |
|---|---|---|
| Conta corrente | Conta, Pix, TED, saldo e empréstimo | `conta_corrente`, `consulta_politica` |
| Cartão de crédito | Cartões, limites, anuidade e fatura | `cartao_credito`, `consulta_politica`, `platinum_hitl` |
| Suporte | Canais, reclamações e SLAs | `suporte`, `escalonamento` |

As URLs dos Agent Cards são placeholders locais. O protótipo demonstra contrato e roteamento, não serviços publicados.

### 7.3 A2A e MCP

| Dimensão | A2A | MCP |
|---|---|---|
| Foco | Colaboração entre supervisor e agentes | Acesso a ferramentas, recursos e prompts |
| Estado | Pode acompanhar tarefa e ciclo de vida | Chamada controlada pelo servidor |
| Uso | Delegação para os três agentes especializados | Consulta de políticas, saldo, fatura e solicitações |
| Conectividade | Polling, SSE/streaming ou webhook | Stdio local no protótipo |

Polling é adequado para operações simples; SSE atende atualizações progressivas de suporte; webhook é recomendado para aprovação ou fraude. MCP separa leitura de mutação e centraliza contratos de acesso.

### 7.4 Catálogo MCP

| Tipo | Capacidade | Controle |
|---|---|---|
| Recurso | Políticas públicas | Dados fictícios e filtro `publico` |
| Recurso | Saldo por referência | Requer core externo configurado |
| Recurso | Fatura por referência | Requer core externo configurado |
| Ferramenta | Consultar políticas | Retorna até quatro fontes |
| Ferramenta | Consultar saldo/fatura | Leitura externa; `not_configured` por padrão |
| Ferramenta | Criar conta | Aprovação humana obrigatória |
| Ferramenta | Solicitar cartão | Aprovação humana obrigatória |
| Prompt | Resposta fundamentada | Obriga uso de políticas e citação de origem |

### 7.5 Human-in-the-Loop

O fluxo Platinum identifica a intenção, captura estado e evidências, interrompe antes da mutação, registra snapshot e solicita decisão de pessoa autorizada. A aprovação retoma o fluxo; o cancelamento encerra com motivo auditável. O servidor MCP repete o controle e recusa mutações sem sinal explícito. Em produção, ainda são necessários identidade do aprovador, segregação de funções, SLA, política de expiração, assinatura do evento e armazenamento imutável da decisão.

## 8. Interface, publicação e operação

A interface Gradio recebe uma pergunta, executa o grafo e exibe classificação e resposta. O README apresenta motivação, arquitetura, tecnologias, decisões, aprendizados, comandos e limites. Diagramas Mermaid são versionados junto aos SVGs exportados. O GitHub Pages e a planilha Google estão referenciados no README.

O ambiente declara dependências em `requirements.txt`, usa `.env.example` como contrato e ignora `.env`, índices Chroma e saídas temporárias. `scripts/setup_runtime.py` prepara o runtime; `scripts/start_bytebank_mcp.ps1` inicia o servidor MCP; `package.json` orquestra sintaxe, testes e conformidade.

## 9. Segurança e conformidade

### 9.1 Controles implementados

- dados e políticas são fictícios;
- `.env` é ignorado e não deve ser versionado;
- modo local impede chamadas externas inesperadas;
- filtro de acesso ocorre antes dos retrievers;
- fontes e modos são registrados por caso;
- erros de API permanecem visíveis como fallback;
- mutações MCP exigem aprovação humana;
- sem endpoint/token, o core externo permanece desabilitado;
- logs não devem armazenar tokens, cabeçalhos ou dados pessoais.

### 9.2 Higiene da entrega final

A preparação final removeu do arquivo-fonte de requisitos um valor local com formato de credencial e descartou conteúdo operacional alheio ao desafio. O arquivo `.env` permanece ignorado e é o único local previsto para configuração de chave. A varredura anterior à publicação confirmou ausência de credenciais nos arquivos destinados ao commit e em todo o histórico Git alcançável. Logs de depuração também foram excluídos e passaram a ser ignorados por padrão.

## 10. Testes, validações e integridade técnica

### 10.1 Suíte automatizada

| Grupo | Cobertura | Resultado |
|---|---|---|
| RAG | Carga, chunking, metadados, acesso, recuperação vetorial, reranking e geração | Aprovado |
| Avaliação | Comparação dos dois caminhos, juiz e rastreabilidade | Aprovado |
| Multiagente | Três rotas, Gemini/fallback e HITL Platinum | Aprovado |
| MCP | Bloqueio de mutações e protocolo JSON local | Aprovado |
| Sintaxe | `compileall` em `src`, `scripts` e `tests` | Aprovado |
| Conformidade | Arquivos, CSVs, metadados, roteamento e 8 para 4 | `CONFORMIDADE=OK` |

A execução final registrou 14 testes unitários aprovados. Houve aviso não fatal do Pydantic Settings sobre uma referência de tipo em dependência externa; nenhum teste falhou.

### 10.2 Histórico Git

O objeto de commit `8f2a23a...`, pai do `HEAD`, estava ausente localmente. O histórico alcançável de `main` foi transferido novamente do `origin`, restaurando o objeto sem alterar arquivos de trabalho. Depois da recuperação, `git cat-file` reconhece o objeto como commit, `git log` exibe os commits e `git fsck --full` termina com código zero. Árvores `dangling` indicadas pelo fsck são objetos não referenciados e não constituem corrupção do histórico alcançável.

### 10.3 Utilitário PDF

`pdftotext` está instalado no `PATH` pelo pacote Poppler 25.07.0. A versão foi validada e uma extração real recuperou texto do PDF renderizado deste padrão de relatório. O PDF original do questionário possui páginas iniciais baseadas em imagem; nessas páginas, `pdftotext` retorna apenas separadores. OCR é uma capacidade distinta e não foi instalada automaticamente.

## 11. Matriz final de aceite

| ID | Critério | Evidência | Status |
|---|---|---|---|
| 1.1 | Composição do time com mínimo de cinco papéis | CSV e planilha Google | FEITO |
| 1.2 | Carreira em Y | CSV e planilha Google | FEITO |
| 1.3 | Princípios éticos e conformidade | Documento de governança | FEITO |
| 1.4 | Causas e mitigação de alucinações | Documento de governança | FEITO |
| 1.5 | Quatro pilares de LLM Ops | Documento de governança | FEITO |
| 1.6 | README e GitHub Pages | README, index e site | FEITO |
| 2.1 | Diagrama RAG completo | Mermaid e SVG | FEITO |
| 2.2 | Comparação de vector stores | ADR RAG | FEITO |
| 2.3 | Glossário com 15 termos | CSV e planilha Google | FEITO |
| 2.4 | Decisão RAG, embeddings e metadados | ADR RAG | FEITO |
| 3.1 | Carga do CSV e metadados | Pipeline e testes | FEITO |
| 3.2 | Chunking 500/100 e categoria | Pipeline e testes | FEITO |
| 3.3 | Embeddings, Chroma e `k=4` | Pipeline e testes vetoriais | FEITO |
| 3.4 | Reranking de 8 para 4 | Pipeline e validador | FEITO |
| 3.5 | Comparação sem/com RAG | Avaliação e CSV | FEITO |
| 3.6 | Oito perguntas e gabaritos | Código de avaliação | FEITO |
| 3.7 | Tabela Markdown e percentual | Documento e CSV de avaliação | FEITO |
| 3.8 | Fontes, modos e fallbacks | CSV de avaliação | FEITO |
| 4.1 | Diagrama multiagente completo | Mermaid e SVG | FEITO |
| 4.2 | A2A, MCP e conectividade | Documento multiagente | FEITO |
| 4.3 | Três tipos de memória | Documento multiagente | FEITO |
| 4.4 | HITL Platinum | Documento, grafo e testes | FEITO |
| 4.5 | StateGraph e estado tipado | Código multiagente | FEITO |
| 4.6 | Três rotas e Mermaid | Código, diagrama e testes | FEITO |
| 4.7 | Interface Gradio | `src/app.py` | FEITO |
| 4.8 | Recursos, ferramentas e prompts MCP | Servidor e testes | FEITO |
| 4.9 | README final | README | FEITO |
| V.1 | 14 testes unitários | Execução local | FEITO |
| V.2 | Validador de conformidade | `CONFORMIDADE=OK` | FEITO |
| V.3 | Histórico Git operacional | `git log` e `git fsck` | FEITO |

## 12. Riscos residuais e limitações

- O embedding compacto não é específico para português; comparar modelos multilíngues com recall, latência e custo.
- O mesmo provedor pode gerar e julgar; usar juiz independente e amostragem humana.
- Uma rodada externa completa pode realizar até 40 chamadas; controlar orçamento, taxa e retentativas.
- A cota HTTP 429 demonstra dependência operacional do provedor; implementar backoff, filas e limites.
- Agent Cards, URLs e HITL são protótipos; não representam serviços bancários publicados.
- O core externo não foi fornecido; saldo, fatura e mutações permanecem desabilitados.
- A segurança de segredos depende de manter chaves exclusivamente no `.env` ignorado e de revisar o conjunto preparado antes de cada publicação.
- O PDF de entrada baseado em imagem exige OCR para extração textual completa.

## 13. Recomendações e próximos passos

- manter credenciais exclusivamente em `.env`, rotacioná-las quando houver suspeita de exposição e repetir a varredura antes de cada publicação;
- estabelecer RBAC real para `nivel_acesso` e testes de tentativa de bypass;
- escolher embeddings multilíngues e executar benchmark de recuperação;
- separar modelo gerador e juiz e ampliar o dataset de avaliação;
- configurar rate limiting, backoff e observabilidade de custos do Gemini;
- definir API de homologação, contratos, scopes e cofre de segredos;
- implementar persistência de snapshots HITL e identidade do aprovador;
- adicionar testes end-to-end da interface e do servidor MCP;
- executar DAST/SAST, revisão LGPD e threat modeling antes de qualquer dado real;
- habilitar OCR somente se a extração de PDFs digitalizados fizer parte do escopo operacional.

## 14. Reprodução

```powershell
.\.venv\Scripts\Activate.ps1
python scripts/setup_runtime.py
python -m unittest discover -s tests -v
python scripts/validate_project.py
python -m src.rag_pipeline --mode local --retrieval chroma
python -m src.evaluation --mode local --retrieval chroma
python -m src.multiagent_graph --mode auto
.\scripts\start_bytebank_mcp.ps1
```

Para validar o utilitário PDF:

```powershell
pdftotext -v
pdftotext -layout arquivo.pdf arquivo.txt
```

## 15. Conclusão

A implementação atende os quatro entregáveis centrais e apresenta evidência executável, documental e visual. O principal resultado técnico é a combinação de recuperação autorizada, rastreabilidade de fontes, fallbacks explícitos e aprovação humana antes de mutações. A entrega final foi higienizada, validada e preparada para publicação; eventual promoção para produção ainda depende de integração homologada, identidade, segurança operacional e maior cobertura de avaliação.

**GitHub Pages:** https://fredjml.github.io/aluraCarreiraEspecialistaIANivel2B/

**Pull Request de referência:** https://github.com/fredjml/aluraCarreiraEspecialistaIANivel2B/pull/1

**Repositório:** https://github.com/fredjml/aluraCarreiraEspecialistaIANivel2B

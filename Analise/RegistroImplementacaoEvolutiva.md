# Registro da Implementação Evolutiva — GeoAI Mentor

Este arquivo é a fonte técnica consolidada para o relatório final da evolução. Cada portão registra escopo, decisões, evidências, métricas e pendências.

## Portão 0 — Linha de base

- Situação: aprovado.
- Evidências: aplicação compilável, credencial fora do Git e suíte inicial aprovada.
- Decisão: preservar o índice Git existente e evoluir sem criar commits automáticos.

## Portão 1 — Separação arquitetural

- Situação: aprovado.
- Implementação: camadas `interfaces`, `application`, `domain`, `infrastructure` e `config`.
- Evidência: Streamlit e CLI consomem `MentorService`; LangChain e OpenAI permanecem na infraestrutura.

## Portão 2 — Persistência SQLite

- Situação: aprovado.
- Implementação: SQLite como fonte oficial, transação única para pergunta e resposta, isolamento por conversa e exclusão em cascata.
- Evidências: recuperação após nova instância, atomicidade e isolamento validados por testes.

## Portão 3 — Cobertura e qualidade

- Situação: aprovado em 17/08/2026.
- Implementação: `pytest-cov` e limite obrigatório de cobertura no `pytest.ini`.
- Resultado: 37 testes aprovados; cobertura total de 86,69%; aplicação, configuração, domínio, gateway e recuperação local com 100%; persistência com 98%.
- Critério mínimo: cobertura geral >= 85%, componentes críticos >= 90% e nenhuma chamada real à API nos testes padrão.

## Portão 4 — Gerenciamento completo de sessões

- Situação: aprovado em 17/08/2026.
- Implementação: criar, listar, reabrir, renomear e excluir conversas; título automático pela primeira pergunta; migração compatível da tabela `conversations`.
- Evidências: ciclo completo validado no repositório e no serviço; reabertura recompõe o estado visual do Streamlit.

## Portão 5 — Piloto RAG controlado

- Situação: aprovado em 17/08/2026 para escopo piloto.
- Implementação: recuperação lexical somente em arquivos Markdown da pasta autorizada `knowledge_base`; nomes das fontes são enviados no contexto; ausência de evidência é explicitada.
- Segurança: sem ingestão automática, sem banco vetorial externo e sem envio prévio de documentos a terceiros.
- Evidências: recuperação pertinente, recusa fora do domínio e inclusão da fonte no contexto validadas por testes.
- Limite conhecido: base pequena, local e ainda sem fontes institucionais externas.

## Portão 6 — Prontidão operacional e piloto com usuários

- Situação: em execução.
- Objetivo: preparar operação controlada antes de qualquer uso produtivo.

### Critérios técnicos

- retenção e expiração configuráveis;
- backup e restauração verificáveis do SQLite;
- limites de timeout e tamanho da resposta da API;
- logs sem chave, conteúdo de conversa ou dados sensíveis;
- testes de concorrência e recuperação;
- instruções operacionais reproduzíveis.

### Critérios que exigem validação externa

- autenticação e identidade dos usuários do ambiente de publicação;
- infraestrutura de hospedagem controlada;
- fontes institucionais aprovadas para o RAG;
- piloto com geocientistas e feedback registrado;
- responsáveis por retenção, incidentes, custos e aprovação de produção.

### Registro de execução

- Situação técnica local: aprovada em 17/08/2026.
- Situação integral do portão: parcialmente aprovada; aguarda validações externas.
- Retenção: `GEOAI_RETENTION_DAYS`, padrão de 90 dias, com exclusão baseada na última atualização e teste que preserva conversas recentes.
- Backup: API nativa de backup do SQLite, fechamento explícito da conexão e teste de restauração das mensagens.
- Limites da API: timeout padrão de 30 segundos e máximo padrão de 1.200 tokens de saída.
- Logs: filtro de redação para padrões de chave e atribuições `OPENAI_API_KEY`; o código não registra perguntas ou respostas.
- Concorrência: 12 gravações paralelas em quatro workers permaneceram isoladas e completas.
- Operação: `scripts/operacoes_geoai.py` fornece status, backup e aplicação manual da retenção.
- Resultado final desta rodada: 49 testes aprovados, cobertura total de 88,50%, compilação aprovada e nenhuma chamada real à API.

### Pendências para aprovação integral

- escolher a plataforma de hospedagem e o provedor de identidade;
- implementar autenticação e separação dos dados conforme a identidade fornecida pela plataforma;
- aprovar formalmente retenção, responsáveis, restauração e resposta a incidentes;
- substituir ou ampliar a base piloto com fontes institucionais autorizadas;
- executar piloto com geocientistas e registrar métricas e feedback;
- definir orçamento, alertas e responsáveis pelo consumo da API.

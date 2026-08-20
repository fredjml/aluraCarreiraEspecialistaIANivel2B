# Relatório Executivo de Análise

## Hermex Log — Desafio Especialista em IA, Nível 1

**Data da análise:** 19/08/2026  
**Fonte analisada:** `projNivel1EspIAB.txt`, contendo o enunciado, os datasets de referência e o prompt de trabalho.  
**Escopo desta entrega:** estudo detalhado, preparação da execução, riscos, decisões, testes e critérios de aceite. Nenhuma conta, integração, workflow, dashboard ou base externa foi criada ou alterada.

## 1. Resumo executivo

A Hermex Log precisa conectar quatro capacidades: padronização de prazos para vendas, desenho do pós-vendas, tratamento automatizado de NPS e gestão de indicadores/documentação. O desafio combina análise de processos, modelagem de responsabilidades, automação low-code, integração com APIs de IA, visualização de dados e governança de conhecimento.

O trabalho é tecnicamente viável, mas não é um único desenvolvimento local. A maior parte da implementação ocorre em SaaS externos e exige autenticação, permissões, chaves e decisões de negócio. A execução pode ser conduzida diretamente com assistência no workspace e navegação orientada, desde que o usuário forneça ou autorize os acessos e confirme as decisões listadas neste relatório. Segredos não devem ser enviados ao chat; devem ser inseridos diretamente nos formulários ou credenciais das plataformas.

**Conclusão executiva:** a sequência correta é definir a fonte oficial dos SLAs e o contrato de dados, validar as regras de NPS e o destinatário de e-mail, então implementar na ordem 1 → 2 → 3 → 4. O principal risco de retrabalho é automatizar antes de resolver a inconsistência entre prazos específicos e prazos regionais.

## 2. Evidência e método da análise

### 2.1 Material verificado

- O arquivo local existe e foi lido integralmente até o fim do conteúdo disponível.
- O enunciado contém quatro etapas, pré-requisitos, datasets, dicas de troubleshooting e requisitos de aceite implícitos.
- O dataset `pesquisa_satisfacao` descreve 60 pedidos, de P001 a P060, com datas, UF, nota NPS e comentário.
- O dataset `handoff_vendas_posvenda` apresenta 30 pedidos, de P001 a P030, com dados de contato, valor, pagamento, responsável e observações.
- O mesmo arquivo inclui um prompt posterior que pede a execução da implementação. Nesta entrega, ele foi tratado como contexto futuro e não como autorização, pois a solicitação atual determina explicitamente “neste momento você não executará nada”.
- Não foi localizado um relatório-modelo separado anexado ao workspace. Assim, a estrutura deste documento preserva o espírito pedido: visão executiva, passo a passo, riscos, testes, evidências e aceite.

### 2.2 Verificações estáticas realizadas

| Verificação | Resultado | Evidência |
|---|---|---|
| Existência do arquivo de referência | Feita | `projNivel1EspIAB.txt` presente no workspace |
| Identificação das quatro etapas | Feita | Seções 1ª, 2ª, 3ª e 4ª do enunciado |
| Identificação dos entregáveis | Feita | Bloco de notas, Miro, Sheets, GPT, n8n, Looker Studio e Notion |
| Identificação das dependências externas | Feita | Google, ChatGPT Plus, n8n, Miro, Notion e Gemini API |
| Verificação do tamanho declarado dos datasets | Feita | 60 respostas NPS e 30 registros de handoff conforme os blocos fornecidos |
| Execução de integrações externas | Não realizada por escopo | Nenhuma conta ou serviço foi acessado |

## 3. Objetivos, persona e fronteiras

### 3.1 Objetivos de negócio

1. Reduzir promessas divergentes de prazo feitas pela equipe comercial.
2. Tornar explícito o handoff entre vendas e pós-vendas.
3. Fazer reclamações de NPS chegarem à equipe correta com contexto suficiente para ação humana.
4. Permitir à liderança acompanhar tendências, diferenças regionais, SLA e volume de detratores.
5. Criar documentação semântica confiável para atendimento e futura recuperação por chatbot.

### 3.2 Personas necessárias

**Persona primária — Analista comercial:** precisa consultar rapidamente um prazo por UF e tipo de frete. Tem baixa tolerância a respostas longas e precisa de uma saída padronizada, sem promessas não autorizadas.

**Persona operacional — Analista de pós-vendas:** recebe handoffs e alertas de detratores. Precisa do pedido, cliente, nota, comentário, categoria e próximo passo; não deve depender de interpretar dados incompletos.

**Persona gestora — Liderança:** acompanha tendências, diferenças regionais, SLA e volume de detratores para priorizar melhorias.

**Persona de governança — Dono do processo/conhecimento:** mantém SLAs, política de devolução e reembolso corretos e aprova alterações que afetem respostas automatizadas.

**Persona do assistente — Hermex Prazos:** assistente logístico profissional, objetivo, conservador e rastreável. Consulta somente a tabela aprovada, explicita que o prazo é estimativa, pede o dado faltante e recusa inventar informação. Não deve expor raciocínio interno detalhado; deve retornar apenas justificativa operacional curta e a tabela solicitada.

### 3.3 Fora do escopo

- Criar contas ou aceitar termos em nome do usuário.
- Enviar e-mails reais sem destinatário e autorização definidos.
- Tomar decisão automática de reembolso, devolução ou compensação.
- Substituir aprovação humana para reclamações.
- Usar dados pessoais reais ou publicar chaves/API tokens no relatório.

## 4. Conhecimentos necessários

### 4.1 Negócio e processos

- Logística de última milha, dias úteis, regiões brasileiras e exceções de endereço.
- Definição de SLA, lead time, data de corte, feriados, fins de semana e frete expresso.
- Jornada pós-venda: envio, rastreio, entrega, pesquisa, detrator, triagem e encerramento.
- RACI: diferença entre Responsible, Accountable, Consulted e Informed; uma atividade deve ter um A claro.
- NPS: promotores 9–10, neutros 7–8, detratores 0–6; fórmula e interpretação.

### 4.2 Dados e qualidade

- CSV, cabeçalho, tipos, datas ISO, UTF-8, acentuação e separadores.
- Chave de pedido, unicidade, campos obrigatórios e relacionamento entre handoff e pesquisa.
- Validação de nota no intervalo 0–10 e datas em ordem: pedido ≤ envio ≤ recebimento.
- Privacidade e minimização de PII: e-mail e telefone devem ser tratados apenas nos sistemas autorizados.
- Métricas agregadas, filtros por UF e cuidado com amostra pequena por estado.

### 4.3 IA e prompt engineering

- Instruções de sistema, limites de conhecimento, exemplos de entrada/saída e fallback.
- Classificação fechada, normalização da resposta e validação do rótulo retornado.
- Alucinação, prompt injection em comentários livres, dados sensíveis e revisão humana.
- Diferença entre pedir um procedimento observável e exigir cadeia de pensamento privada. O teste deve verificar o resultado, não solicitar raciocínio oculto.

### 4.4 Integração e automação

- OAuth do Google, credenciais n8n, webhooks/gatilhos por nova linha e idempotência.
- Expressões n8n, tratamento de campos ausentes, ramificação IF e retries.
- API Gemini, limites, erros, timeout e resposta fora da enumeração.
- Gmail, remetente, destinatários, ambiente de teste e prevenção de envio duplicado.

### 4.5 Visualização e conhecimento

- Looker Studio: fontes, tipos geográficos, campos calculados, agregação e filtros.
- Modelagem de NPS e SLA em percentual, pontos e dias; legenda acessível e escalas coerentes.
- Notion: database, páginas, metadados de versão, proprietário, revisão e validade.
- Chunking semântico, linguagem clara e atualização controlada para futura busca por IA.

## 5. Softwares, serviços e acessos

### 5.1 Necessários para a implementação

| Recurso | Uso | Instalação local? | Observação |
|---|---|---:|---|
| Navegador atualizado | Acesso a todas as plataformas | Não | Chrome/Edge recomendado |
| Editor de texto/Bloco de Notas | Planejamento, CSD e governança | Não | Pode ser VS Code |
| Conta Google | Sheets, Forms, Looker Studio e Gmail | Não | Necessita permissões de edição |
| Google Drive | Pasta e organização de artefatos | Não | Pasta “Hermex Log — Projeto NPS” |
| ChatGPT Plus | GPT personalizado | Não | Necessário para criar GPTs customizados |
| n8n Cloud | Workflow e credenciais | Não | Plano gratuito pode bastar; confirmar limites atuais |
| Miro | Fluxograma | Não | Permissão de edição no board |
| Notion | Base de conhecimento | Não | Workspace e database |
| Google AI Studio/Gemini API | Classificação de comentários | Não | Chave e quota; nunca registrar no relatório |
| TempEmail ou caixa de teste | Validação de mensagens | Não | Opcional; confirmar política e disponibilidade |

### 5.2 Necessários para produzir evidências

- Capturas ou links compartilháveis do GPT, board Miro, planilhas, workflow, dashboard e database Notion.
- IDs/nomes dos recursos e data da última atualização.
- Histórico de execução do n8n e outputs anonimizados.
- E-mails de teste ou cabeçalhos, sem expor conteúdo pessoal desnecessário.
- Exportações PDF/CSV/JSON quando a plataforma permitir.

Não há software local obrigatório além de navegador e editor. O DOCX e o Markdown desta análise foram gerados no workspace; isso não substitui as ferramentas SaaS requeridas pelo desafio.

## 6. Análise profunda das quatro etapas

### Etapa 1 — Assistente Hermex Prazos

**Entrada:** UF, tipo de frete e, quando aplicável, condições especiais.  
**Regra:** normalizar UF, mapear região, consultar tabela aprovada e responder com mínimo/máximo em dias úteis e observação.  
**Saída:** tabela com Estado, Prazo mínimo, Prazo máximo e Observações.

**CSD inicial:**

| Categoria | Item | Tratamento |
|---|---|---|
| Certeza | SP tem referência de 2–4 dias úteis | Pode ser usado somente como regra aprovada |
| Suposição | Norte/Nordeste podem ficar entre 8–15 dias úteis | Não apresentar como fato até aprovação |
| Dúvida | Existe frete expresso para toda região? | Perguntar ou retornar “não informado” |
| Dúvida | Feriados e áreas remotas alteram o SLA? | Registrar decisão antes do prompt final |
| Risco | Etapa 4 define faixas regionais diferentes | Resolver conflito com um catálogo oficial versionado |

**Briefing recomendado:** o assistente deve responder somente com dados da tabela; se UF ou modalidade não estiverem cobertos, declarar ausência de dados. Deve descrever quatro operações observáveis: ler a entrada, identificar a região, consultar a tabela, formatar a resposta. Não deve revelar cadeia de pensamento privada.

**Testes sugeridos:** SP, BA e AM; entrada com nome de cidade, UF inválida, modalidade não informada e pedido para inventar prazo.  
**Resultado da análise:** casos e critérios estão definidos; resultados reais dependem da criação do GPT.

### Etapa 2 — Processo, automação e RACI

**Fluxo mínimo:** Pedido enviado → registrar handoff → notificar pós-vendas → verificar entrega → [confirmada?] não: aguardar e verificar novamente; sim: enviar pesquisa → classificar feedback → [insatisfeito?] sim: notificar equipe; não: encerrar → ciclo encerrado.

**Candidatos à automação:** registro e notificação do handoff, consulta recorrente de entrega, envio da pesquisa, classificação, alerta e rastreabilidade. Cada marcação deve indicar repetitividade, regras claras, transferência, criticidade e/ou rastreabilidade.

**RACI mínimo a validar:** vendas inicia e fornece dados; pós-vendas executa tratamento e é A pelo atendimento; n8n é R por executar automações; correios é C/R na confirmação conforme integração; liderança é A ou C de políticas, nunca um A genérico em tudo.

**Resultado da análise:** o handoff é o ponto crítico porque transfere informação entre equipes, é repetitivo, possui regras claras e cria rastreabilidade. O dataset de handoff tem apenas 30 pedidos, enquanto o NPS tem 60; a cobertura e a chave de cruzamento devem ser validadas antes de usar os dois como uma única fonte.

### Etapa 3 — Workflow NPS no n8n

**Fluxo proposto:** nova resposta Google Forms/Sheets → validar campos → IF nota < 6 → Gemini com enumeração fechada → normalizar categoria → Gmail para pós-vendas; caso contrário → Gmail de agradecimento ao cliente. Deve haver log, idempotência, erro tratado e validação humana.

**Categorias permitidas:** Atraso, Defeito, Atendimento, Embalagem, Outro. A classificação não deve ser o único fundamento para decisão financeira ou resposta definitiva ao cliente.

**Pontos a corrigir no desenho:** o gatilho precisa receber nome de cliente e e-mail, mas o formulário listado contém apenas ID, nota e comentário. Definir se esses dados virão de uma busca no handoff ou se serão adicionados ao Forms. Também decidir se nota 6 é detrator; pela regra `< 6`, nota 6 segue o caminho positivo/neutro, embora a convenção NPS normalmente trate 0–6 como detrator.

**Testes sugeridos:** detrator com atraso, detrator com defeito, promotor ≥ 9, nota 6, categoria inesperada, comentário vazio, timeout Gemini, falha Gmail e repetição do mesmo evento.  
**Resultado da análise:** arquitetura identificada; nenhum workflow foi executado.

### Etapa 4 — Looker Studio e Notion

**Métricas:** Promotores = nota > 8; Detratores = nota < 7; NPS = proporção de promotores menos proporção de detratores; dias até envio e entrega como diferenças de datas. Confirmar se o scorecard deve exibir fração formatada como percentual ou o índice convencional de -100 a 100.

**Visualizações:** scorecards, mapa por UF, barras de média de entrega por UF e tabela analítica. Para estados com amostra pequena, exibir quantidade de respostas junto da média e evitar conclusões fortes.

**Notion:** database “Processos Hermex Log” com Política de Devolução, Processo de Reembolso e SLA regional. Cada página precisa de proprietário, versão, data de revisão, validade e fonte de aprovação.

**Resultado da análise:** o dashboard e a base atendem públicos diferentes, mas devem compartilhar definições e versão do SLA. A documentação semântica é adequada para futura busca por IA porque expressa regras, exceções e contexto; dados brutos continuam necessários para métricas e auditoria.

## 7. Inconsistências e decisões obrigatórias

| Tema | Conflito/lacuna | Decisão recomendada |
|---|---|---|
| SLA | SP 2–4 dias; regional Sudeste 2–5 | Escolher catálogo oficial e versioná-lo |
| Norte/Nordeste | CSD cita 8–15; Notion cita Norte 8–16 e Nordeste 6–12 | Aprovar faixas por região antes do GPT |
| NPS | IF do desafio usa nota < 6; fórmula usa < 7 | Adotar convenção 0–6 ou seguir literalmente, documentando |
| Formulário | Campos não incluem nome/e-mail, mas Gmail exige ambos | Enriquecer pela chave do pedido ou adicionar campos |
| Dataset | NPS tem P001–P060; handoff tem P001–P030 | Definir fonte de enriquecimento e comportamento sem correspondência |
| Tipo de frete | É critério de resposta, mas não há tabela por modalidade | Definir modalidades e prazos ou declarar “não informado” |
| Datas | Regras dizem dias úteis; DATE_DIFF mede dias corridos | Decidir se dashboard usa dias corridos ou cálculo útil |
| E-mail | Destinatário da equipe não foi informado | Fornecer caixa de teste e caixa operacional |
| Privacidade | Dados têm e-mails e telefones fictícios, mas fluxo real pode ter PII | Definir retenção, compartilhamento e anonimização de evidências |
| Evidência | Não há relatório-modelo separado no workspace | Usar este relatório como modelo executivo e anexar links depois |

## 8. Plano de implementação futuro

1. Aprovar decisões da seção 7 e criar catálogo de SLA versionado.
2. Criar pasta, planilhas, permissões e importar dados; validar schema e chaves.
3. Produzir planejamento, CSD e briefing; criar e testar GPT.
4. Mapear fluxo no Miro e aprovar RACI.
5. Criar Forms e workflow n8n em ambiente de teste; integrar Gemini e Gmail.
6. Executar testes positivos, negativos, falhas e duplicidade; registrar evidências.
7. Construir dashboard e validar fórmulas com cálculo independente.
8. Criar Notion, aplicar governança e revisar semântica dos textos.
9. Fazer revisão de aceite, segurança, privacidade e handoff operacional.

## 9. Estratégia de testes e evidências

| Área | Teste | Evidência esperada |
|---|---|---|
| GPT | SP, BA, AM e UF desconhecida | Transcrições/capturas, tabela correta e fallback |
| RACI | Cada atividade tem R e um A | Link/captura da aba e revisão aprovada |
| Dados | Campos obrigatórios, tipos e chaves | Cabeçalho, contagem e validação documentada |
| n8n | Detrator e promotor | Execuções, ramo seguido, output Gemini e e-mail de teste |
| n8n | Nota 6, comentário vazio e categoria inválida | Registro de regra e tratamento de erro |
| Gmail | Variáveis dinâmicas | Mensagens anonimizadas/cabeçalhos de teste |
| Dashboard | Fórmulas e filtros por UF | Capturas, fonte e cálculo de conferência |
| Notion | Três páginas e metadados | Link/captura do database e versão |
| Governança | Revisão e proprietário | Documento com responsáveis, periodicidade e risco |

## 10. Critérios de aceite do levantamento

Os critérios abaixo avaliam esta entrega de análise, não a implementação SaaS. Todos estão **feito** porque foram cobertos no relatório e não exigem execução externa nesta fase.

| ID | Critério | Status | Evidência |
|---|---|---|---|
| AL-01 | Desafio e arquivo local analisados | feito | Seções 2 e 6 |
| AL-02 | Quatro etapas de negócio decompostas | feito | Seção 6 |
| AL-03 | Conhecimentos técnicos e de negócio identificados | feito | Seção 4 |
| AL-04 | Persona definida | feito | Seção 3.2 |
| AL-05 | Softwares, contas e instalação distinguidos | feito | Seção 5 |
| AL-06 | Riscos e inconsistências registrados | feito | Seção 7 |
| AL-07 | Decisões necessárias para execução listadas | feito | Seção 7 |
| AL-08 | Passos de implementação futura descritos | feito | Seção 8 |
| AL-09 | Testes e evidências sugeridos | feito | Seção 9 |
| AL-10 | Três análises críticas realizadas | feito | Seção 11 |
| AL-11 | Três revisões realizadas | feito | Seção 12 |
| AL-12 | Relatórios MD e DOCX preparados | feito | Arquivos em `Analise` |

## 11. Três análises críticas do levantamento

### Análise crítica 1 — Completude

O levantamento cobre objetivos, personas, conhecimentos, ferramentas, dados, etapas, riscos, testes, evidências e aceite. A revisão do texto revelou que não bastava repetir o enunciado: era necessário identificar o contrato de dados ausente, as divergências de SLA e a fronteira entre análise e execução. Esses pontos foram incorporados nas seções 7 e 9.

### Análise crítica 2 — Consistência técnica

Foram confrontadas as regras de NPS, as fórmulas do dashboard, os campos do Forms e os campos exigidos pelo e-mail. A nota 6 e a ausência de nome/e-mail no formulário são ambiguidades funcionais reais. Também foi separado `DATE_DIFF` em dias corridos de SLA em dias úteis. O relatório não mascara essas questões como implementação pronta.

### Análise crítica 3 — Executabilidade e prova

Foi verificado o que pode ser feito localmente e o que depende de SaaS, credenciais e intervenção humana. As evidências sugeridas são reproduzíveis e proporcionais: links/capturas, execuções n8n, e-mails de teste, contagens, fórmulas e metadados. Nenhuma evidência de integração foi declarada como produzida nesta fase.

## 12. Três revisões aplicadas

### Revisão 1 — Requisitos

Conferidos os entregáveis, ferramentas, testes mínimos, formato das respostas, Matriz CSD, RACI, categorias Gemini, gráficos, páginas Notion e governança. Foram incluídos critérios de aceite específicos para cada requisito de análise.

### Revisão 2 — Dados e regras

Conferidas as quantidades declaradas, intervalos de IDs, campos, limiares NPS, prazos regionais e dependências entre bases. Foram registradas as divergências em vez de escolher silenciosamente uma regra.

### Revisão 3 — Segurança e operação

Incluídos PII, segredos, permissões, destinatários de teste, idempotência, falhas de API, revisão humana, versionamento do conhecimento e limites do que pode ser comprovado sem acessar as plataformas.

## 13. Posso executar a implementação diretamente?

**Sim, posso conduzir a implementação das quatro etapas, mas não de forma autônoma sem decisões e acessos do responsável.** Posso produzir os documentos, estruturar planilhas, orientar/criar configurações quando houver acesso autorizado, montar o fluxo, validar fórmulas e registrar evidências. Não posso criar contas em nome do usuário, obter credenciais por ele, aceitar termos legais, enviar comunicação real sem aprovação ou inventar regras de negócio.

### Decisões que o usuário precisa tomar antes da execução

1. Qual é a tabela oficial de SLA por UF, região e modalidade de frete?
2. A regra operacional de detrator será `nota < 6` (literal) ou `nota <= 6` (convenção NPS)?
3. O prazo do dashboard será em dias corridos ou dias úteis?
4. Como obter nome e e-mail da resposta do Forms: adicionar ao formulário ou buscar pelo `id_pedido` no handoff?
5. Qual conta Google será proprietária e quais usuários terão edição?
6. Qual endereço de teste recebe alertas de detratores e qual endereço recebe agradecimentos?
7. Qual conta/ambiente n8n será usado e o workflow poderá permanecer ativo após os testes?
8. A chave Gemini será inserida pelo usuário diretamente no n8n/AI Studio, sem ser compartilhada no chat?
9. O board Miro e o workspace Notion já existem ou devem ser criados pelo usuário?
10. Qual política de retenção, anonimização e compartilhamento deve ser aplicada às evidências?
11. A aprovação humana será obrigatória antes de qualquer resposta ao cliente ou apenas antes de reembolso/devolução?
12. Quem é o Accountable final por SLA, pós-vendas, dashboard e base Notion?

Com essas decisões e sessões autenticadas, a implementação pode ser conduzida por incrementos, com validação após cada etapa. O próximo artefato de execução deve ser um catálogo de SLA aprovado e um contrato de dados versionado.

## 14. Encerramento

O estudo atende ao objetivo de preparar a execução sem executar o desafio. Os arquivos produzidos são uma base de decisão e uma trilha de auditoria inicial. O levantamento está concluído; a implementação permanece deliberadamente pendente de aprovação das decisões e de acesso aos serviços externos.

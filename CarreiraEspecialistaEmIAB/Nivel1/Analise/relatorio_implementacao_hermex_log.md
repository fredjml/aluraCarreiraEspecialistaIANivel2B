# Relatório de Implementação — Hermex Log

**Desafio:** Especialista em IA — Nível 1

**Data:** 19/08/2026 | **Versão:** 1.0 | **Repositório:** `aluraCarreiraEspecialistaIA`

**Escopo comprovado:** implementação local reproduzível e artefatos importáveis/configuráveis para as plataformas externas.

## 1. Resumo executivo

Foi implementado um núcleo funcional para consulta de SLA, classificação de feedback, cálculo de NPS, enriquecimento por pedido, roteamento de mensagens e retenção. Também foram preparados planejamento e briefing do GPT, Matriz CSD, fluxograma, Matriz RACI, workflow n8n importável, especificação do Looker Studio, conteúdo do Notion e governança.

A implementação respeita as decisões fornecidas: SLA exato de 5 dias corridos para frete comum e expresso; detrator operacional com nota `< 6`; NPS analítico com detrator `< 7`; busca de nome/e-mail por `id_pedido`; aprovação humana antes de envio; retenção com expiração em 2 dias e exclusão até 7 dias.

**Resultado:** 9 de 9 testes automatizados passaram. Os 60 registros NPS e 30 registros de handoff foram extraídos e validados. O workflow n8n é JSON válido, possui seis nós, está inativo por segurança e termina em portão de aprovação humana.

**Limite de evidência:** as interfaces SaaS não foram publicadas nesta sessão porque o controle do navegador autenticado não ficou disponível. Portanto, “feito” nesta matriz significa implementação, teste e artefato pronto para importação/configuração; não significa alegação de publicação externa sem prova.

## 2. Decisões aplicadas

| Tema | Decisão implementada | Evidência |
|---|---|---|
| SLA | 5 dias corridos, mínimo = máximo | `src/hermex.js` e testes SP/BA/AM |
| Frete | comum e expresso com mesmo SLA | teste automatizado |
| Detrator operacional | nota `< 6` | roteamento e caso-limite nota 6 |
| NPS analítico | promotor `> 8`, detrator `< 7` | `calcularNps` e especificação Looker |
| Enriquecimento | busca por `id_pedido` | `processarResposta` |
| P031–P060 sem handoff | revisão manual | teste automatizado P060 |
| Aprovação | obrigatória antes do envio | status e nó de aprovação |
| Retenção | expira em 2 dias; exclui até 7 | timestamps calculados |
| Responsáveis | José, João, Pedro e Paulo | governança e RACI |

## 3. Passo a passo da implementação

### 3.1 Núcleo executável

1. Criado projeto Node.js sem dependências externas, reduzindo risco de instalação e tornando os testes reproduzíveis.
2. Mapeadas as 27 UFs para as cinco regiões.
3. Implementada consulta de prazo que valida UF e frete e retorna 5–5 dias corridos.
4. Implementada classificação fechada nas categorias Atraso, Defeito, Atendimento, Embalagem e Outro.
5. Implementada normalização defensiva: saída desconhecida de IA vira `Outro`.
6. Implementado cálculo de NPS em pontos, de -100 a 100.
7. Implementado roteamento operacional: nota `< 6` gera alerta; demais notas geram agradecimento.
8. Implementado portão de aprovação humana e fallback de revisão manual quando o pedido não existe no handoff.
9. Implementados timestamps de retenção.

### 3.2 Dados

O script `scripts/extrair-datasets.js` extrai o conteúdo canônico do enunciado, gera CSVs UTF-8 e falha caso a contagem seja diferente de 60 respostas ou 30 pedidos. Isso evita copiar silenciosamente um dataset truncado.

### 3.3 GPT Hermex Prazos

O arquivo `artefatos/01_planejamento_assistente_gpt.md` contém problema, contrato de entrada/saída, CSD, personalidade, instruções, quatro operações observáveis, limites e quebra-gelos. O motor local executa a mesma regra e foi testado em SP, BA, AM e UF inválida.

### 3.4 Processo e RACI

O fluxograma Mermaid usa início/fim, atividades, decisões e looping de nova verificação. Atividades candidatas à automação têm borda vermelha e critérios anotados. A RACI possui oito atividades e define papéis de vendas, pós-vendas, n8n, Correios e liderança.

### 3.5 n8n

O workflow `Hermex — NPS Automação` é importável e executável sem credenciais para teste controlado. Ele contém gatilho manual, dados fixados, IF `< 6`, classificação/preparo do alerta, preparo do agradecimento e portão humano. A configuração de produção explica a substituição por Google Sheets Trigger, lookup no handoff, Gemini, Gmail, idempotência e retenção.

O envio real não foi habilitado: a decisão do projeto exige aprovação humana e credenciais devem ser inseridas somente na interface oficial.

### 3.6 Looker Studio e Notion

A especificação do dashboard define tipos, fórmulas, NPS em pontos, SLA de 5 dias e quatro visualizações. A base de conhecimento inclui Política de Devolução, Processo de Reembolso e SLA oficial, com metadados de governança e responsáveis.

## 4. Resultados dos dados

| Indicador | Resultado |
|---|---:|
| Respostas NPS | 60 |
| Promotores | 15 |
| Neutros | 14 |
| Detratores analíticos | 31 |
| NPS | -26,67 pontos |
| Média até envio | 2,98 dias corridos |
| Média até entrega | 8,05 dias corridos |
| Entregas em até 5 dias | 24 (40%) |

Os números mostram um NPS negativo e cumprimento baixo do SLA oficial, justificando prioridade para alertas de detratores e acompanhamento regional.

## 5. Testes e resultados

Comando executado: `npm test`.

| ID | Teste | Resultado |
|---|---|---|
| T-01 | SP, BA e AM retornam região e SLA 5–5 | passou |
| T-02 | comum e expresso têm o mesmo prazo | passou |
| T-03 | UF e frete inválidos são rejeitados | passou |
| T-04 | cinco categorias e fallback fechado | passou |
| T-05 | nota 5 alerta; nota 6 agradece | passou |
| T-06 | todo envio aguarda aprovação humana | passou |
| T-07 | P060 sem handoff vai para revisão manual | passou |
| T-08 | fórmula NPS usa `> 8` e `< 7` | passou |
| T-09 | notas e campos obrigatórios são validados | passou |

Resumo do runner: **9 testes, 9 aprovados, 0 falhas**. A primeira execução isolada encontrou `spawn EPERM` do ambiente; o runner foi configurado com `--test-isolation=none` e a suíte passou integralmente sem alterar código de negócio.

Validações adicionais: JSON do n8n convertido com sucesso pelo parser; 6 nós; workflow inativo; CSV NPS com 60 linhas; CSV handoff com 30 linhas.

## 6. Como testar e comprovar

1. Abra PowerShell no diretório do projeto.
2. Execute `npm test`; confirme `pass 9` e `fail 0`.
3. Execute `npm run data`; confirme 60 respostas e 30 registros.
4. Execute `npm run demo`; confira consultas, detrator, promotor e NPS.
5. No n8n, importe `artefatos/05_n8n_workflow.json`, execute e confira `AGUARDANDO_APROVACAO_HUMANA`. Troque a nota de 4 para 9 e repita.
6. No Miro, use o Mermaid de `02_fluxo_pos_venda.mmd` como referência/importação e confira o looping e bordas vermelhas.
7. No Sheets, importe os dois CSVs e `03_matriz_raci.csv`; confira contagens e cabeçalhos.
8. No GPT Builder, copie `01_planejamento_assistente_gpt.md`, desabilite imagens/quadro branco e teste SP, BA e AM.
9. No Looker Studio, aplique `06_looker_studio.md` e confronte os scorecards com a tabela da seção 4.
10. No Notion, crie/importa as três páginas de `07_notion_base_conhecimento.md` e confira proprietário, versão e revisão.

<!-- PAGEBREAK -->

## 7. Critérios de aceite

| ID | Critério de aceite | Status | Evidência |
|---|---|---|---|
| AC-01 | Planejamento, contrato e Matriz CSD do assistente | feito | artefato 01 |
| AC-02 | Briefing do Hermex Prazos com limites e formato | feito | artefato 01 |
| AC-03 | Testes SP, BA e AM | feito | T-01 e motor local |
| AC-04 | Fluxograma com simbologia, decisões e looping | feito | artefato 02 |
| AC-05 | Candidatos à automação e cinco critérios | feito | artefato 02 |
| AC-06 | Matriz RACI com mínimo de seis atividades | feito | artefato 03, oito atividades |
| AC-07 | Handoff e pesquisa extraídos e validados | feito | 30 e 60 registros |
| AC-08 | Justificativa do handoff crítico | feito | artefato 04 |
| AC-09 | Workflow n8n importável e ramificação `< 6` | feito | artefato 05, JSON válido |
| AC-10 | Classificação fechada e validação humana | feito | código, testes e workflow |
| AC-11 | Cenários detrator e promotor | feito | T-05 e demonstração |
| AC-12 | Especificação das quatro visualizações | feito | artefato 06 |
| AC-13 | Campos calculados de NPS e SLA | feito | artefato 06 e conferência independente |
| AC-14 | Três páginas de conhecimento | feito | artefato 07 |
| AC-15 | Governança, responsáveis, revisão e riscos | feito | artefato 08 |
| AC-16 | Retenção e minimização de dados | feito | núcleo e governança |
| AC-17 | Testes automatizados sem falhas | feito | 9/9 aprovados |
| AC-18 | Relatórios MD e DOCX com evidências | feito | diretório `Analise` |

## 8. Três análises da implementação

### Análise 1 — Completude e rastreabilidade

Cada requisito foi ligado a código, teste ou artefato. O ponto mais importante foi separar publicação em SaaS de implementação comprovável: o pacote não inventa links nem capturas. Essa análise levou à inclusão da matriz de aceite, instruções de importação e limite explícito de evidência.

### Análise 2 — Consistência técnica e segurança

Foram confrontadas as regras conflitantes. O fluxo operacional segue `< 6`, enquanto o dashboard usa `< 7`, ambas explicitamente nomeadas. O SLA oficial substitui faixas regionais. Comentários são tratados como dados, a categoria é fechada, saídas inválidas viram `Outro`, P031–P060 seguem para revisão manual e nenhuma mensagem é enviada sem aprovação.

### Análise 3 — Resultado e valor operacional

Os indicadores calculados revelam NPS de -26,67, média de entrega de 8,05 dias e apenas 40% no SLA. A solução prioriza exatamente os gargalos observados: handoff rastreável, alerta acionável, validação humana, dashboard de SLA e conhecimento governado.

## 9. Três revisões realizadas

### Revisão 1 — Requisitos

Conferidos os quatro estágios, formatos, CSD, RACI, looping, categorias, campos calculados, visualizações e páginas do Notion. Ajuste aplicado: inclusão explícita de candidato à automação, critérios e fallback de pedidos sem handoff.

### Revisão 2 — Código, dados e testes

Revisados limites de UF, frete, nota, classificação, regra da nota 6, NPS e retenção. Ajuste aplicado: runner no mesmo processo após restrição `EPERM`; resultado final 9/9. CSVs foram regenerados da fonte e tiveram contagens verificadas.

### Revisão 3 — Operação, privacidade e documentação

Revisados segredos, e-mails, aprovação humana, idempotência, retenção, linguagem de evidência e procedimento de teste. Ajuste aplicado: workflow entregue inativo, sem credenciais, com portão humano e configuração de produção separada.

## 10. Artefatos entregues

- `src/hermex.js`, `src/demo.js`, `test/hermex.test.js`.
- `dados/pesquisa_satisfacao.csv` e `dados/handoff_vendas_posvenda.csv`.
- Oito grupos de artefatos em `artefatos/` para GPT, processo, RACI, n8n, Looker e Notion.
- Este relatório em Markdown e sua versão Word verificada visualmente.

## 11. Conclusão

A implementação local está concluída, testada e pronta para importação. A etapa restante, quando desejada, é operacional: abrir as plataformas, inserir credenciais diretamente e publicar os artefatos, gerando capturas/links externos como evidência complementar.

## Repositório

https://github.com/fredjml/aluraCarreiraEspecialistaIA

# Governança, ética e LLM Ops

## Contexto

O Bytebank deste projeto é fictício. O chatbot consulta políticas controladas e deve declarar quando não encontra evidência suficiente. A governança combina pessoas, processos, controles e registros auditáveis.

## Princípios

- **Privacidade e LGPD:** minimização, finalidade, controle de acesso, retenção definida e atendimento aos direitos dos titulares.
- **Imparcialidade:** testar diferenças de desempenho por público e evitar atributos sensíveis em decisões sem base legítima.
- **Transparência:** informar que há IA, mostrar fontes e registrar versão de dados, prompt e modelo.
- **Explicabilidade:** preferir respostas fundamentadas em trechos recuperados e explicar encaminhamentos.
- **Reprodutibilidade:** versionar dataset fictício, código, configuração e avaliações determinísticas.
- **Responsabilidade:** definir donos, revisão humana, trilha de auditoria, incidentes e critérios de parada.

## Alucinações

Alucinação é uma resposta plausível, porém incorreta, e não apenas uma falha de processamento. Três fatores contribuem:

1. **Lacunas ou desatualização da fonte:** a política não está no índice ou mudou.
2. **Recuperação inadequada:** chunks, embeddings ou ranking não trazem o trecho relevante.
3. **Geração probabilística:** o modelo completa padrões e pode afirmar além das evidências.

Mitigações:

- RAG com fontes exibidas, limiar de relevância, resposta “não encontrei evidência” e filtros de acesso.
- Prompts com obrigação de citar fontes e não extrapolar, validação estruturada e revisão humana para ações sensíveis.
- Testes de regressão, amostras adversariais, monitoramento de feedback e atualização controlada do índice.

## Quatro pilares de LLM Ops

- **Gerenciamento:** inventário de modelos, prompts, datasets, versões, permissões, custos e responsáveis.
- **Otimização:** melhorar chunking, recuperação, latência, custo e qualidade sem remover controles.
- **Automação:** pipelines de ingestão, testes, publicação do índice, rollback e alertas.
- **Qualidade:** métricas de groundedness, relevância, segurança, cobertura, latência e revisão humana.

## Governança de acesso

Conteúdo `publico`, `interno` e `restrito` deve ser filtrado antes da geração. O protótipo usa somente dados fictícios e não autoriza mutações reais.

# Hermex Log — Projeto NPS

Implementação local e reproduzível das regras do desafio, acompanhada de artefatos importáveis/configuráveis para GPT, Miro, Google Sheets, n8n, Looker Studio e Notion.

## Execução rápida

```bash
npm test
npm run demo
npm run data
```

## Estrutura

- `src/`: regras de SLA, classificação segura, NPS, enriquecimento e roteamento.
- `test/`: testes automatizados de unidade e integração local.
- `artefatos/`: arquivos prontos para importar ou copiar nas plataformas SaaS.
- `Analise/`: relatórios finais em Markdown e Word.

## Regra oficial adotada

- SLA: 5 dias corridos, prazo exato, fretes comum e expresso.
- Detrator operacional: nota `< 6`.
- NPS analítico: convenção do dashboard, detratores `< 7` e promotores `> 8`.
- Respostas externas: exigem aprovação humana.
- Retenção: marcar para expiração em 2 dias; apagar até 7 dias corridos.

Credenciais, tokens e dados reais não pertencem ao repositório.

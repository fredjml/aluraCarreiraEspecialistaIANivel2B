# Análise 3: riscos residuais

1. O modelo de embeddings é compacto e não especializado em português; a fusão
   lexical reduz o risco, mas deve ser comparada a embeddings multilíngues.
2. O mesmo modelo pode gerar e julgar uma resposta, introduzindo viés. Uma
   evolução deve usar amostragem humana ou modelo juiz independente.
3. Uma rodada Gemini completa faz até 40 chamadas; cota, custo e latência devem
   ser monitorados.
4. A cota Gemini gerou HTTP 429 em parte da rodada; produção requer orçamento,
   limitação de taxa e modelo juiz independente.
5. Agent Cards e HITL permanecem protótipos; não representam serviços bancários
   publicados nem aprovação financeira real.

**Mitigação:** manter testes locais, registrar fallbacks, medir recall e
groundedness, revisar amostras e exigir decisão humana para mutações.

# Maturidade e evolucao tecnica

## Controles implementados

| Area | Implementacao | Evidencia |
|---|---|---|
| Cota Gemini | Backoff exponencial com jitter, limite local por minuto e retries de HTTP 429 | `src/gemini_integration.py` e campos de metricas no CSV |
| Avaliacao | Clientes e modelos configuraveis separadamente para geracao e julgamento | `BYTEBANK_GENERATOR_MODEL` e `BYTEBANK_JUDGE_MODEL` |
| Autorizacao | JWT com validacao de assinatura, emissor, audiencia e expiracao; permissao derivada de papel | `src/identity.py` e `tests/test_mcp_server.py` |
| HITL | Mutacoes exigem identidade com papel `aprovador` ou `administrador`, alem da aprovacao explicita | `scripts/bytebank_mcp_server.py` |
| E2E | Browser Gradio e sessao MCP stdio oficial, executados pelo CI | `tests/test_gradio_e2e.py`, `tests/test_mcp_protocol_e2e.py` e `.github/workflows/ci.yml` |

## Configuracao JWT

Para demonstracao local, configure `BYTEBANK_JWT_ISSUER`,
`BYTEBANK_JWT_AUDIENCE` e uma chave publica ou segredo local. Em ambiente
integrado, use um emissor OIDC homologado, JWKS rotacionado e algoritmo
assimetrico. O repositorio nao inclui chaves, tokens, URLs ou identidades reais.

Os papeis permitidos sao `cliente`, `atendente`, `analista`, `aprovador` e
`administrador`. Sem token, a regra e negar por padrao, exceto por politicas
publicas. Um aprovador deve ser registrado por um servico de auditoria externo
antes de qualquer integracao real de mutacao.

## Pendencias para producao

1. Integrar um servidor OIDC/JWKS de homologacao e auditoria persistente de HITL.
2. Reduzir os quatro fallbacks de julgamento observados na rodada Gemini de 32 casos e repetir a medição com juiz externo em todos os casos.
3. Configurar gerador e juiz com provedores ou famílias de modelos distintos e registrar a revisão humana de uma amostra.
4. Homologar um core bancario estritamente ficticio, auditoria persistente de HITL e isolamento por tenant.

Os controles locais tornam essas pendencias rastreaveis, mas nao representam
certificacao ou autorizacao de producao.
# Revisão 2: segurança e conformidade

**Escopo:** segredos, dados, níveis de acesso, MCP e rastreabilidade.

**Resultado:** aprovada para protótipo. `.env` é ignorado, a chave não é
impressa, o dataset é fictício e o filtro de acesso ocorre antes dos retrievers
Chroma e lexical. O modo `local` impede chamadas externas; erros são registrados.
As ferramentas MCP de mutação exigem aprovação humana explícita.

**Ponto de atenção:** em produção, identidade e papéis reais devem alimentar
`allowed_levels`; logs devem continuar sem tokens, cabeçalhos ou dados sensíveis.

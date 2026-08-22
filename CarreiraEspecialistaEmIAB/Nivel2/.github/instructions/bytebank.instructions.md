---
description: "Regras para documentação e código do projeto fictício Bytebank Nivel2"
applyTo: "**/*"
---

- Preserve o contexto fictício do Bytebank e nunca use dados reais.
- Não grave credenciais, tokens, URLs públicas ou identificadores pessoais.
- Marque como pendente qualquer avaliação, integração ou publicação que não tenha sido executada.
- Prefira soluções locais determinísticas quando APIs externas não estiverem configuradas.
- Em RAG, preserve `id`, `dominio`, `secao`, `nivel_acesso` e `categoria_semantica`.
- Diferencie ferramentas MCP de mutação, recursos MCP de leitura e prompts.
- Valide alterações com o comando mais estreito disponível.

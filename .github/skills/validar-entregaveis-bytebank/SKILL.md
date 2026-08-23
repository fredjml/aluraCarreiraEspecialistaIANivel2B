---
name: validar-entregaveis-bytebank
description: Validar a estrutura, sintaxe e rastreabilidade dos entregáveis do desafio Bytebank Nivel2.
---

# Validar entregáveis Bytebank

Use esta skill após cada etapa do projeto.

## Procedimento

1. Conferir se os arquivos previstos existem e não estão vazios.
2. Validar cabeçalhos dos CSVs e contagem de registros.
3. Executar `python -m compileall src tests` para código Python.
4. Executar `python -m unittest discover -s tests` para os testes locais.
5. Procurar links relativos quebrados e menções a credenciais reais.
6. Registrar limitações e resultados objetivos no relatório da etapa.
7. Executar `python scripts/validate_project.py` e testar `python scripts/mcp_tools.py` com entradas JSON locais.
8. Gerar os relatórios Markdown e DOCX somente depois das validações.

## Limites

A skill não publica no GitHub, não cria Google Sheets, não acessa APIs e não atribui notas de LLM sem execução comprovada.

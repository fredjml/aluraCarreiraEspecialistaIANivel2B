# Especificação do dashboard Hermex Log

## Tipos

- `estado`: geográfico, subdivisão de país nível 1 (Brasil).
- `data_pedido`, `data_envio`, `data_recebimento`: data.
- `nota_nps`: número inteiro.

## Campos calculados

```text
Promotores: IF(nota_nps > 8, 1, 0)
Detratores: IF(nota_nps < 7, 1, 0)
NPS: ((SUM(Promotores) / COUNT(nota_nps)) - (SUM(Detratores) / COUNT(nota_nps))) * 100
Dias até envio: DATE_DIFF(data_envio, data_pedido)
Dias até entrega: DATE_DIFF(data_recebimento, data_pedido)
SLA cumprido: IF(DATE_DIFF(data_recebimento, data_pedido) <= 5, 1, 0)
```

O NPS deve ser exibido em pontos, de -100 a 100. Se for formatado como porcentagem, remover o `* 100`.

## Visualizações

1. Scorecards: NPS geral, promotores e detratores.
2. Mapa do Brasil: UF, NPS médio; azul alto e vermelho baixo.
3. Barras: média de dias até entrega por UF, linha de referência em 5 dias.
4. Tabela: UF, respostas, NPS, média até envio e média até entrega.

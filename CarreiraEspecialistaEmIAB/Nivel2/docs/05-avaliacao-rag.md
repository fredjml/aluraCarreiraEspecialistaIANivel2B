# Avaliação do pipeline RAG

O conjunto de validação tem oito perguntas em `src/evaluation.py`, cada uma com gabarito, resposta sem RAG, resposta com RAG, critério e resultado.

## Política de medição

- **Gabarito:** fato esperado extraído do dataset fictício.
- **Sem RAG:** fica `PENDENTE` sem uma API de LLM configurada.
- **Com RAG:** resposta do modo local determinístico com fontes.
- **Critério:** conter o fato do gabarito e citar pelo menos uma fonte recuperada.
- **Resultado:** `compatível com gabarito local` ou `manual: verificar`.

Não há porcentagem final inventada. Para obter uma taxa, execute o relatório, revise os casos marcados e registre a decisão humana ou habilite um juiz de LLM com credencial autorizada.

```powershell
python -m src.evaluation
```

O arquivo gerado em `outputs/avaliacao_rag.csv` é ignorado pelo Git por conter saída de execução.

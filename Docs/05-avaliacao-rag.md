# Avaliação do pipeline RAG

O conjunto ativo de validação possui 32 casos versionados em
`data/avaliacao_rag.csv`. Ele inclui perguntas diretas, paráfrases, múltiplas
fontes, negativas, tentativas de prompt injection, acesso proibido e regressões.
Cada execução compara uma resposta sem RAG com uma resposta RAG para o mesmo
gabarito e grava os modos realmente usados em `outputs/avaliacao_rag.csv`.

A tabela de oito casos abaixo é uma evidência histórica da rodada de
22/08/2026. Ela não substitui a suíte ativa nem representa uma rodada externa
integral. As execuções novas usam cache e checkpoint em `outputs/` para retomar
casos concluídos sem repetir chamadas ao provedor.

## Fluxo avaliado

| Componente | Com Gemini | Fallback local |
|---|---|---|
| Sem RAG | Gemini responde sem receber políticas | Registra que geração livre não está disponível |
| Recuperação | Chroma + embeddings traz candidatos e fusão lexical completa a cobertura | Mesmo Chroma local; sem API externa |
| Reranking | Gemini pontua e ordena os 8 candidatos | Ordem da similaridade lexical |
| Geração RAG | Gemini responde apenas com os 4 melhores chunks e cita `[id=N]` | Concatena evidências e cita `id=N` |
| Juiz | Gemini compara resposta e gabarito com saída estruturada | Correspondência normalizada e exigência de fonte |

Falhas de inicialização ou chamada externa não são tratadas como sucesso. A
coluna `fallbacks` registra o componente, tipo do erro e motivo; as colunas
`modo_sem_rag`, `modo_reranking`, `modo_com_rag` e `modo_juiz` identificam a
origem de cada resultado.

## Configuração segura

1. Copie `.env.example` para `.env`.
2. Grave a chave somente em `GOOGLE_API_KEY` dentro de `.env`.
3. Defina `BYTEBANK_LLM_MODE=gemini`.
4. Mantenha `BYTEBANK_GEMINI_MODEL=gemini-3.5-flash-lite` ou informe outro modelo
   autorizado.
5. Nunca adicione `.env` ao Git.

A implementação usa a SDK oficial `google-genai` e saída estruturada Pydantic
para reranking e juiz. O modo `auto` usa Gemini apenas quando encontra a chave;
o modo `local` proíbe chamadas externas mesmo que uma chave exista.

Uma rodada completa com 32 casos realiza até 160 chamadas (baseline, reranking,
geração RAG e dois julgamentos por caso). Verifique cota, custo e política de
uso antes de executar em ambiente compartilhado.

## Execução

```powershell
# Validação offline e reproduzível
python -m src.evaluation --mode local

# Gemini quando GOOGLE_API_KEY estiver configurada
python -m src.evaluation --mode gemini

# Gemini se houver chave; fallback local caso contrário
python -m src.evaluation --mode auto
```

## Resultado verificado em 23/08/2026

A execução com `gemini-3.5-flash-lite` e Chroma processou os **32 casos** da
suíte ativa. Obteve **12/32 (37,5%) sem RAG** e **28/32 (87,5%) com RAG**. A
geração permaneceu no Gemini nos 32 casos; quatro julgamentos acionaram fallback
local rastreável. Portanto, a rodada demonstra execução externa integral da
geração, mas não uma avaliação integralmente externa.

| Indicador | Resultado |
|---|---:|
| Casos processados | 32/32 |
| Acertos sem RAG | 12/32 (37,5%) |
| Acertos com RAG | 28/32 (87,5%) |
| Geração Gemini | 32/32 |
| Juiz com fallback local | 4/32 |
| Modelo e provedor | `gemini-3.5-flash-lite` / Gemini |

O arquivo versionado `outputs/avaliacao_rag.csv` registra fontes, modos,
métricas e fallbacks por caso. Os quatro fallbacks impedem atribuir o resultado
ao Gemini como se o julgamento também tivesse sido externo em todos os casos.

O CSV em `outputs/` é versionado como evidência de execução e não contém
credenciais. Cache e checkpoint permanecem ignorados; o CSV registra modelo,
data, parâmetros, quantidade de casos e eventuais limites de cota.

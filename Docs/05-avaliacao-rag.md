# Avaliação do pipeline RAG

O conjunto de validação tem oito perguntas em `src/evaluation.py`. Cada execução
compara uma resposta sem RAG com uma resposta RAG para o mesmo gabarito e grava
os modos realmente usados em `outputs/avaliacao_rag.csv`.

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

Uma rodada completa com oito casos realiza até 40 chamadas (baseline,
reranking, geração RAG e dois julgamentos por caso). Verifique cota, custo e
política de uso antes de executar em ambiente compartilhado.

## Execução

```powershell
# Validação offline e reproduzível
python -m src.evaluation --mode local

# Gemini quando GOOGLE_API_KEY estiver configurada
python -m src.evaluation --mode gemini

# Gemini se houver chave; fallback local caso contrário
python -m src.evaluation --mode auto
```

## Resultado verificado em 22/08/2026

A execução com `gemini-3.5-flash-lite` e Chroma obteve **1/8 (12,5%) sem RAG** e
**8/8 (100%) com RAG**. A recuperação usou `chroma_embeddings+lexical_hybrid`
nos oito casos. A cota do provedor respondeu HTTP 429 após parte da rodada:
três casos concluíram todas as etapas Gemini e cinco usaram algum fallback local.
O arquivo versionado `outputs/avaliacao_rag.csv` registra o modo de cada etapa,
as fontes e os fallbacks; por isso o resultado não é apresentado como uma rodada
100% Gemini.

### Tabela final de avaliação

| # | Pergunta | Gabarito | Sem RAG | Com RAG | Fontes RAG | Geração/juiz | Fallback |
|---:|---|---|---:|---:|---|---|---|
| 1 | Quais documentos são necessários para abrir conta? | CPF válido, comprovante de residência e documento de identidade | 100 - acerto | 100 - acerto | `id=1`, `id=2`, `id=50`, `id=28` | Gemini/Gemini | Não |
| 2 | Quanto custa a TED adicional? | R$ 9,90 | 0 - erro | 100 - acerto | `id=3`, `id=30`, `id=25`, `id=36` | Gemini/Gemini | Não |
| 3 | Qual é a anuidade do cartão Platinum? | R$ 59,90 | 0 - erro | 100 - acerto | `id=9`, `id=36`, `id=11`, `id=45` | Gemini/Gemini | Não |
| 4 | Qual o limite máximo do cartão Gold? | R$ 20.000 | 0 - erro | 100 - acerto | `id=11`, `id=9`, `id=7`, `id=13` | Local/Local | Sim - HTTP 429 |
| 5 | Como contestar uma transação não reconhecida? | Em até 48 horas pelo aplicativo | 0 - erro | 100 - acerto | `id=30`, `id=9`, `id=46`, `id=1` | Local/Local | Sim - HTTP 429 |
| 6 | Qual o prazo para excluir dados pessoais? | 15 dias úteis | 0 - erro | 100 - acerto | `id=28`, `id=5`, `id=26`, `id=50` | Local/Local | Sim - HTTP 429 |
| 7 | Qual o prazo de resposta da ouvidoria? | 10 dias úteis | 0 - erro | 100 - acerto | `id=15`, `id=37`, `id=5`, `id=28` | Local/Local | Sim - HTTP 429 |
| 8 | Qual o limite do Pix noturno? | R$ 1.000 por transação | 0 - erro | 100 - acerto | `id=32`, `id=31`, `id=11`, `id=29` | Local/Local | Sim - HTTP 429 |
| **Total** | **8 casos** | - | **1/8 (12,5%)** | **8/8 (100%)** | **8/8 com fontes** | **3 Gemini; 5 local** | **5/8 casos** |

“Fallback” indica que ao menos uma etapa solicitada ao Gemini retornou HTTP 429 e
foi concluída pelo caminho local rastreável. As notas e modos acima foram lidos
diretamente de `outputs/avaliacao_rag.csv`; o resultado não implica que os oito
casos tenham sido executados integralmente pelo provedor externo.

O CSV em `outputs/` é ignorado pelo Git porque contém saída de execução, não
credenciais. Para uma evidência reproduzível, registre também modelo, data,
parâmetros, quantidade de casos e eventuais limites de cota.

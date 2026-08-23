# ADR-002: Arquitetura RAG do Bytebank

- **Status:** aceito para protótipo
- **Contexto:** políticas podem mudar e precisam ser citadas sem treinar novamente o modelo.
- **Decisão:** usar RAG com índice local, metadados preservados e geração opcional.

## RAG versus fine-tuning

RAG mantém conhecimento fora do modelo, permitindo atualizar documentos e reindexar somente o conteúdo alterado. Também facilita rastreabilidade, controle de acesso e remoção de uma política. Fine-tuning pode ensinar estilo, formato ou comportamento, mas custa mais para iterar, exige conjunto de treino e não é a escolha primária para fatos que mudam. Fine-tuning pode complementar o sistema para comportamento, nunca substituir controles de fonte.

## Ingestão e chunking

A fonte inicial é `data/politicas_bytebank.csv`. Cada linha vira um `Document` com `page_content=conteudo` e metadados `id`, `dominio`, `secao` e `nivel_acesso`. O protótipo usa `RecursiveCharacterTextSplitter`, tamanho 500 e overlap 100. O tamanho fixo é previsível para custo e janela de contexto; o overlap reduz a perda de contexto nas fronteiras. Em produção, avaliaríamos também divisão por parágrafo e regras semânticas.

## Embeddings

O pipeline usa `sentence-transformers/all-MiniLM-L6-v2` localmente, com execução offline após o download inicial. Os vetores são normalizados antes da indexação. Como o modelo é compacto e não é especializado em português, a recuperação combina o ranking vetorial do Chroma com um ranking lexical por Reciprocal Rank Fusion; essa decisão reduz falsos negativos sem enviar políticas a terceiros. Em produção, deve-se comparar um modelo multilíngue hospedado sob controle do banco com provedores autorizados, medindo recall, latência, custo, residência e retenção.

## Vector store

| Opção | Vantagem | Limitação | Decisão |
|---|---|---|---|
| FAISS | rápido e simples localmente | exige camada própria de metadados e persistência | útil para benchmark |
| ChromaDB | persistência local, integração LangChain e filtros | operação distribuída exige desenho adicional | escolhido no protótipo |
| Supabase | Postgres, filtros e operação gerenciada | dependência externa e governança de acesso | avaliar em produção |

## Recuperação e reranking

A busca inicial no Chroma usa similaridade de cosseno com `k=4`; em paralelo, oito candidatos vetoriais são fundidos com os oito melhores lexicais e reduzidos a oito candidatos únicos. O reranker Gemini, quando habilitado, ordena esses oito e seleciona quatro. Sem LLM, o reranker lexical determinístico mantém a demonstração reproduzível. O índice persistente fica em `outputs/chroma_db` e usa IDs estáveis para `upsert` idempotente.

## Metadados e segurança

Cada chunk conserva `id`, `dominio`, `secao`, `nivel_acesso`, `categoria_semantica`, `origem` e `chunk_index`. O parâmetro `allowed_levels` é convertido em filtro `where` no Chroma e também aplicado ao fallback lexical antes do ranking. A consulta pública usa somente `publico`; conteúdo `interno` jamais entra no contexto por padrão.

## Rastreamento

A resposta retorna `source_documents`, IDs, seção, domínio e nível de acesso. Logs devem conter versão do índice, prompt e modelo sem armazenar segredos ou dados pessoais desnecessários.

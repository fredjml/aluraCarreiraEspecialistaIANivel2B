# ADR-002: Arquitetura RAG do Bytebank

- **Status:** aceito para protótipo
- **Contexto:** políticas podem mudar e precisam ser citadas sem treinar novamente o modelo.
- **Decisão:** usar RAG com índice local, metadados preservados e geração opcional.

## RAG versus fine-tuning

RAG mantém conhecimento fora do modelo, permitindo atualizar documentos e reindexar somente o conteúdo alterado. Também facilita rastreabilidade, controle de acesso e remoção de uma política. Fine-tuning pode ensinar estilo, formato ou comportamento, mas custa mais para iterar, exige conjunto de treino e não é a escolha primária para fatos que mudam. Fine-tuning pode complementar o sistema para comportamento, nunca substituir controles de fonte.

## Ingestão e chunking

A fonte inicial é `data/politicas_bytebank.csv`. Cada linha vira um `Document` com `page_content=conteudo` e metadados `id`, `dominio`, `secao` e `nivel_acesso`. O protótipo usa `RecursiveCharacterTextSplitter`, tamanho 500 e overlap 100. O tamanho fixo é previsível para custo e janela de contexto; o overlap reduz a perda de contexto nas fronteiras. Em produção, avaliaríamos também divisão por parágrafo e regras semânticas.

## Embeddings

O modo demonstrativo usa vetores locais determinísticos por tokens, adequado para testes sem enviar conteúdo a terceiros. Em produção, comparar um modelo open source hospedado sob controle do banco com um provedor proprietário. Critérios: janela de entrada, dimensão do vetor, português e multilíngue, latência, custo, residência e política de retenção. A escolha deve ser comprovada por benchmark de recall e risco, não por preferência nominal.

## Vector store

| Opção | Vantagem | Limitação | Decisão |
|---|---|---|---|
| FAISS | rápido e simples localmente | exige camada própria de metadados e persistência | útil para benchmark |
| ChromaDB | persistência local, integração LangChain e filtros | operação distribuída exige desenho adicional | escolhido no protótipo |
| Supabase | Postgres, filtros e operação gerenciada | dependência externa e governança de acesso | avaliar em produção |

## Recuperação e reranking

A busca inicial é similarity search com `k=4`. Para o fluxo de reranking, recuperar oito candidatos, pontuar relevância por LLM quando habilitado e selecionar quatro. Sem LLM, o fallback lexical determinístico mantém a demonstração reproduzível e não deve ser descrito como avaliação de modelo.

## Metadados e segurança

Cada chunk conserva `id`, `dominio`, `secao`, `nivel_acesso`, `categoria_semantica`, `origem` e `chunk_index`. Eles permitem filtrar por domínio, seção e nível de acesso antes da geração, facilitam auditoria e explicam de qual trecho veio a resposta. A autorização do usuário deve ser aplicada antes do retriever, nunca depois da resposta.

## Rastreamento

A resposta retorna `source_documents`, IDs, seção, domínio e nível de acesso. Logs devem conter versão do índice, prompt e modelo sem armazenar segredos ou dados pessoais desnecessários.

# Dicionário de dados

O arquivo [`data/politicas_bytebank.csv`](../data/politicas_bytebank.csv) contém somente políticas fictícias.

| Campo | Tipo | Regra |
|---|---|---|
| `id` | inteiro | Identificador único do trecho original |
| `dominio` | texto | `conta_corrente`, `cartao_credito`, `suporte`, `rh` ou `seguranca` |
| `secao` | texto | Seção funcional da política |
| `conteudo` | texto | Texto consultável da política |
| `nivel_acesso` | texto | `publico`, `interno` ou `restrito` |

Os chunks acrescentam `categoria_semantica`, `origem` e `chunk_index` sem apagar os campos originais.

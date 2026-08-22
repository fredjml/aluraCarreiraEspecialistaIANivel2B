# Plano de execucao - Bytebank Nivel 2

## Objetivo
Construir um repositório reproduzível para o checkpoint Especialista em IA Nível 2, usando somente o cenário fictício do Bytebank e o enunciado em `projNivel2EspIAB.txt`.

## Estado inicial
- Requisitos: disponíveis em `projNivel2EspIAB.txt`.
- Dataset: embutido no enunciado, com 50 políticas fictícias e os campos `id`, `dominio`, `secao`, `conteudo` e `nivel_acesso`.
- Código, documentação técnica, planilhas reproduzíveis e configuração Python: ainda não identificados.
- Credenciais, usuário GitHub, publicação e screenshots Power BI: não disponíveis.

## Etapas e critérios de saída

1. **Fundação e governança**
   - Criar README de portfólio com limitações explícitas.
   - Criar governança, ética, LGPD, alucinações e LLM Ops.
   - Criar CSVs de composição do time e carreira em Y.
   - Copiar o dataset fictício para `data/politicas_bytebank.csv`.
   - Criar ambiente seguro com `.env.example`, `.gitignore` e dependências declaradas.

2. **Arquitetura RAG**
   - Documentar ADR, decisões de chunking, embeddings, vector store e metadados.
   - Criar diagrama Mermaid completo e glossário CSV com pelo menos 15 termos.

3. **Pipeline RAG e avaliação**
   - Implementar carregamento CSV, `Document`, metadados, categoria semântica e `RecursiveCharacterTextSplitter` com `chunk_size=500` e `chunk_overlap=100`.
   - Implementar modo local determinístico e adaptador opcional para embeddings/LLM.
   - Demonstrar retriever `similarity` com `k=4`, reranking de 8 para 4 e avaliação de 8 perguntas.
   - Separar gabarito, respostas, critério e resultado; resultados de LLM ficam pendentes sem credencial.

4. **Multiagente e operação**
   - Implementar `StateGraph` com `TypedDict`, classificação, três agentes, roteamento e síntese.
   - Documentar A2A, MCP, Agent Cards, memórias, HITL e snapshots.
   - Criar diagrama Mermaid e interface Gradio com fallback local.
   - Criar instruções e skill reutilizável somente onde houver fluxo repetível.

## Validação por etapa

- Markdown/CSV: inspeção estrutural e links relativos.
- Python: `compileall`/checagem sintática e testes locais sem API.
- RAG: execução demonstrativa determinística e conferência de metadados.
- Multiagente: execução de três perguntas e validação do roteamento.
- Externo: GitHub Pages, Google Sheets, APIs e Power BI permanecem pendentes sem dados ou autorização.

## Próxima fatia
Criar a fundação documental, o dataset local e a configuração de ambiente. Nenhuma publicação, instalação global, commit ou chamada externa será executada.

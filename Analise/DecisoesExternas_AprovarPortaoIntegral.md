# Decisões externas para aprovar o portão integral

## Objetivo

Registrar as alternativas e recomendações para concluir o portão de Prontidão Operacional e Piloto com Usuários do GeoAI Mentor. A orientação geral é executar primeiro um piloto controlado, sem antecipar a complexidade de uma produção corporativa completa.

## 1. Plataforma de hospedagem

### Alternativas

- **Streamlit Community Cloud:** implantação rápida, integração com GitHub e gerenciamento de secrets. Adequado para demonstração e piloto pequeno sem persistência crítica.
- **Google Cloud Run com PostgreSQL:** aplicação conteinerizada, escalabilidade e cobrança por uso.
- **Azure App Service com Azure PostgreSQL:** indicado quando a organização já utiliza Microsoft 365 e Microsoft Entra ID.
- **Servidor próprio ou VPS:** oferece maior controle, mas exige manutenção, atualizações, backups, TLS e monitoramento.

### Recomendação

Usar Streamlit Community Cloud somente para demonstração. Para um piloto persistente, escolher Azure App Service ou Google Cloud Run com PostgreSQL gerenciado.

O armazenamento local de plataformas conteinerizadas pode ser descartável. No Cloud Run, por exemplo, o sistema de arquivos gravável não persiste quando a instância é encerrada. Portanto, o SQLite não deve ser o banco definitivo nessa modalidade de hospedagem.

### Fontes

- [Implantação no Streamlit Community Cloud](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app)
- [Visão geral do Google Cloud Run](https://docs.cloud.google.com/run/docs/overview/what-is-cloud-run)

## 2. Provedor de autenticação

### Alternativas

- **Google OIDC:** conveniente para participantes com contas Google.
- **Microsoft Entra ID:** recomendado para ambientes corporativos ou educacionais baseados em Microsoft 365.
- **Auth0 ou Okta:** úteis quando são necessários vários provedores e políticas mais sofisticadas.
- **Cloudflare Access:** adiciona autenticação e políticas de acesso na frente da aplicação, com suporte a identidade, grupos e postura do dispositivo.

### Recomendação

Usar Google OIDC em um piloto independente ou Microsoft Entra ID quando os participantes pertencerem a uma instituição Microsoft. O Streamlit oferece suporte nativo ao protocolo OIDC.

### Fontes

- [Autenticação OIDC no Streamlit](https://docs.streamlit.io/develop/tutorials/authentication)
- [Aplicações protegidas pelo Cloudflare Access](https://developers.cloudflare.com/cloudflare-one/access-controls/applications/http-apps/)

## 3. Separação por usuário

### Alternativas

- adicionar `owner_id` às conversas e utilizar o identificador imutável `sub` fornecido pelo OIDC;
- manter um banco SQLite separado por usuário, solução simples, porém difícil de operar e escalar;
- utilizar PostgreSQL compartilhado com `owner_id`, índices e filtros obrigatórios;
- utilizar PostgreSQL com Row-Level Security como proteção adicional no banco.

### Recomendação

Migrar para PostgreSQL e adotar a seguinte estrutura conceitual:

```text
users
  id = identificador OIDC estável

conversations
  id
  owner_id
  title
  created_at
  updated_at

messages
  id
  conversation_id
  role
  content
  created_at
```

Toda leitura, alteração ou exclusão deve verificar simultaneamente `conversation_id` e `owner_id`. O e-mail não deve ser a chave principal, pois pode mudar.

## 4. Política institucional de retenção

### Alternativas

- **30 dias:** menor risco de privacidade, com histórico reduzido para avaliação.
- **90 dias:** equilíbrio adequado para o piloto.
- **180 a 365 dias:** melhor análise longitudinal, mas com maior risco e obrigação de governança.
- **Retenção indefinida:** não recomendada.

### Recomendação para o piloto

- conversas: 90 dias após a última atividade;
- backups: 30 dias;
- logs técnicos: 30 dias;
- exclusão manual disponível ao usuário;
- exclusão antecipada mediante solicitação;
- nenhum conteúdo de conversa nos logs;
- fontes RAG administradas separadamente do histórico das conversas.

Também devem ser formalizados o responsável pelos dados, o processo de restauração, a aprovação de exclusões e o procedimento de resposta a incidentes.

## 5. Fontes institucionais para o RAG

### Fontes candidatas

- materiais oficiais dos cursos da Alura, quando houver autorização;
- guias institucionais de carreira;
- procedimentos e manuais internos;
- documentação oficial de Python e das bibliotecas utilizadas;
- fontes públicas reconhecidas de geociências;
- exemplos e conjuntos de dados com licença compatível.

### Manifesto recomendado para cada fonte

```yaml
titulo:
origem:
responsavel:
licenca:
data_de_aprovacao:
data_de_revisao:
nivel_de_confidencialidade:
versao:
```

### Recomendação

Começar com 10 a 20 documentos revisados, sem ingestão automática. Cada documento deve possuir responsável, licença, versão, validade e classificação de confidencialidade. O sistema deve recusar respostas quando não houver evidência adequada.

## 6. Orçamento e alertas da API

### Alternativas

- orçamento único para toda a organização;
- projeto OpenAI exclusivo para o GeoAI Mentor;
- chaves separadas para desenvolvimento, piloto e produção;
- limites internos por usuário, conversa ou dia.

### Recomendação

- criar um projeto OpenAI exclusivo para o piloto;
- permitir somente modelos aprovados;
- configurar alertas em 50%, 75%, 90% e 100% do orçamento;
- estabelecer limite diário por usuário;
- limitar tamanho das perguntas, do histórico e das respostas;
- registrar tokens e custo estimado sem registrar o conteúdo;
- utilizar uma chave exclusiva no ambiente publicado.

Os budgets da plataforma OpenAI funcionam como alertas e não necessariamente interrompem as requisições. Por isso, o sistema deve possuir seu próprio limite de uso. A Usage API pode acompanhar consumo por projeto, usuário, chave e modelo.

### Fontes

- [Gerenciamento de projetos e budgets da OpenAI](https://help.openai.com/en/articles/9186755-managing-projects-in-the-api-platform)
- [OpenAI Usage API](https://platform.openai.com/docs/api-reference/usage/moderations_object?lang=node.js%EF%BC%89)

## 7. Piloto real com geocientistas

### Alternativas

- teste rápido com 3 a 5 participantes;
- piloto controlado com 8 a 12 participantes;
- piloto institucional com 20 ou mais participantes.

### Recomendação

Executar um piloto com 8 a 12 geocientistas durante duas a quatro semanas, incluindo profissionais iniciantes e experientes.

### Métricas propostas

- utilidade percebida: média igual ou superior a 4/5;
- clareza: média igual ou superior a 4/5;
- respostas com fonte quando necessária: pelo menos 90%;
- fontes corretas entre as citações apresentadas: pelo menos 90%;
- recusa adequada fora da base: pelo menos 90%;
- conclusão das tarefas propostas: pelo menos 80%;
- incidentes de separação entre usuários: zero;
- exposição de segredo ou dado de outro usuário: zero;
- custo médio por conversa;
- tempo médio de resposta;
- intenção de reutilização.

Os participantes devem ser informados de que se trata de uma IA experimental, orientados a não inserir dados confidenciais e convidados a consentir com a análise anonimizada do feedback.

## Pacote de decisão recomendado

- **Hospedagem:** Streamlit Community Cloud apenas para demonstração; Azure App Service ou Cloud Run para o piloto persistente.
- **Banco:** PostgreSQL gerenciado.
- **Autenticação:** Google OIDC para grupo independente ou Microsoft Entra ID para instituição Microsoft.
- **Separação:** `owner_id` derivado do `sub` do OIDC.
- **Retenção:** conversas por 90 dias e backups por 30 dias.
- **RAG:** conjunto inicial de 10 a 20 documentos autorizados e revisados.
- **Orçamento:** projeto OpenAI exclusivo, alertas progressivos e limite diário interno.
- **Piloto:** 8 a 12 geocientistas durante duas a quatro semanas.

Esse conjunto mantém custo e complexidade moderados e produz evidências para decidir se o GeoAI Mentor deve avançar para produção controlada.

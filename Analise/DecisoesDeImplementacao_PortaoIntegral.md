# Decisões de implementação — portão integral

## Objetivo

Definir o pacote técnico para concluir o portão de Prontidão Operacional e executar um piloto controlado do GeoAI Mentor.

## Decisões confirmadas

### Enquadramento

- **Natureza:** prova de conceito (POC) e projeto piloto, não produção.
- **Participantes previstos:** 2.
- **Data prevista para início:** 24/08/2026.
- **Feedback:** poderá ser armazenado de forma anonimizada.
- **Objetivo:** demonstrar viabilidade, isolamento básico, controle de custo, utilidade e segurança proporcionais ao piloto.

### Ecossistema do piloto

- **Identidade:** Microsoft Entra ID.
- **Hospedagem:** Azure App Service.
- **Banco persistente:** Azure Database for PostgreSQL.
- **Orçamento mensal total do piloto:** R$ 50,00.
- **Assinatura:** Azure for Students.
- **Tenant Entra ID:** `aa495f2c-d37e-4b58-ab95-bf0874a3adb2`.
- **Escopo de acesso:** somente um tenant.
- **Região Azure:** `eastus`.
- **Banco inicial:** vazio, sem migração do histórico SQLite.

## Escopo técnico que pode ser implementado

### 1. PostgreSQL e migração

- manter SQLite para desenvolvimento local;
- implementar repositório compatível com PostgreSQL;
- configurar a conexão por variável de ambiente;
- criar tabelas, índices e migrações versionadas;
- adicionar `owner_id` às conversas;
- preparar migração opcional do histórico SQLite;
- testar integração, transações, isolamento e concorrência;
- preparar compatibilidade com Azure Database for PostgreSQL.

### 2. Autenticação com Microsoft Entra ID

- adicionar login e logout via OIDC no Streamlit;
- bloquear a aplicação para usuários não autenticados;
- utilizar o claim imutável `sub` como identificador interno do usuário;
- usar nome e e-mail apenas para apresentação, nunca como chave principal;
- manter tokens e credenciais fora do banco;
- configurar URIs de redirecionamento por ambiente;
- validar sessão expirada e falhas de autenticação.

O cadastro da aplicação, os secrets OIDC e a autorização dos usuários dependerão do tenant Microsoft escolhido.

### 3. Separação por usuário

- associar toda conversa a um `owner_id`;
- exigir `owner_id` em criação, listagem, abertura, alteração e exclusão;
- impedir acesso a uma conversa pertencente a outro usuário;
- incluir índices por proprietário;
- adicionar testes negativos de acesso cruzado;
- avaliar Row-Level Security no PostgreSQL como defesa adicional.

### 4. Retenção e backups

- retenção inicial proposta de 90 dias para conversas;
- backups mantidos por 30 dias;
- modo de simulação antes da exclusão;
- execução automática e comando manual;
- registro somente das quantidades processadas;
- teste de integridade e restauração;
- exclusão manual solicitada pelo usuário;
- definição de destino persistente para os backups no Azure.

### 5. Governança do RAG

- aceitar somente fontes autorizadas;
- exigir manifesto com título, origem, responsável, licença, aprovação, revisão, versão e confidencialidade;
- validar extensões, tamanho e codificação;
- registrar hash do conteúdo;
- detectar duplicidades;
- bloquear fontes vencidas ou não aprovadas;
- produzir inventário das fontes disponíveis;
- manter recusa quando não houver evidência;
- ampliar testes de recuperação, citação e recusa.

Os documentos institucionais e suas permissões precisam ser fornecidos e aprovados externamente.

### 6. Orçamento e limites de consumo

O orçamento mensal total confirmado é de **R$ 50,00**. Como a cobrança da OpenAI ocorre em moeda estrangeira e pode variar com câmbio, impostos, modelo e volume, o sistema deverá trabalhar com uma margem de segurança.

Esse orçamento cobre conjuntamente os serviços Azure e o consumo da OpenAI. Portanto, o teto não poderá ser controlado somente pela aplicação: será necessário acompanhar também o consumo da assinatura Azure for Students.

#### Proposta inicial

- teto operacional interno: 80% do orçamento, equivalente a R$ 40,00;
- reserva de segurança: 20%, equivalente a R$ 10,00;
- alertas em 50%, 75%, 80%, 90% e 100%;
- bloqueio interno de novas chamadas ao alcançar o teto operacional;
- projeto OpenAI exclusivo para o piloto;
- chave exclusiva do ambiente publicado;
- modelos permitidos definidos por configuração;
- limite diário por usuário;
- limite por conversa;
- tamanho máximo de pergunta e histórico;
- máximo de tokens por resposta;
- registro de tokens e custo estimado sem armazenar o conteúdo nos logs;
- painel ou relatório administrativo de consumo.

O bloqueio interno em R$ 40,00 está aprovado. Ele limitará as chamadas à OpenAI, mas não interromperá automaticamente cobranças ou consumo já incorrido nos serviços Azure.

Os budgets configurados na plataforma OpenAI devem ser tratados como alertas. O bloqueio rígido deverá ser implementado na aplicação.

### 7. Azure App Service

- preparar inicialização do Streamlit com a porta fornecida pelo ambiente;
- criar configuração de implantação;
- definir variáveis e secrets por ambiente;
- adicionar endpoint ou verificação de saúde;
- documentar implantação, reversão e diagnóstico;
- restringir acesso ao piloto autenticado;
- conectar ao Azure Database for PostgreSQL usando TLS;
- avaliar Managed Identity para eliminar credenciais permanentes de banco quando aplicável;
- configurar logs sem conteúdo conversacional ou credenciais.

### 8. Instrumentos do piloto

- termo informativo para participantes;
- orientação para não inserir dados confidenciais;
- formulário de consentimento;
- roteiro de tarefas;
- questionário pré e pós-piloto;
- escala de utilidade e clareza;
- registro anonimizado de feedback;
- cálculo das métricas de aprovação;
- relatório final do piloto.

## Métricas propostas para o piloto

- 2 participantes nesta POC;
- duração de duas a quatro semanas;
- utilidade percebida média igual ou superior a 4/5;
- clareza média igual ou superior a 4/5;
- respostas com fonte quando necessária em pelo menos 90% dos casos;
- fontes corretas em pelo menos 90% das citações avaliadas;
- recusa adequada fora da base em pelo menos 90% dos casos;
- conclusão das tarefas em pelo menos 80% dos casos;
- zero acesso a conversas de outro usuário;
- zero exposição de segredo ou dado de outro usuário;
- acompanhamento de custo e tempo médio por conversa.

## Sequência de implementação

1. Confirmar as decisões externas restantes.
2. Implementar autenticação Microsoft Entra ID.
3. Introduzir `owner_id` e isolamento completo.
4. Implementar PostgreSQL e migrações.
5. Adicionar medição e bloqueio interno de consumo.
6. Completar retenção, backup e restauração no Azure.
7. Implementar governança das fontes RAG.
8. Preparar Azure App Service e configurações de ambiente.
9. Criar os instrumentos do piloto.
10. Publicar em ambiente controlado e executar o piloto.

## Respostas consolidadas

| Decisão | Resposta |
|---|---|
| Abrangência dos R$ 50 | Azure e OpenAI em conjunto |
| Assinatura Azure | Azure for Students |
| Tenant | `aa495f2c-d37e-4b58-ab95-bf0874a3adb2` |
| Escopo de autenticação | Um único tenant |
| Região | `eastus` |
| Estado inicial do PostgreSQL | Banco vazio |
| Retenção | Conversas por 90 dias e backups por 30 dias |
| Quantidade inicial de fontes RAG | 10 documentos |
| Bloqueio interno | Aprovado ao atingir R$ 40 |
| Participantes | 2 |
| Responsável e alertas | `fredjml.br@gmail.com` — confirmado |
| Início previsto | 24/08/2026 |
| Feedback anonimizado | Aprovado |

## Dúvidas restantes

### Identidade e acesso

1. Quais duas contas do tenant serão autorizadas a participar da POC?
2. O acesso será permitido a qualquer conta desse tenant ou somente aos dois participantes previstos?
3. Haverá usuários administradores com acesso a métricas, fontes e operações?

### Azure e banco

4. O PostgreSQL poderá ser acessado somente pela aplicação ou também por administradores para suporte?
5. Onde os backups deverão ser armazenados e quem poderá restaurá-los?

### Retenção e privacidade

6. Os participantes poderão excluir imediatamente suas próprias conversas?
7. Há alguma categoria de dado que deve ser expressamente proibida além de dados confidenciais e pessoais?
8. Quem será o responsável por privacidade, incidentes e solicitações de exclusão?

### RAG

9. Quem fará a aprovação final dos dez resumos curados em `Analise/docsgeo`?
10. As respostas deverão sempre citar fontes ou apenas quando utilizarem o RAG?

### Orçamento

13. Quantas conversas por participante são esperadas?
14. Ao atingir o limite, a aplicação deve bloquear todas as chamadas ou reservar uma cota administrativa?

### Piloto

16. Como os dois participantes serão recrutados e identificados no tenant?
17. Qual será a duração da POC após 24/08/2026?
18. Quem será o responsável por suporte e comunicação com os participantes?

## Situação

O pacote técnico está definido para o ecossistema Microsoft. A implementação pode começar após a confirmação das decisões que afetam identidade, isolamento, custo, retenção e infraestrutura. Itens sem resposta deverão permanecer configuráveis ou bloqueados por padrão, evitando suposições que possam comprometer segurança, privacidade ou orçamento.

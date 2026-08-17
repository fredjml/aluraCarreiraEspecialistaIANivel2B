# Relatório Executivo Consolidado — GeoAI Mentor

Síntese não técnica da implementação, dos resultados e das evidências do projeto **GeoAI Mentor**.

![Demonstração da interface do GeoAI Mentor](assets/geoai-mentor-demo.gif)

| Campo | Informação |
|---|---|
| Público | Gestores, patrocinadores e usuários não técnicos |
| Finalidade | Apresentar o que foi entregue, como foi validado e o que falta para evolução |
| Período | Implementação e validação concluídas em 16/08/2026 |
| Situação | Protótipo funcional aprovado para demonstração controlada |

> **Conclusão principal:** o GeoAI Mentor foi implementado e testado com sucesso. Ele conversa com o modelo da OpenAI, assume uma personalidade voltada a geocientistas e preserva o contexto entre perguntas da mesma sessão.

## 1. Visão executiva

O projeto transformou uma ideia de assistente especializado em um protótipo executável. O usuário faz perguntas sobre transição de carreira e projetos de dados; o mentor responde de maneira amigável, didática e contextualizada para geociências.

A implementação foi construída em etapas controladas: preparação do ambiente, configuração segura do acesso, conexão com a inteligência artificial, definição da personalidade, inclusão de memória e revisão final. Cada etapa foi documentada e verificada antes do avanço.

## 2. Resultado em números

| Indicador | Resultado | Leitura simples |
|---|---|---|
| Etapas concluídas | 6 de 6 | Todo o escopo solicitado foi implementado e revisado. |
| Critérios finais | 9 de 9 aprovados | Nenhuma não conformidade foi encontrada na revisão final. |
| Perguntas do teste | 2 de 2 respondidas | O modelo respondeu e manteve o contexto da conversa. |
| Compilação | Aprovada | O programa passou pela verificação de integridade sem erros. |
| Proteção da chave | Aprovada | A credencial ficou fora do código e não foi exposta nos registros. |

## 3. O que foi entregue

- Um programa Python chamado `chatbot_mentor.py`, que inicia e executa o GeoAI Mentor.
- Uma interface web amigável em `streamlit_app.py`, com campo de conversa e botão para iniciar uma nova sessão.
- Conexão funcional com o modelo `gpt-5.6-sol` da OpenAI.
- Uma personalidade especializada em apoiar geocientistas na migração para Ciência de Dados.
- Memória por sessão, permitindo que uma pergunta posterior aproveite a resposta anterior.
- Persistência SQLite transacional, mantendo o histórico fora do processo Python.
- Gerenciamento de conversas para criar, listar, reabrir, renomear e excluir históricos.
- Piloto RAG local com fontes Markdown aprovadas, citações de origem e recusa sem evidência.
- Separação entre conversas, evitando mistura de históricos com identificadores diferentes.
- Configuração segura da chave de acesso por arquivo `.env`, ignorado pelo controle de versão.
- Documentação inicial e registro técnico passo a passo no diretório `Analise`.

### Como abrir a interface

No PowerShell, com o ambiente virtual ativo, execute:

```powershell
pip install -r requirements.txt
streamlit run streamlit_app.py
```

O navegador abrirá o GeoAI Mentor. Digite uma pergunta no campo inferior. O `st.session_state` conserva apenas o estado visual; o histórico oficial é gravado no SQLite. A barra lateral permite iniciar, listar, reabrir, renomear e excluir conversas.

Para executar a versão de terminal, use `python chatbot_mentor.py`.

### Operação local

Os limites operacionais são configurados por `OPENAI_REQUEST_TIMEOUT`, `OPENAI_MAX_OUTPUT_TOKENS` e `GEOAI_RETENTION_DAYS`. Para inspecionar o banco, criar um backup consistente ou aplicar a retenção:

```powershell
python scripts/operacoes_geoai.py status
python scripts/operacoes_geoai.py backup
python scripts/operacoes_geoai.py retencao --dias 90
```

Os backups são gravados em `backups/`, fora do Git. A retenção exclui conversas cuja última atualização seja anterior ao período informado.

### Solução de problemas no PowerShell

Se o terminal exibir `System.ArgumentOutOfRangeException` em
`Microsoft.PowerShell.PSConsoleReadLine.ReallyRender` ao colar ou editar um
comando, atualize o PSReadLine no escopo do usuário e reinicie o terminal:

```powershell
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
Install-PackageProvider -Name NuGet -MinimumVersion 2.8.5.201 -Scope CurrentUser -Force -ForceBootstrap
Install-Module PSReadLine -Scope CurrentUser -Force -AllowClobber -Repository PSGallery
```

Para confirmar a versão carregada em uma nova sessão:

```powershell
Get-Module PSReadLine | Select-Object Name, Version, Path
```

Este projeto foi validado com PSReadLine 2.4.5; a versão 2.0.0 apresentou a
falha de reposicionamento do cursor descrita acima.

### Arquitetura separada

O projeto utiliza camadas com responsabilidades distintas:

```text
Interface Streamlit / CLI
          ↓
MentorService (casos de uso)
          ↓
MentorGateway (contrato do domínio)
          ↓
LangChain + OpenAI
          ↓
ConversationRepository → SQLite
```

O front-end não importa LangChain ou `ChatOpenAI`. Ele conhece somente o `MentorService`, que pode receber um back-end falso nos testes. A configuração do modelo está centralizada em `geoai_mentor/config/settings.py`, e os erros técnicos são convertidos em mensagens seguras antes de chegar ao usuário.

## 4. Como a experiência funciona

1. O usuário inicia o programa e faz uma pergunta ao GeoAI Mentor.
2. O programa combina a pergunta com a orientação de personalidade e, quando existente, com o histórico da sessão.
3. A solicitação é enviada ao modelo de inteligência artificial.
4. A pergunta e a resposta são gravadas atomicamente no banco SQLite.
5. Na pergunta seguinte, o histórico é reutilizado para manter continuidade e evitar repetições.

> **Exemplo observado:** depois de recomendar Python, o mentor entendeu que a expressão _“essa linguagem”_ na segunda pergunta se referia a Python e sugeriu projetos coerentes com essa recomendação.

## 5. Benefícios demonstrados

| Benefício | Efeito para o usuário |
|---|---|
| Orientação especializada | Respostas com foco em geociências, carreira e Ciência de Dados. |
| Continuidade da conversa | O usuário pode fazer perguntas complementares sem repetir todo o contexto. |
| Experiência didática | Linguagem amigável e recomendações práticas para quem está aprendendo. |
| Base modular | O armazenamento possui contrato próprio e pode evoluir de SQLite para PostgreSQL. |
| Rastreabilidade | Etapas, decisões, testes e resultados estão registrados para auditoria e consolidação. |

## 6. Testes e evidências de funcionamento

Os testes demonstraram não apenas que o código existe, mas que o comportamento esperado ocorreu na prática.

| O que foi verificado | Situação | Evidência observada |
|---|---|---|
| Configuração segura | Aprovado | A chave foi localizada no `.env` sem ser exibida, copiada ou gravada no código. |
| Conexão com a OpenAI | Aprovado | O modelo recebeu as solicitações e devolveu conteúdo para as duas perguntas. |
| Personalidade do mentor | Aprovado | As respostas usaram orientação e exemplos relacionados a geociências e dados. |
| Memória da conversa | Aprovado | A segunda resposta interpretou corretamente _“essa linguagem”_ como Python. |
| Separação de sessões | Aprovado | O mesmo identificador reutilizou o histórico; outro identificador recebeu histórico independente. |
| Persistência | Aprovado | O histórico foi recuperado por outra instância do repositório e permaneceu isolado por conversa. |
| Atomicidade | Aprovado | Uma falha simulada na resposta desfez também a gravação da pergunta. |
| Cobertura | Aprovado | Limite reproduzível de 85%; componentes críticos de aplicação, configuração e domínio atingiram 100%. |
| Sessões completas | Aprovado | O ciclo criar, listar, reabrir, renomear e excluir foi validado. |
| RAG controlado | Aprovado | Fontes locais autorizadas são recuperadas e identificadas; consultas sem evidência recebem contexto explícito de recusa. |
| Integridade do programa | Aprovado | A compilação terminou sem erro e os 37 testes automatizados foram aprovados. |
| Interface web | Aprovado | O teste do Streamlit confirmou título, mensagem inicial, entrada de chat e reinício da conversa. |
| Consistência das chaves | Aprovado | `query` e `historico` são iguais no template e na configuração do componente de memória. |

## 7. Segurança e privacidade

A chave da OpenAI funciona como uma senha do serviço. Por isso, foi mantida em arquivo local separado e não foi incluída no código, na documentação ou nas saídas de teste. O `.gitignore` impede o envio acidental do `.env` ao repositório.

> **Orientação de segurança:** a chave não deve ser enviada por mensagem, capturada em tela ou incluída no Git. Se houver suspeita de exposição, ela deve ser revogada e substituída na plataforma da OpenAI.

## 8. Limitações atuais

- A interface web é local; ainda não foi publicada em um serviço de hospedagem.
- A base RAG é deliberadamente pequena e lexical; ainda não usa embeddings nem fontes institucionais externas.
- O conteúdo é gerado por inteligência artificial e deve ser tratado como orientação, não como decisão profissional automática.
- O uso da API pode gerar custos conforme o volume de solicitações e as regras da conta utilizada.
- A retenção é configurável e testada, mas sua política institucional e seus responsáveis ainda precisam ser aprovados.
- Autenticação, separação por usuário e hospedagem controlada dependem da infraestrutura escolhida.

## 9. Recomendações e próximos passos

| Prioridade | Recomendação | Resultado esperado |
|---|---|---|
| Alta | Definir política de retenção e proteção do banco. | Governança do histórico persistente. |
| Alta | Publicar a interface Streamlit em ambiente controlado. | Acesso por navegador sem instalação local. |
| Alta | Definir limites de custo, logs e alertas de consumo. | Operação previsível e acompanhamento financeiro. |
| Média | Adicionar uma base de conhecimento validada sobre geociências e carreira. | Respostas mais rastreáveis e alinhadas ao conteúdo institucional. |
| Média | Criar testes automatizados de comportamento e segurança. | Menor risco de regressão durante novas implementações. |
| Média | Realizar piloto com geocientistas e coletar feedback. | Validação de utilidade, clareza e adequação das recomendações. |
| Média | Substituir ou ampliar a base piloto somente com fontes institucionais revisadas. | RAG mais abrangente sem perder rastreabilidade. |

## 10. Conclusão executiva

O GeoAI Mentor atingiu o objetivo desta fase: demonstrar uma conversa especializada, conectada à OpenAI e capaz de manter contexto durante uma sessão. Os testes confirmaram o funcionamento, a consistência da configuração e a proteção da credencial.

O resultado deve ser entendido como um protótipo funcional com persistência local, gerenciamento de sessões e um piloto RAG controlado. A recomendação é definir governança do banco e das fontes, adicionar controles de custo e validar a utilidade com usuários antes de ampliar a base.

---

## Apêndice A — Evidência técnica

Esta seção preserva os elementos necessários para comprovar tecnicamente a implementação. Os registros completos permanecem no documento passo a passo; abaixo está a síntese auditável.

| Categoria | Comando ou verificação | Resultado |
|---|---|---|
| Ambiente | `.venv\Scripts\python.exe --version` | Python 3.12.13 executado no ambiente isolado. |
| Dependências | `pip install -r requirements.txt` | `python-dotenv`, `langchain` e `langchain-openai` instalados e importáveis. |
| Compilação | `.venv\Scripts\python.exe -m py_compile chatbot_mentor.py` | Conclusão sem erros. |
| Execução funcional | `.venv\Scripts\python.exe chatbot_mentor.py` | Duas respostas exibidas e processo encerrado com código zero. |
| Chave | Verificação estrutural do `.env` | Uma atribuição `OPENAI_API_KEY` encontrada; valor não exibido. |
| Singleton | Comparação de identidade do histórico | Mesma sessão retornou o mesmo objeto; sessão distinta retornou outro. |
| Memória | Duas perguntas com `session_id=sessao_demo` | A segunda resposta recuperou Python do contexto anterior. |

### A.1 Retorno da API e comportamento observado

Na pergunta inicial, o usuário informou ser geofísico, desejava migrar para dados e perguntou qual linguagem aprender primeiro. O modelo recomendou Python como linguagem principal.

Na pergunta seguinte, o usuário perguntou que projeto poderia criar usando _“essa linguagem”_. Com a memória ativa, o modelo associou a expressão a Python e sugeriu projetos relacionados, incluindo análise de dados sísmicos e outras aplicações de geociências.

> **Critério de aceite atendido:** a mudança entre o teste sem memória e o teste com memória demonstrou recuperação do contexto, pois deixou de ser necessário perguntar qual linguagem estava sendo mencionada.

## Apêndice B — Evidência executiva

A evidência executiva converte os achados técnicos em indicadores que permitem decisão sem exigir leitura de código.

| Dimensão | Indicador | Avaliação executiva |
|---|---|---|
| Entrega | 6/6 etapas concluídas | Escopo integral desta fase entregue. |
| Qualidade | 9/9 critérios finais aprovados | Nenhum erro comum identificado na revisão. |
| Funcionalidade | 2/2 perguntas respondidas | Conexão e geração de respostas comprovadas. |
| Contexto | Referência anterior recuperada | Memória conversacional comprovada na mesma sessão. |
| Segurança | Credencial não exposta | Tratamento básico da chave aprovado. |
| Prontidão | Protótipo funcional | Adequado para demonstração e evolução; ainda não é produção. |

## Apêndice C — Artefato reproduzível

Os arquivos e as instruções abaixo permitem repetir a validação em uma estação Windows com Python e uma chave válida da OpenAI.

### C.1 Arquivos necessários

| Arquivo | Finalidade |
|---|---|
| `geoai_mentor/application/` | Serviço de aplicação e casos de uso. |
| `geoai_mentor/domain/` | Contratos e erros independentes de frameworks. |
| `geoai_mentor/infrastructure/` | Integração com LangChain, OpenAI e repositório SQLite. |
| `geoai_mentor/interfaces/` | Implementações da interface web e do terminal. |
| `geoai_mentor/config/` | Configuração centralizada e validada. |
| `chatbot_mentor.py` | Ponto de entrada compatível do terminal. |
| `streamlit_app.py` | Ponto de entrada compatível do Streamlit. |
| `requirements.txt` | Lista das bibliotecas necessárias. |
| `requirements-dev.txt` | Dependências para executar os testes. |
| `tests/` | Testes automatizados de memória e interface. |
| `Analise/docsgeo/` | Dez fontes Markdown curadas e autorizadas para o piloto RAG local. |
| `.env` | Configuração local da `OPENAI_API_KEY`; não deve ser versionado. |
| `.env.example` | Modelo seguro do nome da variável, sem chave real. |
| `.gitignore` | Proteção contra inclusão acidental do `.env` e do ambiente virtual. |

### C.2 Como repetir os testes

1. Abra o PowerShell na pasta raiz do projeto.
2. Ative o ambiente virtual com `.venv\Scripts\Activate.ps1`.
3. Instale ou confirme as dependências com `pip install -r requirements.txt`.
4. Confirme que o `.env` contém `OPENAI_API_KEY` com uma chave válida, sem exibi-la no terminal.
5. Execute a compilação: `python -m py_compile chatbot_mentor.py`.
6. Execute os testes automatizados: `python -m pytest -q`.
7. Execute a interface: `streamlit run streamlit_app.py`.
8. Faça duas perguntas relacionadas e verifique se a segunda considera a linguagem recomendada na primeira.

### C.3 Critérios de aprovação

- A compilação termina sem mensagem de erro.
- A chave não aparece no console, no código nem no relatório.
- As duas respostas são apresentadas no terminal.
- A segunda resposta compreende a referência à linguagem indicada anteriormente.
- Uma nova sessão recebe histórico separado da sessão de demonstração.
- A execução falha automaticamente se a cobertura total ficar abaixo de 85%.

## Rastreabilidade

Os detalhes, decisões, correções e evidências de cada etapa estão em:

- `Analise/RegistroPassoAPasso_Implementacao_GeoAI_Mentor.docx`;
- `Analise/RelatorioExecutivoConsolidado_GeoAI_Mentor.docx`.

---

## Manual do usuário — GeoAI Mentor

Guia de instalação, execução, testes, validação e operação local da prova de
conceito. Versão 1.0, de 17 de agosto de 2026, com início do piloto previsto
para 24 de agosto de 2026.

> **Escopo:** POC para dois participantes. O ambiente local está funcional;
> Microsoft Entra ID, Azure App Service e Azure Database for PostgreSQL fazem
> parte da próxima implantação e ainda não estão provisionados.

> **Importante:** o GeoAI Mentor produz orientação assistida por IA. As
> respostas não devem ser usadas como decisão técnica, profissional ou
> institucional sem revisão humana.

### 1. Antes de começar

O manual orienta participantes e responsáveis pela POC na instalação,
execução, validação e operação básica do GeoAI Mentor. Ele consolida o registro
da implementação evolutiva e o roteiro de testes e custos do ambiente.

#### O que já funciona

- Interface web Streamlit e versão de terminal.
- Conversas persistidas em SQLite: criar, listar, reabrir, renomear e excluir.
- Memória por conversa, com isolamento entre identificadores.
- RAG lexical local com dez fontes Markdown curadas em `Analise/docsgeo`.
- Retenção configurável, backup local, limites da API e logs redigidos.
- 49 testes automatizados aprovados e cobertura total de 88,50%.

#### O que ainda não está disponível

- Login pelo Microsoft Entra ID e separação persistente por usuário autenticado.
- Publicação no Azure App Service e banco Azure Database for PostgreSQL.
- Bloqueio financeiro integral somando Azure e OpenAI.
- Piloto real com os dois geocientistas e avaliação final das fontes institucionais.

### 2. Preparar o ambiente

#### Pré-requisitos

- Windows com PowerShell.
- Python 3.12 recomendado.
- Chave válida da API OpenAI para testes com respostas reais.
- Acesso à pasta `E:\ProjAlura`.

#### Configuração inicial

1. Abra o PowerShell na pasta `E:\ProjAlura`.
2. Ative o ambiente virtual.
3. Instale as dependências de desenvolvimento.
4. Copie `.env.example` para `.env` e preencha somente a chave local.

```powershell
cd E:\ProjAlura
.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
Copy-Item .env.example .env
```

#### Variáveis principais

| Variável | Finalidade / padrão |
|---|---|
| `OPENAI_API_KEY` | Obrigatória para respostas reais; nunca versionar. |
| `OPENAI_MODEL` | Modelo de texto; padrão atual: `gpt-5.6-sol`. |
| `GEOAI_DATABASE_PATH` | Banco local; padrão: `data/geoai_mentor.db`. |
| `GEOAI_KNOWLEDGE_PATH` | Base RAG; padrão: `Analise/docsgeo`. |
| `OPENAI_REQUEST_TIMEOUT` | Tempo limite da chamada; padrão: 30 segundos. |
| `OPENAI_MAX_OUTPUT_TOKENS` | Máximo de saída; padrão: 1.200 tokens. |
| `GEOAI_RETENTION_DAYS` | Retenção local; padrão aprovado: 90 dias. |

> **Segurança:** nunca cole a chave em código, captura de tela, relatório,
> mensagem ou Git. Se houver exposição, revogue-a e crie outra.

### 3. Testar antes de usar

A suíte padrão usa substitutos controlados e não realiza chamadas reais à
OpenAI. Portanto, executar apenas o pytest não gera custo de API.

```powershell
python -m pytest -q
```

| Critério | Resultado esperado |
|---|---|
| Testes | 49 aprovados. |
| Cobertura | Pelo menos 85%; última medição: 88,50%. |
| API real | Nenhuma chamada nos testes padrão. |
| Concorrência | 12 gravações em 4 workers, isoladas e completas. |

Para abrir a interface:

```powershell
streamlit run streamlit_app.py
```

O navegador deverá abrir automaticamente. Caso isso não ocorra, use o endereço
local exibido no PowerShell, normalmente `http://localhost:8501`.

### 4. Usar o GeoAI Mentor

1. Digite uma pergunta no campo de chat e envie.
2. Aguarde a resposta; chamadas reais podem consumir a API.
3. Faça uma pergunta complementar para verificar se o contexto foi preservado.
4. Confira as fontes quando a resposta utilizar a base RAG.

> **Exemplo de memória:** pergunte qual linguagem aprender primeiro e, em
> seguida, pergunte “Que projeto posso criar com essa linguagem?”. A segunda
> resposta deve compreender a referência anterior.

#### Gerenciar conversas

| Ação | Como usar |
|---|---|
| Nova conversa | Use o comando correspondente na barra lateral. |
| Reabrir | Selecione uma conversa existente; o histórico volta à tela. |
| Renomear | Altere o título para facilitar a localização. |
| Excluir | Confirme a exclusão; as mensagens relacionadas são removidas em cascata. |

#### Validar o RAG

A recuperação pesquisa somente arquivos Markdown da pasta autorizada. Faça
perguntas relacionadas aos dez documentos e confirme se a resposta identifica
a fonte. Para assuntos sem evidência, o sistema deve informar a ausência de
suporte sem inventar uma fonte.

> **Limite conhecido:** a busca é lexical, local e adequada à POC. Os dez
> documentos ainda precisam de aprovação institucional final antes de uso além
> do piloto.

### 5. Roteiro de validação da POC

| Etapa | Ação | Critério de aceite |
|---:|---|---|
| 1 | Executar pytest. | 49 testes aprovados e cobertura igual ou superior a 85%. |
| 2 | Abrir o Streamlit. | A tela carrega sem revelar segredo. |
| 3 | Criar duas conversas. | Os históricos não se misturam. |
| 4 | Reabrir e renomear. | O conteúdo e o novo título permanecem. |
| 5 | Fazer pergunta coberta pelo RAG. | A resposta traz fonte pertinente. |
| 6 | Perguntar fora da base. | O sistema declara falta de evidência. |
| 7 | Excluir uma conversa. | A conversa e suas mensagens deixam de aparecer. |
| 8 | Criar e verificar backup. | Um arquivo restaurável é criado em `backups/`. |

#### Metas de feedback dos dois participantes

- Utilidade percebida: média igual ou superior a 4/5.
- Clareza: média igual ou superior a 4/5.
- Fontes corretas e presentes quando necessárias: pelo menos 90%.
- Recusa adequada fora da base: pelo menos 90%.
- Conclusão das tarefas: pelo menos 80%.
- Zero exposição de segredo e zero acesso cruzado.

### 6. Operação e manutenção local

```powershell
# Inspecionar o banco
python scripts\operacoes_geoai.py status

# Criar backup
python scripts\operacoes_geoai.py backup

# Aplicar retenção de 90 dias
python scripts\operacoes_geoai.py retencao --dias 90
```

O backup consistente é gravado por padrão em `backups/` e fica fora do Git. O
período aprovado para os backups da futura POC Azure é de 30 dias.

> **Atenção:** a retenção exclui conversas cuja última atualização seja
> anterior ao limite. Crie e verifique um backup antes da execução manual.

#### Diagnóstico rápido

| Sintoma | Verificação |
|---|---|
| Chave ausente | Confirme que `.env` existe e contém `OPENAI_API_KEY`, sem exibir o valor. |
| Modelo não responde | Verifique internet, saldo, modelo permitido e timeout. |
| RAG não encontra fonte | Confirme `GEOAI_KNOWLEDGE_PATH` e os arquivos `.md` em `Analise/docsgeo`. |
| Histórico não aparece | Confirme `GEOAI_DATABASE_PATH` e a permissão de escrita na pasta `data`. |
| Streamlit não abre | Leia a URL no terminal e confirme que a porta não está ocupada. |

### 7. Custos e orçamento da POC

O orçamento total aprovado é R$ 50 para Azure e OpenAI em conjunto. As
estimativas variam com câmbio, impostos, tokens, tempo de execução e preços
vigentes.

| Componente / cenário | Estimativa | Observação |
|---|---:|---|
| Testes automatizados | R$ 0 de API | Usam substitutos e não chamam a OpenAI. |
| App Service Linux F1 | R$ 0 | Sem SLA e com limites; apropriado apenas à POC. |
| PostgreSQL B1ms por 14 dias | Aproximadamente R$ 29,50 mais armazenamento | Parar quando ocioso; o armazenamento continua cobrado. |
| OpenAI Sol, 20 interações típicas | Aproximadamente R$ 4 | Exemplo com 3.000 tokens de entrada e 800 de saída. |
| Margem de segurança | R$ 10 | Reserva de 20% do orçamento. |
| Total de planejamento | Aproximadamente R$ 44–50 | Depende principalmente do banco e do uso real. |

#### Economizar durante o piloto

- Preferir `gpt-5.6-luna` quando a qualidade for suficiente.
- Parar o PostgreSQL quando o piloto estiver inativo e remover os recursos ao encerrar.
- Manter respostas curtas, limitar o histórico e acompanhar tokens por participante.
- Usar alertas em 50%, 75%, 80%, 90% e 100% e bloquear novas chamadas OpenAI no teto interno de R$ 40.
- Registrar todo o consumo mesmo quando créditos do Azure for Students evitarem desembolso direto.

### 8. Evolução por portões

| Portão | Situação | Entrega principal |
|---:|---|---|
| 0 | Aprovado | Linha de base e credencial fora do Git. |
| 1 | Aprovado | Separação entre interface, aplicação, domínio, infraestrutura e configuração. |
| 2 | Aprovado | SQLite transacional e isolamento por conversa. |
| 3 | Aprovado | Cobertura mínima automatizada e testes sem API real. |
| 4 | Aprovado | Gerenciamento completo das conversas. |
| 5 | Aprovado para piloto | RAG local controlado, fontes e recusa sem evidência. |
| 6 | Parcialmente aprovado | Prontidão técnica local concluída; validações externas pendentes. |

#### Próxima implantação planejada

| Decisão | Definição da POC |
|---|---|
| Identidade | Microsoft Entra ID em tenant único. |
| Hospedagem | Azure App Service na região `eastus`. |
| Persistência | Azure Database for PostgreSQL iniciado vazio. |
| Participantes | Dois; as contas autorizadas ainda precisam ser definidas. |
| Retenção | Conversas por 90 dias e backups por 30 dias. |
| Responsável por alertas | `fredjml.br@gmail.com`. |
| Início previsto | 24/08/2026. |

> **Estado real:** a tabela registra decisões, não comprova implantação.
> Autenticação, PostgreSQL, hospedagem e controle unificado de custos ainda
> exigem implementação e provisionamento.

### 9. Uso responsável e privacidade

- Não inserir dados pessoais, confidenciais, estratégicos ou sujeitos a sigilo.
- Revisar toda recomendação antes de usá-la em trabalho técnico ou decisão profissional.
- Registrar feedback de forma anonimizada, conforme aprovado para a POC.
- Excluir conversas de teste que não precisem ser preservadas.
- Comunicar imediatamente suspeita de vazamento, acesso indevido ou gasto anormal ao responsável pelo piloto.

#### Pendências antes do piloto hospedado

- Definir as duas contas participantes e se o tenant inteiro ou apenas uma lista terá acesso.
- Definir administrador, suporte, privacidade, incidentes e solicitações de exclusão.
- Definir acesso administrativo ao PostgreSQL e destino autorizado dos backups.
- Aprovar formalmente os dez documentos RAG e a regra de citação.
- Definir duração, número de conversas e comportamento ao atingir o limite financeiro.

### 10. Referências do manual

- [OpenAI — gpt-5.6-sol](https://developers.openai.com/api/docs/models/gpt-5.6-sol)
- [OpenAI — comparação de modelos](https://developers.openai.com/api/docs/models/text)
- [Azure App Service Linux — preços](https://azure.microsoft.com/en-us/pricing/details/app-service/linux/)
- [Azure — limites dos serviços](https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/azure-subscription-service-limits)
- [Azure Database for PostgreSQL — preços](https://azure.microsoft.com/pt-br/pricing/details/postgresql/flexible-server/)
- [Azure Database for PostgreSQL — visão geral](https://learn.microsoft.com/en-us/azure/postgresql/overview)
- [Azure for Students — acompanhamento de custos](https://learn.microsoft.com/en-us/azure/education-hub/navigate-costs)

## Site do projeto no GitHub

https://github.com/fredjml/aluraCarreiraEspecialistaIA

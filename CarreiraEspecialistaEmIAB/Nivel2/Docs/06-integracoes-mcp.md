# Integrações MCP e pendências de fechamento

## O que já funciona localmente

- O servidor `scripts/bytebank_mcp_server.py` usa o protocolo MCP por stdio.
- O recurso `bytebank://policies/public` expõe políticas fictícias públicas.
- A ferramenta `consultar_politicas` pesquisa o dataset local e retorna fontes.
- O prompt `resposta_fundamentada` orienta respostas rastreáveis.
- A ferramenta `solicitar_cartao` exige `aprovado_por_humano=true` antes de qualquer chamada externa.

## O que você precisa fornecer para integração externa

1. Escolher o core/API de demonstração ou homologação que atenderá saldo, fatura e solicitação de cartão.
2. Obter URL base, método de autenticação, escopos e contrato de cada endpoint.
3. Preencher apenas no arquivo local `.env`:
   - `BYTEBANK_CORE_API_BASE_URL`
   - `BYTEBANK_CORE_API_TOKEN`
4. Definir quem pode aprovar mutações e como a decisão será registrada.
5. Configurar autorização por usuário antes de liberar conteúdos `interno` ou `restrito`.
6. Definir retenção, logs, monitoramento, orçamento e procedimento de incidente.

## Como ativar no VS Code

1. Instale dependências no ambiente virtual: `python -m pip install -r requirements.txt`.
2. Copie `.env.example` para `.env` e preencha somente credenciais autorizadas.
3. Reabra a janela do VS Code para ele detectar `.vscode/mcp.json`.
4. Habilite o servidor `bytebank-nivel2` no painel de ferramentas MCP do Chat.
5. Teste primeiro `consultar_politicas`; depois teste leituras externas com referências fictícias de homologação.
6. Só teste `solicitar_cartao` depois de confirmar o fluxo HITL e o ambiente de homologação.

## Pendências para fechar o projeto

| Pendência | Dono sugerido | Critério de conclusão |
|---|---|---|
| Dependências MCP | Pessoa desenvolvedora | `mcp` instalado e servidor listado pelo VS Code |
| API externa | Responsável pela plataforma | Endpoint homologado, autenticação e contrato testados |
| Credenciais | Responsável por segurança | Segredos apenas em `.env` ou cofre, nunca no Git |
| Controle de acesso | DPO e segurança | Filtro por usuário e `nivel_acesso` antes da recuperação |
| HITL | Operação de crédito | Aprovador, SLA, snapshot e auditoria definidos |
| Avaliação LLM | Ciência de dados | Modelo/juiz autorizado e resultados reproduzíveis |
| Portfólio | Pessoa autora | Concluído: GitHub Pages publicado e Google Sheets acessível por link no README |
| Evidências finais | Pessoa autora | Relatórios, testes e link do repositório revisados |

## Limites

Sem uma API escolhida e credenciais fornecidas por você, as ferramentas externas retornam `not_configured`. Isso é intencional: o projeto não executa leitura ou mutação em sistemas externos por padrão.

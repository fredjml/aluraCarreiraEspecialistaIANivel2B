# Arquitetura multiagente

## Componentes

O front-end Gradio conversa com o BFA, que contém supervisor, roteador e síntese. O supervisor usa classificação estruturada Gemini para escolher exatamente `conta_corrente`, `cartao_credito` ou `suporte`; indisponibilidade de rede/API aciona um classificador local rastreável. Em seguida, encaminha via A2A ao agente especializado correspondente.

Cada Agent Card registra `nome`, `descricao`, `url`, `skills` e `versao`. No protótipo as URLs são placeholders locais e não representam serviços publicados.

## A2A e MCP

- **A2A:** comunicação entre supervisor e agentes, com contrato de tarefa, estado, resposta e rastreabilidade.
- **MCP:** acesso padronizado a capacidades do banco. O servidor stdio implementado em `scripts/bytebank_mcp_server.py` expõe as ferramentas de mutação `criar_conta` e `solicitar_cartao`, ambas bloqueadas por `aprovado_por_humano`; recursos URI de leitura para saldo, fatura e políticas públicas; e prompt de resposta fundamentada.

| Critério | A2A | MCP |
|---|---|---|
| Foco | Agente para agente | Agente para ferramenta, recurso ou prompt |
| Estado | Pode acompanhar uma tarefa e seu ciclo de vida | Normalmente chamada de capacidade, com estado controlado pelo servidor |
| Complexidade | Contratos, roteamento e conectividade | Catálogo e permissões de capacidades |
| Uso no Bytebank | Supervisor conversa com os três agentes | Agentes consultam dados e solicitam mutações autorizadas |

Polling atende tarefas simples de conta; SSE/streaming atende suporte quando há atualização de status; webhook é adequado para eventos de aprovação ou fraude. O protótipo simula as três decisões sem rede.

## Memórias

- **Semântica:** políticas e definições recuperáveis.
- **Episódica:** histórico de interações e decisões, com retenção e anonimização controladas.
- **Procedural:** regras de atendimento, autorização, escalonamento e prompts versionados.

## HITL para Platinum

1. O agente identifica solicitação de cartão Platinum.
2. Antes de qualquer mutação, o grafo executa `interrupt_before` no ponto de aprovação.
3. É capturado um snapshot com mensagem, classificação, evidências e versão do fluxo.
4. Uma pessoa autorizada decide `aprovar` ou `cancelar`, sem editar a evidência.
5. `aprovar` retoma o fluxo e chama a ferramenta de mutação; `cancelar` encerra com motivo auditável.

O estado `requer_aprovacao_humana` materializa a pausa no grafo para Platinum, e o servidor MCP recusa a mutação enquanto a aprovação não for explícita. O protótipo não executa aprovação financeira real; sem endpoint/token do core, retorna `not_configured`.

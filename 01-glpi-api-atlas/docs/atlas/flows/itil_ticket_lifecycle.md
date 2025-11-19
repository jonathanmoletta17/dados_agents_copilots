# Fluxo ITIL: Abertura → Atribuição → Followup/Tarefa → Solução → Fechamento

## Abertura de Ticket
- `POST /Ticket`
- Campos mínimos: `name`, `content`, `itilcategories_id`, `entities_id`, `type`.

## Atribuição
- Técnico: `POST /Ticket_User` com `type=2` e `users_id`.
- Grupo técnico: `POST /Group_Ticket` com `type=2` e `groups_id`.

## Followup
- `POST /ITILFollowup` com `itemtype="Ticket"`, `items_id=<ticket_id>`, `content`.

## Tarefa
- `POST /Task` (ou `ITILTask` conforme sua instância) com `itemtype="Ticket"`, `items_id`, `content`.

## Solução
- `PUT /Ticket/{id}` atualizando `status=5` e `solvedate`.

## Fechamento
- `PUT /Ticket/{id}` atualizando `status=6` e `closedate`.

## Observações
- Usar `range` para paginação em listagens.
- Configurar headers `App-Token` e `Session-Token` em todas as requisições.
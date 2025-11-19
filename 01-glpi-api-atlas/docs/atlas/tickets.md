# Tickets

## Listar
- `GET /Ticket` com `range` (ex.: `0-999`), `expand_dropdowns=false`, `get_hateoas=false`.

## Obter
- `GET /Ticket/{id}`.

## Criar/Atualizar/Remover
- `POST /Ticket`, `PUT /Ticket/{id}`, `DELETE /Ticket/{id}`.

## Campos Comuns
- `id`, `name`, `content`, `status`, `priority`, `urgency`, `impact`, `itilcategories_id`, `entities_id`.
- Datas: `date`, `date_mod`, `solvedate`, `closedate`.

## Status
- Mapa conforme uso em scripts do projeto:
  - `1: Novo`, `2: Em andamento (atribuído)`, `3: Em andamento (planejado)`, `4: Pendente`, `5: Solucionado`, `6: Fechado`.

## Relacionamentos
- `Ticket_User`:
  - `type=1` → requerente; `type=2` → técnico.
- `Group_Ticket`:
  - `type=2` → grupo técnico.

## Exemplo de Paginação
- Blocos de 1000, avançando `range` até a página vir vazia ou menor que 1000.
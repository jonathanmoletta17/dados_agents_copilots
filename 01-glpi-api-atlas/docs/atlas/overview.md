# GLPI API Atlas – Visão Geral

## Objetivo
Mapear a API REST do GLPI e fornecer especificações, cliente SDK e exemplos práticos para uso contínuo.

## Autenticação
- Headers: `App-Token`, `Session-Token`.
- Rotas: `/initSession`, `/killSession`.

## Paginação
- Parâmetro `range`: `start-end` (ex.: `0-999`).
- Respostas podem ser `200` ou `206` (parcial).

## Recursos Cobertos
- Núcleo ITIL: `Ticket`, `User`, `Group`, `Entity`, `ITILCategory`.
- Relacionamentos: `Ticket_User` (type 1 requerente, 2 técnico), `Group_Ticket` (type 2 grupo técnico).
- Busca: `/search/Ticket` com `criteria[]` e `forcedisplay[]`.

## Convenções de Performance
- `expand_dropdowns=false` e `get_hateoas=false` para respostas enxutas.
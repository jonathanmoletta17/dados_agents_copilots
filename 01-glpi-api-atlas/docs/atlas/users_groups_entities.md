# Usuários, Grupos e Entidades

## Usuários (`/User`)
- Listagem paginada via `range`.
- Campos comuns: `id`, `firstname`, `realname`.
- Nome normalizado: `"firstname realname"`.

## Grupos (`/Group`)
- Listagem paginada via `range`.
- Campos comuns: `id`, `name`.
- Usado para atribuição de tickets como grupo técnico (`type=2`).

## Entidades (`/Entity`)
- Listagem paginada via `range`.
- Campos comuns: `id`, `name`.
- Estrutura organizacional para agrupar tickets e usuários.

## Perfis
- Perfis controlam permissões dos usuários (visão geral). Ajustes por administração do GLPI.

## Relações com Tickets
- `Ticket_User`:
  - Requerente (`type=1`) e Técnico (`type=2`).
- `Group_Ticket`:
  - Grupo técnico (`type=2`).
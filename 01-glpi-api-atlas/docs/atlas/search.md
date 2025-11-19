# Busca

## Rota
- `GET /search/Ticket`

## Parâmetros
- `range`: paginação.
- `criteria[i][field]`: campo.
- `criteria[i][searchtype]`: tipo de busca (ex.: `contains`).
- `criteria[i][value]`: valor.
- `forcedisplay[]`: adicionar colunas à resposta.

## Exemplo
- Buscar tickets cujo `name` contém `VPN` e exibir `id` e `name`.
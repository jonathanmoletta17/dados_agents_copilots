# Autenticação

## Headers
- `App-Token`: token da aplicação.
- `Session-Token`: token de sessão do usuário autenticado.

## Rotas
- `GET /initSession`: obtém `session_token`.
- `GET /killSession`: encerra sessão ativa.

## Boas Práticas
- Armazenar tokens somente em variáveis de ambiente.
- Não logar segredos em produção.
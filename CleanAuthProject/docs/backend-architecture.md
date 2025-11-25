# Backend Architecture — CleanAuthProject

Este documento consolida a arquitetura e contratos do backend para autenticação de usuário e criação de tickets no GLPI. É um guia de referência do que é essencial e não deve ser removido.

## Visão Geral
- Framework: Flask (servidor HTTP)
- Cliente HTTP: `requests`
- Integração: GLPI REST API
- Endpoints expostos:
  - `POST /api/authenticate-user`
  - `POST /api/create-ticket`
- Configuração via variáveis de ambiente (e opcionalmente `CleanAuthProject/.env`).

## Estrutura do Projeto
- `CleanAuthProject/app.py`: define a aplicação Flask e endpoints.
- `CleanAuthProject/services/glpi.py`: integrações com a API do GLPI.
- `CleanAuthProject/config.py`: carrega `GLPI_URL`, `GLPI_APP_TOKEN`, `GLPI_USER_TOKEN` do ambiente/`.env`.
- `CleanAuthProject/requirements.txt`: dependências fixadas.
- `CleanAuthProject/scripts/run_server.py`: inicializa o servidor em `127.0.0.1:5001`.
- `CleanAuthProject/__init__.py` e `CleanAuthProject/services/__init__.py`: manutenção de pacotes Python.

## Configuração
- `.env` (opcional) em `CleanAuthProject/.env`:
  - `GLPI_URL` (ex.: `http://<host>/glpi/apirest.php`)
  - `GLPI_APP_TOKEN` (obrigatório para chamadas ao GLPI)
  - `GLPI_USER_TOKEN` (recomendado para buscas de usuário por e-mail)
- `config.py`:
  - Usa `python-dotenv` se `.env` existir; não sobrescreve variáveis já definidas no ambiente.
  - `load_settings()` expõe `glpi_url`, `glpi_app_token`, `glpi_user_token`.

## Endpoints

### POST `/api/authenticate-user`
- Headers: `Content-Type: application/json`
- Body:
  ```json
  { "email": "string", "password": "string" }
  ```
- Validações:
  - `Content-Type` deve conter `application/json`.
  - JSON deve ser objeto.
  - `email` e `password` não podem ser vazios.
- Fluxo interno:
  1. Resolve `login` via `services/glpi.buscar_usuario_por_email(email)` (usa sessão de serviço com `USER_TOKEN`).
  2. Autentica via `services/glpi.autenticar_por_login(login, password)` com `initSession`.
- Respostas:
  - 200: `{ "status": "ok", "session_token": "...", "login": "...", "user_id": <int>, "email": "..." }`
  - 401: `{ "status": "unauthorized", "message": "..." }`
  - 404: `{ "status": "not_found", "error": "email_not_found" }`
  - 422: campos ausentes/invalidos.
  - 500: `{ "status": "config_error" }` se ambiente inválido; `{ "status": "internal_error" }` para exceções.

### POST `/api/create-ticket`
- Headers: `Content-Type: application/json`, `Session-Token: <token do usuário>`.
- Body mínimo:
  ```json
  { "title": "string", "description": "string", "category_id": 123 }
  ```
- Opcionais:
  - `type` (int, padrão 1)
  - `status` (int, padrão 2)
  - `requester_user_id` (int)
  - `dry_run` (bool)
- Validações:
  - `Content-Type` deve conter `application/json`.
  - `Session-Token` obrigatório.
  - JSON deve ser objeto.
  - `title`, `description` não vazios; `category_id` inteiro.
- Dry-run:
  - Se `dry_run = true`, retorna payload simulado: `{ name, content, itilcategories_id, type, status, users_id_recipient, _users_id_requester }` (quando `requester_user_id` válido).
- Criação real:
  - Chama `services/glpi.criar_ticket_glpi(...)`.
- Respostas:
  - 200: `{ "status": "ok", "dry_run": true, "input": { ... } }` (dry-run)
  - 200/201: `{ "status": "ok", "ticket_id": <int> }` (real)
  - 401, 422, 502 conforme validações/GLPI; 500 para erros internos.

## Serviços GLPI (services/glpi.py)
- Config:
  - `BASE_URL = settings.glpi_url.rstrip("/")`
  - `APP_TOKEN = settings.glpi_app_token`
  - `USER_TOKEN = settings.glpi_user_token`
  - `TIMEOUT = 10`
- Helpers:
  - `_headers(session_token=None)`: monta cabeçalhos com `App-Token`, `Content-Type` e `Session-Token` (quando presente).
  - `_request(method, path, **kwargs)`: wrapper de `requests` (`BASE_URL/{path}` + `TIMEOUT`).
- Sessões de serviço:
  - `abrir_sessao_servico()`: `POST initSession` com `USER_TOKEN` para chamadas administrativas (ex.: busca de usuário por e-mail).
  - `kill_session(session_token)`: encerra sessão de serviço.
- Usuários:
  - `buscar_usuario_por_email(email)`: `GET search/User` com critérios `email`/`3`/`5` e `forcedisplay` (`1`, `2`, `3`, `9`); retorna `{ login, user_id, email }`.
  - `autenticar_por_login(login, password)`: `POST initSession` com login/senha; mapeia respostas e erros.
  - `autenticar_usuario_por_email(email, password)`: resolve login e autentica; retorna `{ status, session_token, login, user_id, email }`.
- Tickets:
  - `criar_ticket_glpi(session_token, title, description, category_id, type_=1, status=2, requester_user_id=None)`:
    - Valida `title`, `description`, `category_id`.
    - Monta `input_payload = { name, content, itilcategories_id, type?, status? }`.
    - Se `requester_user_id` válido, adiciona `users_id_recipient` e `_users_id_requester`.
    - `POST Ticket` com `json={"input": input_payload}` e `Session-Token` do usuário.
    - Sucesso: 200/201, captura `id` (lista ou objeto) e retorna `{ status: "ok", ticket_id, title, category_id }`.
    - 401/403: `{ status: "unauthorized" }`; demais: `{ status: "glpi_error", code, message, details }`.

## Fluxo End-to-End
1. Cliente chama `POST /api/authenticate-user` com e-mail/senha.
2. Backend resolve login e autentica, retornando `session_token` do usuário.
3. Cliente chama `POST /api/create-ticket` com `Session-Token` e payload mínimo.
4. Opcional: `dry_run` para validar payload sem criar ticket.
5. Criação real: persiste ticket no GLPI e retorna `ticket_id`.

## Itens Essenciais (não remover)
- `app.py`: endpoints e validações.
- `services/glpi.py`: todos os métodos, especialmente mapeamentos de `users_id_recipient` e `_users_id_requester`.
- `config.py`: carregamento de ambiente; `Settings` e `load_settings()`.
- `requirements.txt`: versões fixas (`Flask`, `requests`, `python-dotenv`).
- `scripts/run_server.py`: ponto de entrada do servidor.
- `__init__.py` (raiz e `services/`): garantem importação correta.

## Operação
- Instalação:
  ```
  python -m venv .venv
  .venv\Scripts\activate
  pip install -r CleanAuthProject/requirements.txt
  ```
- Execução do servidor:
  ```
  python CleanAuthProject/scripts/run_server.py
  # Servidor em http://127.0.0.1:5001/
  ```

## Troubleshooting
- 400 `bad_request`: verifique `Content-Type` e se body é JSON objeto.
- 401 `unauthorized`: checar `Session-Token` ausente/expirado ou credenciais incorretas.
- 422 `unprocessable_entity`: campos obrigatórios vazios ou `category_id` não-inteiro.
- 500 `config_error`: garanta `GLPI_URL` e `GLPI_APP_TOKEN` configurados.
- 502 `glpi_error`: inspeção de `details` e `message` retornados pelo GLPI.
- Exposição externa (Copilot/Teams): usar `cloudflared` (binário disponível), apontando para `http://127.0.0.1:5001/`.

## Observações
- `requester_user_id` é opcional, mas quando fornecido deve ser inteiro positivo para vincular corretamente o requerente no GLPI.
- `dry_run` é recomendado em integrações novas para validar mapeamento de payload.
- Scripts de validação/auditoria em `CleanAuthProject/scripts/` não são parte do runtime, mas ajudam na manutenção contínua.
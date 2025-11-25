# CleanAuthProject

Projeto Flask enxuto para autenticação e abertura de chamados via GLPI.

## Estrutura
- `app/` com `routes`, `services` e `utils`
- `config.py` para Settings via env (dotenv opcional)
- `scripts/run_server.py` para iniciar o servidor

## Endpoints
- `GET /api/health`
- `POST /api/authenticate-user` (credenciais: `user`+`password` ou `user_token`)
- `POST /api/create-ticket` (campos em `ticket`, requer `session_token`)

## Execução
1. `python -m pip install -r CleanAuthProject/requirements.txt`
2. Setar variáveis: `GLPI_URL`, `GLPI_APP_TOKEN`, opcional `GLPI_VERIFY_SSL`, `GLPI_TIMEOUT`, `PORT`, `DEBUG`
3. `python CleanAuthProject/scripts/run_server.py`

## Respostas
Envelope padrão via `app/utils/responses.py` com `status`, `message`, `code`, `data`, `request_id`.

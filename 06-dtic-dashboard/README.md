# DTIC Dashboard

Este repositório contém o backend (FastAPI) e o frontend (Vite) do dashboard de métricas do GLPI.

## Visão Geral
- Backend: `backend/` — API FastAPI com endpoints de métricas e ranking.
- Frontend: `frontend/` — aplicação Vite/TS que consome a API.
- Documentação: `docs/` — notas técnicas, auditorias e guias.

## Como executar o Backend
1. Configure as variáveis de ambiente (veja `backend/README.md` para detalhes):
   - `API_URL`, `APP_TOKEN`, `USER_TOKEN`
   - `RANKING_TECHNICIAN_PARENT_GROUP_ID` (opcional)
2. Instale dependências do backend:
   - `python -m pip install -r backend/requirements.txt`
3. Execute o servidor de desenvolvimento:
   - `python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000`

Documentação completa do backend: consulte `backend/README.md`.

## Como executar o Frontend
1. Instale dependências:
   - `cd frontend`
   - `npm install`
2. Execute o servidor de desenvolvimento:
   - `npm run dev`

## Notas
- Auditorias e planos de revisão estão em `docs/`, para referência histórica. O código atual já removeu artefatos obsoletos e está preparado para deploy simples em um único container.
# GLPI Dashboard (Backend + Frontend)
## Deploy simples no HSM (VM)

Premissas:
- Um único container serve API (FastAPI) e UI (frontend build) na mesma porta.
- Sem Nginx, sem múltiplos scripts: um `docker compose` e um `.env` no HSM.
- Segredos só em `backend/.env` na VM (não versionar).

Passos:
- Preparar `.env` no HSM: copie `backend/.env.example` e preencha `API_URL`, `APP_TOKEN`, `USER_TOKEN` e ajustes opcionais.
- Subir o serviço:
  - `docker compose up -d --build`
- Acesso:
  - UI: `http://<host>:<porta>/dashboard/`
  - Health: `http://<host>:<porta>/`
  - APIs: `http://<host>:<porta>/api/v1/metrics-gerais?inicio=YYYY-MM-DD&fim=YYYY-MM-DD` (e demais endpoints)

Porta:
- O container usa `8000` internamente. No HSM, ajuste o mapeamento em `docker-compose.yml` conforme necessidade (`"80:8000"`, `"443:8000"` com TLS externo, etc.). Não é preciso alterar código.

Operação:
- Atualizar UI/API: edite o código e rode `docker compose up -d --build` para reconstruir e reiniciar.
- Logs rápidos: `docker compose logs backend --tail=50`
- Parar/retomar: `docker compose stop` / `docker compose start`

Validação rápida:
- `curl http://localhost:8000/` → `200` e JSON com versão.
- `curl http://localhost:8000/dashboard/` → `200` (index.html do frontend).
- `curl "http://localhost:8000/api/v1/metrics-gerais?inicio=2024-01-01&fim=2024-12-31"` → payload com números.

Notas de simplicidade:
- Não usamos servidores adicionais (ex.: Nginx) nem múltiplas variantes de compose.
- Frontend é buildado no Dockerfile e servido pelo FastAPI em `/dashboard`.
- Vite dev server é apenas para desenvolvimento local; em produção, use somente o container.
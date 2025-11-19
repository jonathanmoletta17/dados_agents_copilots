# GLPI Smart Search

## Backend
- FastAPI rodando em `http://127.0.0.1:8099`
- Endpoints: `/search`, `/suggest`, `/export`, `/stats`, `/health`

## Frontend
- React + Vite + Tailwind em `04-glpi-smart-search/frontend`
- Scripts:
  - `npm install`
  - `npm run dev`
  - `npm run build`
  - `npm run preview`

## Integração
- Busca: `/search?q=incidente&status=solucionado&entidade=casa civil`
- Sugestões: `/suggest?field=entidade&prefix=casa`
- Exportação: `/export?q=incidente&format=xlsx&limit=100`

## Fluxo
1. Indexador carrega `02-analise-dados-glpi/data/processed/todos_tickets_atual_limpo.xlsx`
2. Backend fornece API com FTS5
3. Frontend consome API e apresenta filtros, resultados e exportação

## Arquitetura
- docs/architecture-diagram.png
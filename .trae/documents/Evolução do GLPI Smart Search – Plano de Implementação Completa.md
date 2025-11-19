## Objetivo
Evoluir o projeto 04-glpi-smart-search para entregar uma solução completa: UI moderna em React, exportação XLSX/CSV, melhorias de busca (correção ortográfica, autocomplete, operadores), documentação e testes.

## Escopo e Entregáveis
- Frontend React + Vite + Tailwind com barra única de busca, filtros por chips, destaque de termos, estatísticas, paginação e ordenação.
- Backend com endpoint /export (XLSX/CSV) alinhado aos parâmetros de /search.
- Melhorias de busca: correção ortográfica básica (levenshtein), autocomplete avançado, boost por recência/prioridade, suporte a operadores AND/OR/NOT.
- Documentação atualizada (README, diagrama de arquitetura) e suíte de testes (API e UI).

## Arquitetura
### Backend (FastAPI)
- Módulos:
  - app/main.py: manter /search, /suggest, /index/rebuild, /health.
  - app/export.py: implementar /export com geração de XLSX/CSV via pandas (openpyxl).
  - app/query_parser.py: parser simples de operadores (AND/OR/NOT), campos: status, tecnico, entidade, categoria, datas.
  - app/spellcheck.py: correção ortográfica com distância de edição e dicionários dos campos (entidade, técnico, categoria) pré-carregados do índice.
  - indexer/build_index.py: enriquecer índice com campos normalizados e tabelas auxiliares para sugestões frequentes.
- Ranking:
  - bm25 padrão do FTS5.
  - Boost: somar fatores (recência via data_modificacao recente; prioridade conhecida). Ex.: score_final = bm25 - recency_boost - priority_boost.
- Exportação:
  - /export?q=&filters=&format=xlsx|csv&limit=: aplicar mesma query/filtros de /search e retornar arquivo.

### Frontend (React + Vite + Tailwind)
- Páginas:
  - pages/Search.tsx: layout principal com barra de busca, chips de filtros, tabela de resultados, paginação/ordenação, botões de export.
- Componentes:
  - components/SearchBar.tsx: input com autocomplete (debounce), parsing de operadores.
  - components/FilterChips.tsx: chips de status, técnico, entidade, categoria, datas.
  - components/ResultsTable.tsx: tabela com highlight, colunas essenciais, ações.
  - components/StatsPanel.tsx: gráficos simples (contagem por status/entidade).
- Serviços:
  - services/api.ts: cliente para /search, /suggest, /export.
  - estado global (Zustand ou Context) para query e filtros; debounce para requisições.
- UI/UX:
  - Tailwind para responsividade; atalhos de teclado; URL compartilhável com estado da busca.

## Parsing e Correção Ortográfica
- query_parser: aceitar sintaxe "campo:valor" com operadores (AND/OR/NOT), parênteses simples.
- spellcheck: aplicar correção em termos de campos discretos (entidade, técnico, categoria) usando prefix + distância de edição; sugerir correção e aplicar opcionalmente.
- autocomplete: usar /suggest enriquecido (frequência de valores, prefix matching, synônimos básicos).

## Estrutura de Diretórios
```
04-glpi-smart-search/
  backend/
    app/
      main.py
      export.py
      query_parser.py
      spellcheck.py
    indexer/
      build_index.py
      search.db
  frontend/
    src/
      components/
      pages/
      services/
    public/
    package.json
  docs/
    architecture-diagram.png
    README.md
```

## Testes e Métricas
- API: pytest para /search, /suggest, /export (filtros, paginação, operadores).
- UI: vitest + testing-library para componentes e integração.
- Performance: medir latência p95 de /search com 10k+ registros; validar export ≤ 2s para 5k registros.
- Observabilidade: logs estruturados, métricas básicas (contagem de buscas/exportações).

## Roadmap de Implementação
1. Backend: adicionar /export e modularizar parser/spellcheck; enriquecer indexer.
2. Frontend: scaffolding Vite + Tailwind; implementar SearchBar, FilterChips, ResultsTable; integração com API.
3. Autocomplete e correção ortográfica; boost por recência/prioridade.
4. Estatísticas e export via UI; documentação e testes.

## Segurança
- Ler tokens via .env; sem segredos no repositório.
- CORS restrito; rate limiting básico.

## Critérios de Sucesso
- Frontend funcional com filtros e export.
- /export entrega XLSX/CSV alinhado à busca.
- Autocomplete e correção ortográfica ativos.
- Documentação atualizada e testes passando.

## Ação
Se aprovado, inicio a implementação criando os módulos backend, scaffold do frontend e integração, seguindo este plano e mantendo compatibilidade com o índice atual.
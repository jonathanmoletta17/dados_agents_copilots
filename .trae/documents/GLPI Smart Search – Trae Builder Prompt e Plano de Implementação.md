## Objetivo
Construir um mecanismo de busca moderno, rápido e amigável para dados do GLPI, superando o filtro padrão. O projeto segue ciclo completo: planejamento → arquitetura → indexação → API → UI → testes → métricas.

## Requisitos Funcionais
- Busca full‑text em `título`, `descrição`, `followups` e `documentos`.
- Filtros combináveis: `status`, `prioridade`, `categoria`, `entidade`, `técnico`, `grupo`, `intervalo de datas`.
- Operadores: `AND`, `OR`, `NOT`, agrupamentos com parênteses.
- Autocomplete e sugestões (campos e termos), correção ortográfica e normalização de acentos.
- Ranking por relevância: match no título > descrição; boost por recência, prioridade e status.
- Destaque (highlight) de termos encontrados.
- Exportar resultados para `XLSX` e salvar buscas.
- Histórico de consultas (auditável), favoritos e partilha via URL.

## Requisitos Não Funcionais
- Latência p95 ≤ 200 ms para top 50 resultados em base atual.
- Atualizações incrementais do índice em ≤ 1 min após mudança.
- Observabilidade (logs estruturados, métricas, tracing básico).
- Segurança: tokens em variáveis de ambiente, sem segredos no código.

## Arquitetura Proposta
### Fontes de Dados
- Primária: `03-integracao-glpi/database/glpi.sqlite` (espelho local do GLPI).
- Suporte: `01-glpi-api-atlas/sdk/python` para enriquecimento quando necessário.
- Limpeza: `02-analise-dados-glpi` para padronização de campos.

### Indexação
- Opção A (MVP – simples e rápido): `SQLite FTS5` com tabela `tickets_index` e tokenizer PT‑BR customizado (acentos, stopwords, stemming leve).
- Opção B (Escalável): `OpenSearch/Elasticsearch` com analisadores PT‑BR, sinônimos e relevância avançada.
- Campos indexados: `id`, `titulo`, `descricao`, `status`, `prioridade`, `categoria`, `entidade`, `tecnico`, `grupo`, `data_criacao`, `data_modificacao`, `followups_text`.
- Normalizações: remover HTML, normalizar acentos, lowercasing, limpeza de caracteres invisíveis, data ISO.
- Atualização: job incremental (polling de `data_modificacao`), mais job full rebuild.

### API (FastAPI)
- `GET /search`: parâmetros `q`, `filters{status, prioridade, categoria, entidade, tecnico, grupo, dt_ini, dt_fim}`, `page`, `size`, `sort`.
- `GET /suggest`: termos e campos para autocomplete.
- `POST /index/rebuild`: reconstruir índice (com auth).
- `GET /health` e `GET /metrics`: saúde e métricas Prometheus.
- Respostas com `highlight` e `score`.

### Frontend (React + Vite + Tailwind)
- Barra de busca única com parsing de operadores.
- Chips de filtros com contagem dinâmica.
- Sugestões em tempo real e correção de acentos/typos.
- Tabela de resultados com colunas essenciais e exportar `XLSX`.
- Painel lateral com estatísticas (por status, técnico, entidade).

### Segurança e Governança
- Tokens via `.env`/secret manager; nunca em repositório.
- Rate limit por usuário, logs de auditoria das consultas.
- CORS restrito conforme ambiente interno.

## Métricas de Sucesso
- p95 latência ≤ 200 ms; taxa de cliques em top 5 resultados ≥ 60%.
- Adoção: Nº de buscas/dia por gestores; tempo médio para encontrar um ticket.
- Precisão percebida (pesquisa interna): ≥ 80% satisfação.

## Testes e Validação
- Unitários: parsing de consulta, filtros, ranking.
- Integração: API + índice + base SQLite real (amostra).
- Performance: carga com 10k–100k tickets, medir latência p95/p99.
- UX: testes com cenários reais (ex.: “técnico:ganahan status:solucionado entidade:CASA CIVIL”).

## Estrutura de Diretórios (novo projeto)
```
bd_cau/
  04-glpi-smart-search/
    docs/
    backend/
      app/
      indexer/
      tests/
    frontend/
      src/
      public/
      tests/
    ops/
      docker/
      k8s/
    README.md
```

## Integrações
- Reutilizar `01-glpi-api-atlas` para enriquecimento e schemas.
- Consumir `glpi.sqlite` de `03-integracao-glpi` como fonte primária.
- Importar rotinas de limpeza de `02-analise-dados-glpi` (funções utilitárias).

## Roadmap
1. MVP com `SQLite FTS5`, API `GET /search`, filtros principais, export `XLSX`.
2. Sugestões/autocomplete e correção de acentos/typos.
3. Ranking avançado e painel de estatísticas.
4. Migração opcional para `OpenSearch` conforme volume.

## Prompt para Trae AI Builder (modo solo)
1. Criar projeto `bd_cau/04-glpi-smart-search` com `backend` (Python FastAPI) e `frontend` (React + Vite + Tailwind).
2. Backend:
   - Configurar `FastAPI`, `uvicorn`, `python-dotenv`, `sqlite3`/`sqlalchemy`, `pandas`, `openpyxl`.
   - Implementar `indexer` com `SQLite FTS5`: criar tabela `tickets_index` e popular a partir de `../03-integracao-glpi/database/glpi.sqlite`.
   - Funções de normalização (HTML→texto, acentos, datas ISO).
   - Endpoints: `GET /search`, `GET /suggest`, `POST /index/rebuild`, `GET /health`, `GET /metrics`.
   - Exportar resultados para `XLSX` usando `pandas` + `openpyxl`.
   - Configurar `.env` com tokens GLPI e caminhos da base.
3. Frontend:
   - Página única com barra de busca e filtros (status, técnico, entidade, categoria, datas).
   - Autocomplete e highlight; tabela com paginação; export `XLSX`.
   - Integração com API e estado global (Zustand/Recoil).
4. Testes:
   - Unitários (parsing e filtros), integração (API+DB), performance (locust/pytest‑benchmark).
   - Scripts `make test` e `make run`.
5. Entregáveis do MVP:
   - `GET /search` retornando ≤ 200 ms p95 (top 50).
   - UI com chips de filtro e destaque.
   - Export `XLSX` e salvar busca via URL.
6. Não incluir segredos; ler tokens via `.env`.

## Confirmação
Deseja que eu acione o Trae AI Builder para criar o projeto `04-glpi-smart-search` com essa arquitetura e iniciar pelo MVP com FTS5, API e UI básica? Posso prosseguir.
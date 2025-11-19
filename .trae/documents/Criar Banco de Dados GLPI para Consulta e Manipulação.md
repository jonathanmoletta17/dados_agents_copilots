## Objetivos
- Armazenar, de forma confiável e performática, todos os dados relevantes do GLPI (tickets, usuários, grupos, entidades, categorias e relacionamentos) para consultas rápidas pelo seu agente.
- Replicar fielmente o conjunto e as regras de transformação usadas no script `extrair_todos_tickets.py`, permitindo respostas JSON idênticas às do CSV `todos_tickets_atual.csv`.
- Suportar filtros por período (ex.: últimos 6 meses), paginação e agregações sem depender de chamadas online ao GLPI durante a consulta.

## Fontes de Dados GLPI
- Tickets: `GET /Ticket` paginado em blocos (1.000) — referência em scripts/python/extrair_todos_tickets.py:312-349.
- Users: `GET /User` paginado — 214-248.
- Entities: `GET /Entity` — 249-266.
- ITIL Categories: `GET /ITILCategory` — 267-284.
- Groups: `GET /Group` — 285-302.
- Relacionamentos:
  - `GET /Ticket_User` (type 1=Requerente, 2=Técnico) — 351-384.
  - `GET /Group_Ticket` (type 2=Grupo técnico) — 385-405.

## Modelagem de Dados (Core)
- `tickets` (PK: `id`): campos brutos do GLPI necessários para reproduzir os outputs do script:
  - `id`, `name`, `content`, `status`, `priority`, `urgency`, `impact`, `itilcategories_id`, `entities_id`, `date`, `date_mod`, `solvedate`, `closedate`, `solve_delay_stat`, `close_delay_stat`, `satisfaction`, `type`, `locations_id`, `global_validation`.
  - Metadados: `inserted_at`, `updated_at`, `source_fetched_at`.
- Dimensões:
  - `users` (PK: `id`): `firstname`, `realname`, `full_name` (normalizado), metadados.
  - `groups` (PK: `id`): `name`, metadados.
  - `entities` (PK: `id`): `name`, metadados.
  - `itilcategories` (PK: `id`): `name`, metadados.
- Relacionamentos:
  - `ticket_users`: (PK composto `tickets_id`,`users_id`,`type`) com `type` {1,2}.
  - `group_tickets`: (PK composto `tickets_id`,`groups_id`,`type`) com `type` {2}.

## Derivados e Views
- `tickets_flat` (materialized view ou tabela derivada): uma linha por ticket com joins e seleção das colunas textuais transformadas para JSON:
  - Seleção dos nomes de `Categoria`, `Entidade`.
  - Requerente: primeiro `ticket_users.type=1` por `tickets_id` ou default `'Sem Requerente'`.
  - Técnico: primeiro `ticket_users.type=2` ou default `'Não Atribuído'`.
  - Grupo: primeiro `group_tickets.type=2` ou default `'Sem Grupo'`.
  - Datas formatadas estilo brasileiro (pode ser feito na camada de API; armazenar datas em UTC e formatar na resposta).
  - Status traduzido via mapa do script (202-213), aplicado na resposta.

## Chaves e Índices
- `tickets(id)` PK.
- Índices recomendados: `tickets(date)`, `tickets(status)`, `tickets(entities_id)`, `tickets(itilcategories_id)` para filtros e relatórios.
- `ticket_users(tickets_id, type)`, `group_tickets(tickets_id, type)` para resoluções rápidas.
- Texto: se precisar de busca por `name/content`, considerar `GIN`/`tsvector` (PostgreSQL) com idioma pt.

## Estratégia de Ingestão (ETL)
- Carga inicial (full): varrer `Ticket` em blocos de 1.000 e popular dimensões e relacionamentos.
- Incremental (diário ou horário):
  - Critério: `date_mod` e/ou upsert por `id` (se GLPI não fornece filtro por modificação, repetir varredura paginada e upsert somente alterados; comparar `date_mod`).
  - Upsert (merge) em todas as tabelas base: `INSERT ... ON CONFLICT DO UPDATE` (Postgres) ou equivalente.
- Orquestração: job agendado (Windows Task Scheduler, cron via contêiner, ou serviço Python) com logs e métricas.
- Robustez: retry exponencial, limites de taxa, janela de paginação, fallback para full.

## Regras de Transformação (na Resposta)
- Título: limpeza de `name` (151-166): remover `\r\n\t`, colapsar espaços, duplicar aspas, remover invisíveis, `strip`.
- Descrição: `html.unescape`, remover tags, colapsar espaços, truncar 500 chars com `...`, sem quebras (167-186).
- Status: traduzir `{1:'Novo',2:'Em andamento (atribuído)',3:'Em andamento (planejado)',4:'Pendente',5:'Solucionado',6:'Fechado'}` (202-213).
- Datas: formatar `%d/%m/%Y %H:%M:%S` ou `%d/%m/%Y`; nulos/`'NULL'` → `""` (187-201).
- Defaults: `'Sem Categoria'`, `'Sem Entidade'`, `'Sem Requerente'`, `'Não Atribuído'`, `'Sem Grupo'` conforme script.

## API sobre o Banco
- Novo endpoint pode ler de `tickets_flat` (ou montar joins on-the-fly) e responder JSON idêntico ao endpoint atual que consulta direto o GLPI.
- Filtros:
  - `periodo=6m`: `WHERE tickets.date BETWEEN now()-interval '180 days' AND now()`.
  - Paginação: `LIMIT`/`OFFSET` com parâmetros `page`/`page_size`.
- Consistência: garantir que o shape do JSON e valores coincidem com a referência (CSV e script).

## Histórico e Auditoria
- `*_raw` (opcional): armazenar payloads brutos por coleta (para auditoria e reconstrução).
- Campos de auditoria nas tabelas: `source_fetched_at`, `updated_at`.
- Tabela `etl_runs`: registros de execuções, contagens, falhas, duração.

## Validação e Testes
- Golden dataset: comparar amostra e totais com `todos_tickets_atual.csv` (incluindo `ID=11162`).
- Testes de transformação: asserts para limpeza de `Título`/`Descrição`, formatação de datas e status.
- Testes de relacionamentos: seleção de `Requerente`/`Técnico`/`Grupo` por `type` correta.
- Teste de filtro `6m`: todos os `Data Criação` no intervalo `[now()-180 dias, now()]`.
- Teste de paginação: união de páginas reproduz conjunto completo.

## Performance
- Pré-materializar `tickets_flat` e atualizar após ETL para respostas rápidas.
- Índices nos campos de filtro e chaves de join.
- Page_size até 1.000; para datasets muito grandes, sugerir cursor API ou paginação eficiente.

## Segurança
- Não armazenar tokens do GLPI no banco; apenas dados operacionais.
- Sanitizar strings e evitar injeção (ORM ou queries parametrizadas).
- Controle de acesso ao banco (rede, usuários, roles).

## Opções de Banco
- Produção: PostgreSQL (recomendado) pela robustez, `UPSERT`, índices avançados e materialized views.
- Simplicidade/local: SQLite para protótipo; migrar para Postgres ao escalar.

## Fases de Implementação
1. Provisionar banco (Postgres) e definir acesso seguro.
2. Escrever DDL das tabelas básicas e índices; criar migrations.
3. Implementar ETL full + incremental com upsert e logs.
4. Criar view/tabela `tickets_flat` ou montar joins na API.
5. Adaptar endpoint para ler do banco em vez de chamar GLPI.
6. Escrever suíte de validação contra o CSV de referência e amostras conhecidas.
7. Monitorar execução e ajustar índices/materializações.

## Entregáveis
- Esquema SQL versionado (migrations).
- Serviço ETL com configuração de agendamento.
- Endpoint(s) de consulta ao banco replicando fielmente o JSON desejado.
- Scripts de validação e relatórios de consistência (CSV vs banco, amostra `ID=11162`).

Confirme se prefere PostgreSQL (recomendado) ou começar com SQLite. Após confirmar, inicio a implementação com migrations, ETL e a adaptação do endpoint para usar o banco.
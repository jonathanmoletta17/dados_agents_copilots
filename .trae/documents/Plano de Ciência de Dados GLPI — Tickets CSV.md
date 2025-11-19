# 1) Visão Geral do Dataset

## 1.1. Fonte e Carregamento
1. Arquivo: `scripts/dados/tickets_completos/todos_tickets_atual.csv` (separador `;`, encoding UTF-8).
2. Carregar via Interpretador de Código com `pandas.read_csv(..., sep=';', parse_dates=['Data Criação','Data Modificação'], dayfirst=True)`.

## 1.2. Colunas disponíveis
1. `ID` — numérico (inteiro)
2. `Título` — texto
3. `Descrição` — texto
4. `Status` — categórico
5. `Categoria` — categórico
6. `Entidade` — categórico
7. `Requerente` — texto (pessoa/solicitante)
8. `Técnico` — texto (atendente/resolvedor)
9. `Grupo` — categórico (ex.: "Sem Grupo", "N3")
10. `Data Criação` — data/hora
11. `Data Modificação` — data/hora

Para cada coluna, calcular no código:
- Tipo inferido: por `df.dtypes` + regra semântica.
- % de nulos: `df[col].isna().mean()`.
- % de valores "placeholder" (ex.: `Grupo == 'Sem Grupo'`).

## 1.3. Resumo do dataset
1. Linhas/colunas: colunas=11; linhas estimadas >10.8k (precisar com `len(df)`).
2. Período coberto: estimado de 2023-03-17 a 2025-11-05 (confirmar com `df[['Data Criação','Data Modificação']].min()/max()`).
3. Principais campos de análise:
   - Identificação: `ID`, `Título`, `Descrição`.
   - Status & categorização: `Status`, `Categoria`, `Grupo`.
   - Organização: `Entidade`.
   - Pessoas: `Requerente`, `Técnico`.
   - Datas: `Data Criação`, `Data Modificação`.
   - Derivados (a calcular): `TTR = Data Modificação - Data Criação` para tickets fechados/solucionados, flags de SLA se houver catálogo externo.

---

# 2) Mapa de Oportunidades de Análise

## A) Operação / Volume
1. Perguntas:
   - Volume por técnico, entidade, categoria, status, mês.
   - Top categorias/entidades com maior demanda.
2. Colunas: `Status`, `Categoria`, `Entidade`, `Técnico`, `Data Criação`.
3. Complexidade: simples–média (agrupamentos por contagem e resampling mensal).
4. Risco de qualidade: baixo–médio (valores "Sem Grupo", categorias genéricas).

## B) Tempo / SLA
1. Perguntas:
   - TTR médio/mediano por grupo/técnico/entidade/categoria.
   - Idade dos chamados em aberto (se existirem tickets não fechados).
   - Percentual fora de SLA (se regras forem definidas).
2. Colunas: `Data Criação`, `Data Modificação`, `Status`, `Categoria`, `Entidade`, `Técnico`, `Grupo`.
3. Complexidade: média–avançada (cálculo de TTR; integração de regras de SLA externas).
4. Risco: médio–alto (datas inconsistentes; modificação ≠ fechamento; ausência de coluna de solução explícita).

## C) Qualidade / Dados suspeitos
1. Perguntas:
   - TTR negativo; datas fora de ordem.
   - Campos críticos nulos ou placeholders (ex.: `Grupo == 'Sem Grupo'`).
   - Categorias "genéricas" ou não padronizadas.
2. Colunas: todas, com foco em `Data Criação`, `Data Modificação`, `Status`, `Categoria`, `Grupo`.
3. Complexidade: média.
4. Risco: médio.

## D) Tendências / Sazonalidade
1. Perguntas:
   - Evolução mensal de volume.
   - Picos por dia da semana/horário (se granularidade estiver disponível nas datas).
   - Comparações de períodos (YoY, MoM).
2. Colunas: `Data Criação`, `Status`, `Categoria`, `Entidade`, `Técnico`.
3. Complexidade: média.
4. Risco: baixo–médio (datas, mudanças de taxonomia).

## E) Cruzamentos avançados
1. Perguntas:
   - Técnico × Entidade; Entidade × Categoria; Categoria × Tipo (se houver tipo); Técnico × SLA.
2. Colunas: `Técnico`, `Entidade`, `Categoria`, `Grupo`, datas para métricas de tempo.
3. Complexidade: média–avançada.
4. Risco: médio (cardinalidade alta, sparsidade).

---

# 3) Catálogo de Prompts Sugeridos

## Prompts de Volume / Distribuição
- P1 — Objetivo: volume mensal por entidade.
  - Exemplos: "Qual o volume por entidade por mês?"; "Quais entidades lideram em chamados no último trimestre?".
  - Resposta: tabela resumida + gráfico.
  - Colunas/filtros: `Entidade`, `Data Criação`, `Status`; filtro período.
  - Amostragem: não; agrega por mês.

- P2 — Objetivo: top categorias por período.
  - Exemplos: "Top 10 categorias entre abril–junho"; "Distribuição por categoria este ano".
  - Resposta: tabela + gráfico de barras.
  - Colunas/filtros: `Categoria`, `Data Criação`.
  - Amostragem: não; agrega.

- P3 — Objetivo: volume por técnico.
  - Exemplos: "Quantos chamados cada técnico recebeu no mês passado?"; "Ranking de técnicos por volume".
  - Resposta: tabela + gráfico.
  - Colunas/filtros: `Técnico`, `Data Criação`, `Status`.
  - Amostragem: não; agrega.

## Prompts de Tempo / SLA
- P4 — Objetivo: TTR por categoria.
  - Exemplos: "Média e mediana de TTR por categoria"; "Distribuição de TTR (boxplot) por categoria".
  - Resposta: resumo executivo + tabela + gráfico.
  - Colunas/filtros: `Data Criação`, `Data Modificação`, `Categoria`, `Status`.
  - Amostragem: possível por amostra estratificada se volume muito alto.

- P5 — Objetivo: idade de chamados em aberto.
  - Exemplos: "Idade média dos abertos por entidade"; "Quais grupos têm mais chamados antigos?".
  - Resposta: tabela + gráfico.
  - Colunas/filtros: `Data Criação`, `Status`, `Entidade`, `Grupo`.
  - Amostragem: não; foca em subset `Status` ≠ fechado/solucionado.

- P6 — Objetivo: SLA por técnico/grupo (se regras disponíveis).
  - Exemplos: "% fora do SLA por técnico"; "SLA cumprido por grupo no último mês".
  - Resposta: resumo executivo + tabela.
  - Colunas/filtros: `Data Criação`, `Data Modificação`, `Técnico`, `Grupo`, regras SLA externas.
  - Amostragem: agrega por técnico/grupo.

## Prompts de Cruzamentos
- P7 — Objetivo: matriz técnico × entidade (volume).
  - Exemplos: "Cruzamento de técnico por entidade"; "Quem atende qual entidade?".
  - Resposta: CSV anexado + heatmap.
  - Colunas/filtros: `Técnico`, `Entidade`, `Status`.
  - Amostragem: não; pivot com agregação.

- P8 — Objetivo: categoria × entidade.
  - Exemplos: "Categorias mais frequentes por entidade"; "Mapa de demanda por categoria".
  - Resposta: tabela + gráfico.
  - Colunas/filtros: `Categoria`, `Entidade`, `Data Criação`.
  - Amostragem: agrega.

## Prompts de Qualidade de Dados
- P9 — Objetivo: checagens de datas.
  - Exemplos: "Há TTR negativo?"; "Tickets com Data Modificação < Data Criação".
  - Resposta: tabela de casos suspeitos + CSV.
  - Colunas/filtros: `Data Criação`, `Data Modificação`, `Status`.
  - Amostragem: não; regra determinística.

- P10 — Objetivo: campos nulos/placeholder.
  - Exemplos: "% de nulos por coluna"; "Tickets com 'Sem Grupo'".
  - Resposta: resumo executivo + tabela + CSV.
  - Colunas/filtros: todas; foco em `Grupo`, `Categoria`, `Técnico`.
  - Amostragem: não.

## Prompts de Exploração Livre (EDA guiada)
- P11 — Objetivo: panorama geral por período.
  - Exemplos: "Resumo operacional Q3 2025"; "Visão geral do último mês".
  - Resposta: resumo executivo + gráficos padrão.
  - Colunas/filtros: principais colunas + `Data Criação`.
  - Amostragem: agrega e limita top-N.

- P12 — Objetivo: drill-down de uma entidade.
  - Exemplos: "Explorar CASA CIVIL em 2025"; "Detalhar categorias e técnicos da GG".
  - Resposta: tabela + CSV anexado.
  - Colunas/filtros: `Entidade` fixo, demais dimensões.
  - Amostragem: agrega + exporta detalhes em CSV.

---

# 4) Plano de Agent Flows e Arquitetura

## 4.1. Cenários atendidos apenas com prompts + Interpretador de Código
1. Volume por dimensões (técnico, entidade, categoria, status, mês).
2. TTR por grupo/categoria/técnico.
3. Checagens de qualidade (datas, nulos, placeholders).
4. Tendências mensais, comparações básicas.

## 4.2. Cenários para Agent Flows dedicados (SharePoint → Prompt)
1. Consultas que sempre usam a base completa (relatórios mensais/trimestrais).
2. Geração de relatórios padrão (PDF/Excel) para gestão.
3. Processos que geram e salvam arquivos (CSV/Excel) em SharePoint para distribuição.

## 4.3. Flows sugeridos
- Flow_RelatorioMensal_GLPI
  - Entradas: período, entidade(s) filtro, top-N categorias.
  - Passos:
    1) Buscar arquivo em SharePoint (path parametrizado).
    2) Pré-filtrar por período no código.
    3) Rodar prompt P1/P2/P11 com interpretador.
    4) Retornar texto + anexar CSV/Excel e gráficos.

- Flow_SLA_Por_Grupo
  - Entradas: período, grupo(s), regras SLA (tempo alvo).
  - Passos:
    1) Buscar arquivo.
    2) Calcular TTR e comparar com SLA.
    3) Rodar prompt P4/P6.
    4) Retornar resumo + CSV de fora do SLA.

- Flow_QualidadeDados_GLPI
  - Entradas: período opcional.
  - Passos:
    1) Buscar arquivo.
    2) Executar checagens P9/P10.
    3) Gerar relatório de anomalias.
    4) Retornar texto + anexos CSV.

- Flow_Tendencias_Semanais
  - Entradas: período, entidade.
  - Passos:
    1) Buscar arquivo.
    2) Derivar dia da semana/hora a partir de `Data Criação`.
    3) Rodar análise de sazonalidade (P11).
    4) Retornar gráficos.

- Flow_Cruzamentos_Tecnico_Entidade
  - Entradas: período, técnico(s), entidade(s).
  - Passos:
    1) Buscar arquivo.
    2) Pivot `Técnico` × `Entidade`.
    3) Rodar prompt P7.
    4) Retornar heatmap + CSV.

---

# 5) Tratamento de Limitações (Dados e Token)

## 5.1. Qualidade de dados
1. Problemas prováveis:
   - `Data Modificação` usada como proxy de fechamento (pode incluir edições sem resolução).
   - TTR negativo/datas incoerentes.
   - Campos nulos/placeholder (ex.: `Sem Grupo`).
   - Taxonomia de `Categoria` heterogênea.
2. Impacto:
   - TTR/SLA distorcidos; contagens por grupo/categoria enviesadas.
3. Tratamentos no código:
   - Definir conjunto de `Status` que caracterizam resolução (ex.: Fechado/Solucionado).
   - Filtrar tickets com `Data Modificação >= Data Criação` para TTR.
   - Marcar/segmentar placeholders em relatórios.
   - Normalizar categorias (mapa de equivalência, se fornecido).

## 5.2. Limites de token/tempo
1. Tamanho: >10k linhas; risco moderado.
2. Estratégias:
   - Filtrar por período (parâmetros nos prompts/flows).
   - Agregar antes de responder; limitar top-N.
   - Exportar detalhes em CSV/Excel em vez de imprimir no texto.
   - Amostragem estratificada para gráficos de distribuição pesada.

---

# 6) Próximos Passos Recomendados

1. Implementar o perfil inicial automatizado: inferência de tipos, % nulos, período, e derivar `TTR`.
2. Construir os prompts P1–P12 no Copilot Studio com parâmetros padrão de período e filtros.
3. Configurar Flows prioritários: `Flow_RelatorioMensal_GLPI`, `Flow_SLA_Por_Grupo`, `Flow_QualidadeDados_GLPI`.
4. Validar qualidade de dados e ajustar regras de SLA/normalização de categorias com o negócio.
5. Publicar coleção de relatórios e CSVs em SharePoint para consumo gerencial.

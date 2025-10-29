# [METRICAS] Scripts de Análise de Dados - GLPI

Este conjunto de scripts permite analisar e visualizar dados dos CSVs gerados pela extração da API do GLPI, fornecendo estatísticas detalhadas, gráficos interativos e comparações entre períodos.

## [ARQUIVO] Scripts Disponíveis

### 1. `analisar_dados_csv.py` - Análise Estatística Básica
**Objetivo**: Gera relatórios estatísticos detalhados dos dados dos tickets.

**Funcionalidades**:
- Contabiliza valores únicos para cada campo padronizado
- Calcula percentuais e frequências
- Análise temporal (tickets por dia da semana, período dos dados)
- Exportação para JSON

**Uso**:
```bash
# Análise básica
python analisar_dados_csv.py "caminho/para/arquivo.csv"

# Salvar relatório em JSON
python analisar_dados_csv.py "caminho/para/arquivo.csv" --salvar-json
```

**Campos Analisados**:
- Status dos tickets
- Entidades
- Grupos técnicos
- Categorias
- Localizações
- Técnicos atribuídos

---

### 2. `analisar_dados_graficos.py` - Análise com Visualizações
**Objetivo**: Cria dashboards interativos com gráficos e visualizações.

**Funcionalidades**:
- Gráficos de pizza e barras para cada campo
- Análises temporais com gráficos de linha
- Matriz de correlação entre campos
- Dashboard HTML interativo
- Exportação de gráficos em PNG

**Uso**:
```bash
# Gerar dashboard HTML
python analisar_dados_graficos.py "caminho/para/arquivo.csv" --html

# Salvar gráficos em PNG
python analisar_dados_graficos.py "caminho/para/arquivo.csv" --png

# Ambos
python analisar_dados_graficos.py "caminho/para/arquivo.csv" --html --png
```

**Dependências**:
```bash
pip install pandas matplotlib seaborn plotly kaleido
```

---

### 3. `comparar_periodos.py` - Comparação entre Períodos
**Objetivo**: Compara dados entre diferentes períodos (meses, anos, etc.).

**Funcionalidades**:
- Comparação de múltiplos arquivos CSV
- Análise de evolução temporal
- Gráficos comparativos
- Relatórios de tendências
- Dashboard comparativo em HTML

**Uso**:
```bash
# Comparar todos os CSVs de uma pasta
python comparar_periodos.py --pasta "caminho/para/pasta/dados"

# Comparar arquivos específicos
python comparar_periodos.py --arquivos arquivo1.csv arquivo2.csv arquivo3.csv

# Gerar relatório HTML
python comparar_periodos.py --pasta "caminho/para/pasta" --html
```

---

## [METRICAS] Campos Padronizados Analisados

Os scripts analisam automaticamente os seguintes campos dos CSVs:

| Campo | Descrição | Exemplos de Valores |
|-------|-----------|-------------------|
| **Status** | Status atual do ticket | "Solucionado", "Fechado", "Em andamento" |
| **Entidade** | Órgão/entidade solicitante | "CASA CIVIL", "SECOM", "GG" |
| **Grupo_tecnico** | Nível de suporte técnico | "N1", "N2", "N3", "Sem Grupo" |
| **Categoria** | Categoria do atendimento | "CONFIGURAÇÃO DE SOFTWARE", "MANUTENÇÃO" |
| **Localizacao** | Local físico do atendimento | "1° Andar", "2° Andar", "Sem Localização" |
| **Tecnico_atribuido** | Técnico responsável | Nome do técnico ou "Não Atribuído" |

## [GRAFICO] Exemplos de Saídas

### Análise Básica (Terminal)
```
[METRICAS] RELATÓRIO COMPLETO DE ANÁLISE DE DADOS
================================================================================

[ARQUIVO] Arquivo: tickets_api_glpi_ultimo_mes_20251022_144314.csv
[DATA] Data da análise: 22/10/2025 14:53:01
[METRICAS] Total de tickets: 372
[LISTA] Colunas disponíveis: 12

[BUSCA] STATUS DOS TICKETS
--------------------------------------------------
Total de registros: 372
Valores únicos: 4

[GRAFICO] Top 10 mais frequentes:
   1. Solucionado                    |  267 tickets ( 71.8%)
   2. Fechado                        |   89 tickets ( 23.9%)
   3. Em andamento (atribuído)       |   15 tickets (  4.0%)
   4. Em andamento (planejado)       |    1 tickets (  0.3%)
```

### Dashboard HTML
- Gráficos interativos de pizza e barras
- Análises temporais com gráficos de linha
- Matriz de correlação
- Interface responsiva e moderna

### Comparação entre Períodos
- Gráficos comparativos lado a lado
- Evolução temporal de indicadores
- Relatórios de tendências

## [INICIO] Exemplos Práticos

### Análise Rápida de um Arquivo
```bash
python analisar_dados_csv.py "C:\dados\tickets_outubro_2025.csv"
```

### Dashboard Completo com Gráficos
```bash
python analisar_dados_graficos.py "C:\dados\tickets_outubro_2025.csv" --html
```

### Comparar Últimos 3 Meses
```bash
python comparar_periodos.py --pasta "C:\dados\tickets_mensais" --html
```

## [LISTA] Estrutura de Arquivos Gerados

```
scripts/python/
[EMOJI] analisar_dados_csv.py
[EMOJI] analisar_dados_graficos.py
[EMOJI] comparar_periodos.py
[EMOJI] dashboard_glpi_YYYYMMDD_HHMMSS.html    # Dashboard interativo
[EMOJI] relatorio_analise_YYYYMMDD_HHMMSS.json # Dados em JSON
[EMOJI] comparacao_periodos_YYYYMMDD_HHMMSS.html # Comparação HTML
[EMOJI] graficos_glpi_YYYYMMDD_HHMMSS/          # Pasta com PNGs
    [EMOJI] grafico_01.png
    [EMOJI] grafico_02.png
    [EMOJI] ...
```

## [CONFIG] Instalação de Dependências

```bash
# Dependências básicas
pip install pandas

# Para gráficos (script avançado)
pip install matplotlib seaborn plotly

# Para salvar PNG (opcional)
pip install kaleido
```

## [DICA] Dicas de Uso

1. **Performance**: Para arquivos grandes (>10MB), use primeiro a análise básica
2. **Visualização**: O dashboard HTML é ideal para apresentações
3. **Comparação**: Use o script de comparação para análises mensais/anuais
4. **Automação**: Os scripts podem ser integrados em rotinas automatizadas

## [FOCO] Casos de Uso Comuns

- **Relatórios Mensais**: Análise de produtividade e indicadores
- **Dashboards Gerenciais**: Visualizações para tomada de decisão
- **Análise de Tendências**: Comparação entre períodos
- **Controle de Qualidade**: Validação de dados extraídos
- **Apresentações**: Gráficos para reuniões e relatórios

---

**Desenvolvido para**: Sistema de Análise de Dados GLPI  
**Data**: Outubro 2025  
**Versão**: 1.0
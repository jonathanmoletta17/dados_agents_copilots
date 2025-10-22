# 🎫 Sistema de Extração e Análise de Dados GLPI

Sistema completo para extração, análise e visualização de dados de tickets do sistema GLPI, desenvolvido para o Governo do Estado do Rio Grande do Sul.

## 🔒 CONFIGURAÇÃO DE SEGURANÇA (IMPORTANTE!)

**ANTES DE USAR O SISTEMA:**

1. **Configure suas credenciais:**
   ```bash
   cd scripts/python
   cp config_exemplo.py config.py
   # Edite config.py com seus tokens reais da API GLPI
   ```

2. **Nunca commite credenciais:**
   - O arquivo `config.py` está no `.gitignore`
   - Use apenas `config_exemplo.py` como referência
   - Mantenha seus tokens seguros e privados

3. **Dados sensíveis protegidos:**
   - Todos os CSVs com dados reais estão no `.gitignore`
   - Relatórios e métricas geradas não sobem para o Git
   - Apenas código-fonte e documentação são versionados

## 📋 Visão Geral

Este projeto oferece uma solução completa para:
- **Extração automatizada** de dados dos últimos 3 meses via API do GLPI
- **Análise estatística** automática com métricas e indicadores
- **Relatórios completos** em formato texto e JSON
- **Processo orquestrado** com execução única e automática
- **Visualizações interativas** com dashboards e gráficos (scripts legados)
- **Comparações temporais** entre diferentes períodos (scripts legados)

## 🚀 PROCESSO AUTOMATIZADO (RECOMENDADO)

### ⚡ Execução Única e Completa
**Script Principal**: `executar_processo_completo.py`

Execute todo o processo com um único comando:

```bash
python executar_processo_completo.py
```

**O que acontece automaticamente:**
1. 📥 **Extração**: Coleta dados dos últimos 3 meses da API GLPI
2. 📊 **Análise**: Processa dados e calcula métricas completas
3. 📝 **Relatórios**: Gera relatórios em texto e JSON
4. 📋 **Log**: Registra todo o processo de execução

**Arquivos gerados:**
- `tickets_automatico_3meses_[timestamp].csv` - Dados extraídos
- `relatorio_analise_tickets_[timestamp].txt` - Relatório completo
- `metricas_tickets_[timestamp].json` - Métricas em JSON
- `log_execucao_completa_[timestamp].txt` - Log da execução

### 🔧 Configuração do Período
Para alterar o período de extração, edite o arquivo `extrair_dados_automatico.py`:

```python
# Linha 25 - Altere o número de dias
self.PERIODO_DIAS = 90  # 3 meses = 90 dias
```

### 📊 Métricas Calculadas Automaticamente
- Taxa de resolução de tickets
- Distribuição por status, entidade, categoria
- Análise temporal (mês, dia da semana, hora)
- Top técnicos e grupos mais produtivos
- Palavras-chave mais frequentes
- Análise de performance e produtividade

## 🏗️ Estrutura do Projeto

```
bd_cau/
├── scripts/
│   ├── dados/                        # Dados extraídos (organizados automaticamente)
│   │   ├── tickets_automatico/       # 🆕 Dados do processo automatizado
│   │   ├── relatorios_automatico/    # 🆕 Relatórios gerados automaticamente
│   │   ├── logs_execucao/           # 🆕 Logs de execução
│   │   ├── tickets_6_meses/         # Dados legados
│   │   ├── tickets_data_personalizada/
│   │   ├── tickets_mensais/
│   │   └── tickets_ultimo_mes/
│   └── python/                       # Scripts Python
│       ├── executar_processo_completo.py      # 🆕 ⭐ SCRIPT PRINCIPAL
│       ├── extrair_dados_automatico.py        # 🆕 Extração automatizada
│       ├── analisar_dados_automatico.py       # 🆕 Análise automatizada
│       ├── extrair_dados_api_glpi_com_filtro_data.py  # Script legado
│       ├── analisar_dados_csv.py              # Análise estatística legada
│       ├── analisar_dados_graficos.py         # Dashboards e gráficos
│       ├── comparar_periodos.py               # Comparação temporal
│       ├── README_API_GLPI.md                 # Doc. extração
│       └── README_ANALISE_DADOS.md            # Doc. análise
└── README.md                         # Este arquivo
```

---

## 📚 SCRIPTS LEGADOS (Uso Avançado)

### 1. 📡 Extração de Dados Manual (API GLPI)
**Script**: `extrair_dados_api_glpi_com_filtro_data.py`

- ✅ Extração via API REST do GLPI
- ✅ Filtros por período (data de abertura/atualização)
- ✅ Sistema de cache para performance
- ✅ Limpeza e formatação automática
- ✅ Múltiplos formatos de saída

**Uso**:
```bash
# Último mês
python extrair_dados_api_glpi_com_filtro_data.py --periodo ultimo_mes

# Período personalizado
python extrair_dados_api_glpi_com_filtro_data.py --data-inicio 2025-10-01 --data-fim 2025-10-31

# Últimos 6 meses
python extrair_dados_api_glpi_com_filtro_data.py --periodo 6_meses
```

### 2. 📊 Análise Estatística
**Script**: `analisar_dados_csv.py`

- ✅ Contabilização automática de campos padronizados
- ✅ Cálculo de percentuais e frequências
- ✅ Análise temporal (dias da semana, períodos)
- ✅ Exportação para JSON

**Campos Analisados**:
- Status dos tickets
- Entidades solicitantes
- Grupos técnicos
- Categorias de atendimento
- Localizações
- Técnicos atribuídos

### 3. 📈 Dashboards e Visualizações
**Script**: `analisar_dados_graficos.py`

- ✅ Gráficos interativos (pizza, barras, linha)
- ✅ Dashboard HTML responsivo
- ✅ Análises temporais avançadas
- ✅ Matriz de correlação
- ✅ Exportação PNG para apresentações

### 4. 🔄 Comparação entre Períodos
**Script**: `comparar_periodos.py`

- ✅ Comparação automática de múltiplos CSVs
- ✅ Análise de evolução temporal
- ✅ Gráficos comparativos
- ✅ Relatórios de tendências



## 🎯 Casos de Uso

### 📅 Relatórios Mensais
```bash
# 1. Extrair dados do mês
python extrair_dados_api_glpi_com_filtro_data.py --periodo ultimo_mes

# 2. Gerar dashboard
python analisar_dados_graficos.py "dados/tickets_ultimo_mes/arquivo.csv" --html

# 3. Análise estatística
python analisar_dados_csv.py "dados/tickets_ultimo_mes/arquivo.csv" --salvar-json
```

### 📊 Análise Comparativa Trimestral
```bash
# 1. Comparar últimos 3 meses
python comparar_periodos.py --pasta "dados/tickets_mensais" --html
```

### 🎨 Apresentações Executivas
```bash
# Dashboard completo com gráficos PNG
python analisar_dados_graficos.py "arquivo.csv" --html --png
```

## 📦 Dependências

### Python
```bash
pip install pandas requests plotly matplotlib seaborn kaleido
```

### Sistema
- Python 3.7+
- Acesso à API do GLPI

## ⚙️ Configuração

### 1. API GLPI
Configure as credenciais da API no script principal:
```python
# Configurações da API (editar no script)
GLPI_URL = "https://seu-glpi.com/apirest.php"
APP_TOKEN = "seu_app_token"
USER_TOKEN = "seu_user_token"
```



## 📈 Indicadores Extraídos

### Principais Métricas
- **Volume de Tickets**: Total por período
- **Status**: Distribuição (Solucionado, Fechado, Em andamento)
- **Entidades**: Tickets por órgão/secretaria
- **Performance**: Tickets por técnico e grupo
- **Categorias**: Tipos de atendimento mais frequentes
- **Temporal**: Padrões por dia da semana, hora, mês

### Análises Avançadas
- **Tendências**: Evolução temporal de indicadores
- **Correlações**: Relacionamentos entre campos
- **Produtividade**: Análise por técnico e grupo
- **Sazonalidade**: Padrões temporais de demanda

## 🔧 Manutenção

### Estrutura de Dados
Os CSVs gerados seguem o padrão:
```
ID, Titulo, Entidade, Status, Ultima_atualizacao, Data_abertura, 
Requerente, Tecnico_atribuido, Grupo_tecnico, Categoria, Localizacao, Descricao
```

### Organização de Arquivos
- **tickets_ultimo_mes/**: Dados do mês atual
- **tickets_mensais/**: Histórico mensal
- **tickets_6_meses/**: Dados semestrais
- **tickets_data_personalizada/**: Extrações específicas

## 📞 Suporte

Para dúvidas ou problemas:
1. Consulte a documentação específica em cada pasta
2. Verifique os logs de execução dos scripts
3. Valide as configurações de API e banco

---

**Desenvolvido para**: Governo do Estado do Rio Grande do Sul  
**Sistema**: GLPI - Gestão de Tickets  
**Versão**: 1.0 - Produção  
**Data**: Outubro 2025
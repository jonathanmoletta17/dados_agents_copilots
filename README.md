# [METRICAS] Sistema de Extração e Análise de Dados GLPI

Sistema completo para extração, análise e visualização de dados de tickets do GLPI via API REST.

## [INICIO] Início Rápido

### 1. Configuração Inicial
```bash
# Navegar para o diretório dos scripts
cd scripts/python

# Instalar dependências
pip install -r requirements_api.txt

# Configurar credenciais da API GLPI
cp config_exemplo.py config.py
# Editar config.py com suas credenciais reais
```

### 2. Configurar Credenciais (OBRIGATÓRIO)
Edite o arquivo `scripts/python/config.py` com suas credenciais:

```python
# Configurações da API GLPI
GLPI_URL = "http://cau.ppiratini.intra.rs.gov.br/glpi/apirest.php"
APP_TOKEN = "seu_app_token_real"
USER_TOKEN = "seu_user_token_real"

# Configurações opcionais
TIMEOUT = 30
CACHE_ENABLED = True
DEBUG = False
```

### 3. Executar o Sistema
```bash
# Extração interativa (últimos 6 meses)
python extrair_dados_api_glpi_com_filtro_data.py

# Análise de métricas
python extrair_metricas_tickets.py

# API de métricas (acesse http://localhost:5000)
python api_metricas.py
```

## [ARQUIVO] Estrutura do Projeto

```
bd_cau/
[EMOJI] [EMOJI] README.md                                     # Este arquivo
[EMOJI] [EMOJI] CONFIGURACAO_INICIAL.md                       # (será removido)
[EMOJI] [EMOJI] .gitignore                                    # Arquivos protegidos
[EMOJI] [EMOJI] scripts/
    [EMOJI] [EMOJI] dados/                                    # Dados extraídos (protegido)
    [EMOJI]   [EMOJI] metricas_csv/                           # Métricas em CSV
    [EMOJI]   [EMOJI] relatorios_metricas/                    # Relatórios gerados
    [EMOJI]   [EMOJI] tickets_6_meses/                        # Dados de tickets
    [EMOJI] [EMOJI] python/
        [EMOJI] [EMOJI] extrair_dados_api_glpi_com_filtro_data.py  # Script principal
        [EMOJI] [EMOJI] extrair_metricas_tickets.py               # Análise de métricas
        [EMOJI] [EMOJI] api_metricas.py                           # API REST
        [EMOJI] [CONFIG] config_exemplo.py                         # Template de config
        [EMOJI] [LISTA] requirements_api.txt                      # Dependências
```

## [CONFIG] Scripts Principais

### [METRICAS] `extrair_dados_api_glpi_com_filtro_data.py`
**Script principal para extração de dados da API GLPI**

**Recursos:**
- [OK] Extração por período (dias, semanas, meses)
- [OK] Cache inteligente de usuários (incluindo excluídos)
- [OK] Correção automática para usuários não encontrados
- [OK] Exportação para CSV
- [OK] Suporte a argumentos de linha de comando

**Uso:**
```bash
# Modo interativo
python extrair_dados_api_glpi_com_filtro_data.py

# Com argumentos específicos
python extrair_dados_api_glpi_com_filtro_data.py --periodo 30 --formato csv

# Ver todas as opções
python extrair_dados_api_glpi_com_filtro_data.py --help
```

**Opções de período:**
- `1` - Últimos 30 dias
- `2` - Últimos 3 meses  
- `3` - Últimos 6 meses (padrão)
- `4` - Último ano
- `5` - Período personalizado

### [GRAFICO] `extrair_metricas_tickets.py`
**Análise completa de métricas e KPIs**

**Métricas geradas:**
- [METRICAS] Tickets por categoria
- [EMOJI] Tickets por técnico
- [EMOJI] Tickets por entidade
- [EMOJI] Tickets por localização
- [TEMPO] Tempos de resolução
- [GRAFICO] Tendências temporais

**Arquivos gerados:**
- `metricas_categorias.csv` - Análise por categoria
- `metricas_tecnicos.csv` - Performance de técnicos
- `metricas_entidades.csv` - Distribuição por entidade
- `metricas_localizacoes.csv` - Análise geográfica
- `metricas_tempos_resolucao.csv` - KPIs de tempo

### [EMOJI] `api_metricas.py`
**API REST para consulta de métricas em tempo real**

**Endpoints disponíveis:**
- `GET /` - Página inicial
- `GET /status` - Status da API
- `GET /metricas` - Métricas gerais
- `GET /categorias` - Top categorias
- `POST /analisar` - Análise completa

**Iniciar servidor:**
```bash
python api_metricas.py
# Acesse: http://localhost:5000
```

## [LISTA] Funcionalidades

### [OK] Extração via API
- Dados atualizados em tempo real do GLPI
- Filtros por período flexíveis
- Cache inteligente para performance

### [OK] Correção de Usuários Excluídos
O sistema automaticamente:
- Detecta usuários excluídos da API
- Mantém cache local de usuários
- Adiciona sufixo "(não encontrado na API)" para usuários excluídos
- Garante relatórios 100% confiáveis

### [OK] Análise de Métricas
- Status, entidades, categorias
- Produtividade de técnicos
- Padrões temporais
- KPIs de performance

### [OK] Múltiplos Formatos
- CSV para planilhas
- JSON para integração
- Relatórios em texto
- API REST para consultas

### [OK] Cache Inteligente
- Cache automático de usuários, entidades, categorias
- Reduz chamadas à API
- Melhora performance significativamente
- Atualização automática quando necessário

### [OK] Segurança
- Credenciais protegidas em `config.py`
- Dados sensíveis no `.gitignore`
- Tokens seguros para ambiente controlado

## [GRAFICO] Exemplos de Uso

### Extração Básica
```bash
cd scripts/python
# Extrair últimos 6 meses (padrão)
python extrair_dados_api_glpi_com_filtro_data.py
# Escolha opção 3 quando solicitado
```

### Análise Completa
```bash
# 1. Extrair dados
python extrair_dados_api_glpi_com_filtro_data.py

# 2. Gerar métricas
python extrair_metricas_tickets.py

# 3. Iniciar API para visualização
python api_metricas.py
```

### Automação
```bash
# Script automatizado para relatório mensal
python extrair_dados_api_glpi_com_filtro_data.py --periodo 30 --formato csv
python extrair_metricas_tickets.py
```

## [EMOJI] Solução de Problemas

### Erro de Configuração
| Erro | Solução |
|------|---------|
| `config.py não encontrado` | Copie `config_exemplo.py` para `config.py` |
| `Erro de autenticação` | Verifique tokens no GLPI |
| `Módulo não encontrado` | Execute `pip install -r requirements_api.txt` |

### Erro de Conexão
```bash
# Verificar conectividade
python -c "import requests; print(requests.get('http://cau.ppiratini.intra.rs.gov.br/glpi/apirest.php/initSession').status_code)"
```

### Usuários Não Encontrados
- [OK] **Resolvido automaticamente** - O sistema corrige automaticamente
- Usuários excluídos aparecem com sufixo "(não encontrado na API)"
- Cache manual para usuários problemáticos (1439, 1392, 1386)

### Performance Lenta
- Verifique se o cache está habilitado
- Reduza o período de extração
- Use filtros mais específicos

## [METRICAS] Arquivos de Saída

### Dados Extraídos
- `tickets_api_glpi_ultimos_X_meses_YYYYMMDD_HHMMSS.csv`
- Formato CSV com campos padronizados
- ID, Título, Entidade, Status, Datas, Técnico, Categoria, etc.

### Métricas
Localizados em `scripts/dados/metricas_csv/`:
- `metricas_categorias.csv`
- `metricas_tecnicos.csv`
- `metricas_entidades.csv`
- `metricas_localizacoes.csv`
- `metricas_tempos_resolucao.csv`

### Relatórios
Localizados em `scripts/dados/relatorios_metricas/`:
- Relatórios detalhados em formato texto
- Análises temporais
- Gráficos e visualizações

## [FOCO] Status do Projeto

- [OK] **Extração de dados:** Funcionando 100%
- [OK] **Correção de usuários excluídos:** Implementado
- [OK] **Análise de métricas:** Funcionando
- [OK] **API REST:** Funcionando
- [OK] **Cache inteligente:** Implementado
- [OK] **Documentação:** Consolidada

## [EMOJI] Segurança e Boas Práticas

- **Credenciais protegidas**: `config.py` não é versionado
- **Dados sensíveis**: CSVs e relatórios no `.gitignore`
- **Tokens seguros**: Use apenas em ambiente controlado
- [ERRO] **NUNCA** commite credenciais ou dados reais

## [EMOJI] Suporte

Para dúvidas ou problemas:
1. Verifique este README
2. Execute scripts com `--help` para ver opções
3. Verifique logs de erro para diagnóstico
4. Valide configurações da API GLPI

---

**Sistema GLPI - Governo do Estado do Rio Grande do Sul**  
**Última atualização:** 23/10/2025  
**Status:** [OK] Projeto funcional e pronto para produção
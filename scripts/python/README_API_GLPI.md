# 📡 Extração de Dados da API do GLPI

Este documento descreve os scripts desenvolvidos para extrair dados de tickets diretamente da API do GLPI, garantindo dados atualizados e completos.

## 📋 Visão Geral

Os scripts extraem dados de tickets do sistema GLPI através da API REST, aplicando as mesmas formatações e limpezas utilizadas nos dados do banco local, garantindo consistência e qualidade dos dados.

## 🔧 Scripts Disponíveis

### 1. `extrair_dados_api_glpi.py` (Versão Original)
Script inicial para extração de dados da API do GLPI.

**Características:**
- Extração completa de tickets
- Busca individual de dados relacionados
- Formatação e limpeza de dados
- Mais lento devido às múltiplas chamadas à API

### 2. `extrair_dados_api_glpi_otimizado.py` (Versão Recomendada)
Versão otimizada com cache para melhor performance.

**Características:**
- ⚡ **Performance otimizada** (3-4 segundos vs vários minutos)
- 🗄️ **Sistema de cache** para dados relacionados
- 📊 **Processamento em lote** de relacionamentos
- 🧹 **Mesma qualidade de limpeza** de dados

### 3. `extrair_dados_api_glpi_com_filtro_data.py` (Mais Recente) ⭐
Versão com filtro de data para extrair tickets de períodos específicos.

**Características:**
- 📅 **Filtro por período** (data de abertura ou última atualização)
- ⚡ **Performance otimizada** com sistema de cache
- 🎯 **Extração direcionada** para análises específicas
- 📊 **Ideal para relatórios mensais/trimestrais**

## 🚀 Como Usar

### Pré-requisitos
```bash
pip install requests
```

### Execução Básica (Todos os Tickets)
```bash
python extrair_dados_api_glpi_otimizado.py
```

### Execução com Filtro de Data ⭐
```bash
# Para os últimos 6 meses (salva em dados/tickets_6_meses/)
python extrair_dados_api_glpi_com_filtro_data.py --periodo ultimos_6_meses

# Para o último mês (salva em dados/tickets_ultimo_mes/)
python extrair_dados_api_glpi_com_filtro_data.py --periodo ultimo_mes

# Para os últimos 3 meses (salva em dados/tickets_mensais/)
python extrair_dados_api_glpi_com_filtro_data.py --periodo ultimos_3_meses

# Para o último ano (salva em dados/tickets_mensais/)
python extrair_dados_api_glpi_com_filtro_data.py --periodo ultimo_ano

# Para o ano atual (salva em dados/tickets_mensais/)
python extrair_dados_api_glpi_com_filtro_data.py --periodo ano_atual

# Para o ano passado (salva em dados/tickets_mensais/)
python extrair_dados_api_glpi_com_filtro_data.py --periodo ano_passado

# Para um período específico (salva em dados/tickets_data_personalizada/)
python extrair_dados_api_glpi_com_filtro_data.py --data-inicial "01/09/2025" --data-final "30/09/2025"
```

> **💡 Organização Automática:** O script automaticamente cria e organiza os arquivos nas pastas corretas baseado no tipo de execução, facilitando a gestão e localização dos dados extraídos.

### Configuração
Os scripts já estão configurados com as credenciais da API:
- **API URL:** `http://cau.ppiratini.intra.rs.gov.br/glpi/apirest.php`
- **App Token:** Configurado no script
- **User Token:** Configurado no script

### Execução (Versões Anteriores)
```bash
# Versão otimizada (recomendada)
python extrair_dados_api_glpi_otimizado.py

# Versão original
python extrair_dados_api_glpi.py
```

## 📊 Dados Extraídos

### Colunas do CSV Gerado
| Coluna | Descrição | Exemplo |
|--------|-----------|---------|
| `ID` | Identificador único do ticket | 12345 |
| `Titulo` | Título/assunto do ticket | "Problema com impressora" |
| `Entidade` | Entidade/órgão responsável | "CASA CIVIL" |
| `Status` | Status atual do ticket | "Fechado", "Em andamento" |
| `Ultima_atualizacao` | Data da última modificação | "21/10/2025 20:57:03" |
| `Data_abertura` | Data de criação do ticket | "15/10/2025 14:30:00" |
| `Requerente` | Nome do usuário solicitante | "João Silva" |
| `Tecnico_atribuido` | Técnico responsável | "Maria Santos" |
| `Grupo_tecnico` | Grupo técnico responsável | "Suporte TI" |
| `Categoria` | Categoria do ticket | "HARDWARE" |
| `Localizacao` | Localização física | "Prédio A - Sala 101" |
| `Descricao` | Descrição limpa do problema | "Impressora não funciona..." |

### Formatação e Limpeza Aplicada

#### 🧹 Limpeza de Texto
- **Remoção de HTML:** Tags HTML são removidas completamente
- **Caracteres especiais:** Normalizados para texto simples
- **Espaços em branco:** Múltiplos espaços reduzidos a um
- **Quebras de linha:** Convertidas em espaços

#### 📅 Formatação de Datas
- **Formato de entrada:** `YYYY-MM-DD HH:MM:SS`
- **Formato de saída:** `DD/MM/YYYY HH:MM:SS`

#### 📝 Limitação de Texto
- **Descrições:** Limitadas a 500 caracteres (+ "..." se truncado)
- **Campos de texto:** Limpeza de caracteres de controle

#### 🔄 Tradução de Status
- `1` → "Novo"
- `2` → "Em andamento (atribuído)"
- `3` → "Em andamento (planejado)"
- `4` → "Pendente"
- `5` → "Solucionado"
- `6` → "Fechado"

## 📈 Estatísticas das Últimas Extrações

### Extração Completa (Todos os Tickets)
**Arquivo gerado**: `tickets_api_glpi_otimizado_20251021_205703.csv`
**Localização**: `dados/tickets_mensais/`
- **Total de tickets**: 10,695
- **Tamanho do arquivo**: ~5.7 MB
- **Tempo de execução**: 3.8 segundos
- **Data de extração**: 21/10/2025 20:57

### Extrações com Filtro de Data e Organização Automática

#### Últimos 6 Meses
**Arquivo gerado**: `tickets_api_glpi_ultimos_6_meses_20251022_144233.csv`
**Localização**: `dados/tickets_6_meses/` ✨
- **Total de tickets**: 2,850
- **Período**: 25/04/2025 a 22/10/2025
- **Tamanho do arquivo**: ~1.5 MB
- **Tempo de execução**: 2.8 segundos
- **Data de extração**: 22/10/2025 14:42

#### Último Mês
**Arquivo gerado**: `tickets_api_glpi_ultimo_mes_20251022_144314.csv`
**Localização**: `dados/tickets_ultimo_mes/` ✨
- **Total de tickets**: 372
- **Período**: 22/09/2025 a 22/10/2025
- **Tamanho do arquivo**: ~200 KB
- **Tempo de execução**: 2.7 segundos
- **Data de extração**: 22/10/2025 14:43

#### Data Personalizada (Setembro 2025)
**Arquivo gerado**: `tickets_api_glpi_personalizado_20251022_144329.csv`
**Localização**: `dados/tickets_data_personalizada/` ✨
- **Total de tickets**: 379
- **Período**: 01/09/2025 a 30/09/2025
- **Tamanho do arquivo**: ~220 KB
- **Tempo de execução**: 2.6 segundos
- **Data de extração**: 22/10/2025 14:43

### Comparação com Banco Local
| Fonte | Registros | Observação |
|-------|-----------|------------|
| **API GLPI** | 10.695 | Dados atualizados e completos |
| **Banco Local** | 10.474 | Dados de teste (desatualizados) |
| **Diferença** | +221 | Novos tickets na API |

## 🔧 Funcionalidades Técnicas

### Sistema de Cache (Versão Otimizada)
```python
# Caches carregados uma única vez
cache_usuarios = {}      # Todos os usuários
cache_entidades = {}     # Todas as entidades
cache_categorias = {}    # Todas as categorias
cache_localizacoes = {}  # Todas as localizações
cache_grupos = {}        # Todos os grupos
```

### Busca de Relacionamentos
- **Ticket_User:** Relacionamentos usuário-ticket (requerente/técnico)
- **Group_Ticket:** Relacionamentos grupo-ticket (grupo técnico)
- **Processamento em lote:** Reduz chamadas à API

### Tratamento de Erros
- **Conexão:** Verificação de conectividade com a API
- **Autenticação:** Validação de tokens
- **Dados:** Tratamento de campos nulos/vazios
- **Encoding:** Suporte completo a UTF-8

## 🆚 Comparação: API vs Banco Local

### Vantagens da API
✅ **Dados atualizados:** Sempre os dados mais recentes  
✅ **Dados completos:** Todos os tickets do sistema  
✅ **Relacionamentos:** Dados de usuários, grupos, etc.  
✅ **Integridade:** Dados diretamente da fonte  

### Vantagens do Banco Local
✅ **Performance:** Consultas SQL mais rápidas  
✅ **Offline:** Funciona sem conexão com o GLPI  
✅ **Controle:** Dados sob controle local

## 📁 Organização dos Arquivos

Os arquivos CSV são automaticamente organizados em pastas específicas baseadas no tipo de execução:

### 🗂️ Estrutura de Pastas
- **`dados/tickets_6_meses/`** - Exports dos últimos 6 meses
- **`dados/tickets_ultimo_mes/`** - Exports do último mês  
- **`dados/tickets_data_personalizada/`** - Exports com datas personalizadas
- **`dados/tickets_mensais/`** - Outros períodos (3 meses, ano, etc.)

### 📝 Nomenclatura dos Arquivos
- `tickets_api_glpi_[periodo]_[timestamp].csv`

**Exemplos:**
- `tickets_api_glpi_ultimos_6_meses_20251022_144233.csv` → `dados/tickets_6_meses/`
- `tickets_api_glpi_ultimo_mes_20251022_144314.csv` → `dados/tickets_ultimo_mes/`
- `tickets_api_glpi_personalizado_20251022_144329.csv` → `dados/tickets_data_personalizada/`

## 🔄 Vantagens da API vs Banco Local

| Aspecto | API GLPI | Banco Local |
|---------|----------|-------------|
| **Dados** | Sempre atualizados | Podem estar defasados |
| **Acesso** | Direto via HTTP | Requer conexão com BD |
| **Manutenção** | Sem dependências locais | Requer configuração BD |
| **Performance** | Boa (3.8s para 10k tickets) | Variável |
| **Segurança** | Tokens de acesso | Credenciais de BD |
| **Filtros** | ✅ Por período de data | ❌ Limitado |

## 🎯 Vantagens do Filtro de Data

### 📊 Análises Direcionadas
- **Relatórios mensais**: Extrair apenas tickets do mês atual
- **Análises trimestrais**: Dados dos últimos 3 meses
- **Comparações anuais**: Tickets do ano atual vs ano passado

### ⚡ Performance Otimizada
- **Menos dados**: Arquivos menores e processamento mais rápido
- **Foco específico**: Apenas os dados necessários para análise
- **Economia de recursos**: Menor uso de memória e armazenamento

### 🔧 Flexibilidade
- **Períodos pré-definidos**: Opções comuns já configuradas
- **Datas personalizadas**: Qualquer período específico
- **Formato brasileiro**: Datas no formato DD/MM/YYYY  

## 🔄 Fluxo de Execução (Versão Otimizada)

1. **🔐 Autenticação**
   - Inicia sessão na API
   - Valida tokens de acesso

2. **🗄️ Carregamento de Caches**
   - Usuários (todos)
   - Entidades (todas)
   - Categorias (todas)
   - Localizações (todas)
   - Grupos (todos)

3. **🎫 Extração de Tickets**
   - Busca paginada (1000 por vez)
   - Dados básicos dos tickets

4. **🔗 Relacionamentos**
   - Ticket_User (em lote)
   - Group_Ticket (em lote)

5. **🧹 Processamento**
   - Limpeza de dados
   - Formatação de campos
   - Aplicação de traduções

6. **💾 Geração do CSV**
   - Arquivo com timestamp
   - Encoding UTF-8
   - Aspas em todos os campos

## 📝 Logs de Execução

### Exemplo de Saída
```
🚀 EXTRATOR OTIMIZADO DE DADOS DA API GLPI
============================================================
🔐 Iniciando sessão na API do GLPI...
✅ Sessão iniciada com sucesso!
🔄 Carregando caches para otimização...
👥 Carregando cache de usuários...
   ✅ 1.234 usuários carregados
🏢 Carregando cache de entidades...
   ✅ 45 entidades carregadas
📂 Carregando cache de categorias...
   ✅ 67 categorias carregadas
📍 Carregando cache de localizações...
   ✅ 49 localizações carregadas
👨‍💻 Carregando cache de grupos...
   ✅ 85 grupos carregados
✅ Todos os caches carregados!
🎫 Buscando tickets com relacionamentos...
✅ Total de tickets encontrados: 10,695
🔗 Buscando relacionamentos de usuários e grupos...
🧹 Processando e formatando dados...
💾 Gerando arquivo: tickets_api_glpi_otimizado_20251021_205703.csv
✅ Extração concluída com sucesso!
📁 Arquivo: ../dados/tickets_mensais/tickets_api_glpi_otimizado_20251021_205703.csv
📈 Total de registros: 10,695
🕒 Timestamp: 20251021_205703
⏱️ Tempo de execução: 0:00:03.829617
```

## 🔧 Manutenção e Atualizações

### Atualizando Credenciais
Para atualizar as credenciais da API, edite as variáveis no início da função `main()`:
```python
API_URL = "http://cau.ppiratini.intra.rs.gov.br/glpi/apirest.php"
APP_TOKEN = "seu_app_token_aqui"
USER_TOKEN = "seu_user_token_aqui"
```

### Modificando Campos Extraídos
Para adicionar/remover campos, edite:
1. A consulta de tickets na função `buscar_tickets_com_relacionamentos()`
2. O processamento na função `extrair_todos_tickets()`
3. O cabeçalho do CSV

### Ajustando Performance
- **Range de busca:** Modifique `range_limit` (padrão: 1000)
- **Cache:** Ajuste os ranges dos caches se necessário
- **Timeout:** Configure timeouts nas requisições se necessário

## 🚨 Troubleshooting

### Problemas Comuns

#### Erro de Autenticação
```
❌ Erro ao iniciar sessão: 401
```
**Solução:** Verificar se os tokens estão corretos e válidos

#### Timeout de Conexão
```
❌ Erro na conexão: timeout
```
**Solução:** Verificar conectividade de rede com o servidor GLPI

#### Dados Incompletos
```
⚠️ Erro ao carregar usuários: 500
```
**Solução:** Verificar se o usuário da API tem permissões adequadas

## 📞 Suporte

Para dúvidas ou problemas:
1. Verificar logs de execução
2. Validar conectividade com a API
3. Confirmar permissões do usuário da API
4. Consultar documentação da API do GLPI

---

**Última atualização:** 21/10/2025  
**Versão:** 2.0 (Otimizada)  
**Autor:** Sistema de Extração CAU
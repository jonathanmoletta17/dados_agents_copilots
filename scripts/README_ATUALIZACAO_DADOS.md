# 📊 Sistema de Atualização de Dados GLPI - Casa Civil RS

## 🎯 Objetivo
Este documento descreve o processo unificado de atualização de todos os dados GLPI, garantindo consistência e integridade para alimentação da base SharePoint.

## 🚀 Script Principal

### `atualizar_dados_glpi.py`
**Localização:** `C:/Users/jonathan-moletta/OneDrive - Governo do Estado do Rio Grande do Sul/Área de Trabalho/BD_cau_sis/bd_cau/scripts/atualizar_dados_glpi.py`

**Função:** Script unificado que executa todas as etapas de atualização de dados em sequência.

### Como Executar
```powershell
cd "C:/Users/jonathan-moletta/OneDrive - Governo do Estado do Rio Grande do Sul/Área de Trabalho/BD_cau_sis/bd_cau/scripts"
python atualizar_dados_glpi.py
```

## 📋 Etapas do Processo de Atualização

### 1️⃣ Extração de Tickets Completos
- **Script:** `extrair_todos_tickets.py`
- **Saída:** `dados/tickets_completos/todos_tickets_atual.xlsx`
- **Função:** Extrai todos os tickets do GLPI sem filtro de data

### 2️⃣ Extração de Tickets dos Últimos 6 Meses
- **Script:** `extrair_todos_tickets.py` (com filtro de data)
- **Saída:** `dados/tickets_6_meses/tickets_ultimos_6_meses_atual.xlsx`
- **Função:** Extrai apenas tickets dos últimos 6 meses

### 3️⃣ Geração de Métricas e Análises
- **Script:** `extrair_metricas_tickets_otimizado.py`
- **Saída:** `dados/metricas_xlsx/`
- **Arquivos gerados:**
  - `status_atual.xlsx` - Análise por status
  - `tecnicos_atual.xlsx` - Análise por técnico
  - `entidades_atual.xlsx` - Análise por entidade
  - `relatorio_qualidade_atual.xlsx` - Relatório de qualidade
  - `columns_profile_atual.xlsx` - Perfil das colunas
  - `dataset_resumo_atual.xlsx` - Resumo do dataset

### 4️⃣ Atualização de Históricos
- **Script:** `endpoints/historico_tickets_api.py`
- **Saída:** `dados/historicos/`
- **Função:** Gera históricos detalhados de tickets específicos

### 5️⃣ Preparação para SharePoint
- **Função:** Cria arquivo consolidado com todos os dados
- **Saída:** `dados/resumo_exportacao.json`
- **Integração:** Prepara dados para consumo pelo agente SharePoint

## 📁 Estrutura de Diretórios

```
scripts/
├── atualizar_dados_glpi.py          # Script principal unificado
├── converter_csv_para_xlsx.py       # Utilitário de conversão
├── dados/
│   ├── tickets_completos/           # Tickets completos (XLSX)
│   ├── tickets_6_meses/            # Tickets últimos 6 meses (XLSX)
│   ├── metricas_xlsx/              # Métricas e análises (XLSX)
│   ├── historicos/                 # Históricos de tickets (XLSX)
│   └── resumo_exportacao.json      # Resumo para SharePoint
└── python/
    ├── extrair_todos_tickets.py     # Extração principal
    ├── extrair_metricas_tickets_otimizado.py  # Geração de métricas
    ├── endpoints/
    │   └── historico_tickets_api.py # Históricos
    ├── tools/
    │   ├── dashboard_gerencial.py   # Dashboard gerencial
    │   └── profile_tickets_csv.py   # Perfil de tickets
    └── file_manager.py              # Gerenciador de arquivos
```

## ✅ Verificação de Sucesso

O script principal verifica automaticamente:
- ✅ Tickets completos extraídos
- ✅ Tickets dos últimos 6 meses extraídos
- ✅ Métricas geradas
- ✅ Históricos atualizados
- ✅ Dados preparados para SharePoint

## 🔄 Frequência de Atualização

Recomenda-se executar o script:
- **Diariamente** - Para dados operacionais
- **Semanalmente** - Para relatórios gerenciais
- **Mensalmente** - Para análises estratégicas

## 📊 Arquivos de Saída

### Formato XLSX (Excel)
Todos os dados agora são gerados em formato XLSX para melhor compatibilidade e funcionalidades avançadas do Excel.

### Backup Automático
O sistema mantém backups automáticos dos arquivos anteriores com timestamp.

## 🚨 Tratamento de Erros

O script possui:
- Verificação de pré-requisitos
- Tratamento de timeouts
- Logs detalhados de execução
- Validação de arquivos gerados
- Relatório de sucesso/falha por etapa

## 📞 Suporte

Em caso de erros:
1. Verifique os logs gerados durante a execução
2. Confirme que todos os scripts necessários existem
3. Verifique permissões de escrita nos diretórios
4. Execute novamente o script principal

## 🎯 Resultado Final

Após a execução bem-sucedida, você terá:
- ✅ Todos os tickets atualizados em XLSX
- ✅ Métricas e análises geradas
- ✅ Históricos atualizados
- ✅ Dados prontos para SharePoint
- ✅ Base consistente para seu agente

---

**Última atualização:** Novembro 2025
**Versão:** 1.0 - Script unificado
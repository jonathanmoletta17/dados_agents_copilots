# Blueprint Conceitual: Agente Analista DTIC/GLPI

> Baseado no blueprint geral de agente analista de dados, adaptado especificamente para a base DTIC/GLPI

## Contexto DTIC

A DTIC (Diretoria de Tecnologia da Informação e Comunicação) utiliza o GLPI para gerenciamento de tickets de suporte IT. O agente deve ser capaz de analisar:
- **Tickets** (incidentes, requisições, problemas)
- **Usuários** (solicitantes, técnicos, equipes)
- **Métricas** (SLA, tempo de resolução, volume)
- **Categorias** (hardware, software, rede, etc.)

## Arquitetura Proposta

### 1. APIs Analytics DTIC

```
/api/v1/analytics/dtic/
├── tickets/
│   ├── metrics          # KPIs agregados
│   ├── trends           # Séries temporais
│   ├── by-category      # Distribuição por categoria
│   ├── by-priority      # Distribuição por prioridade
│   └── by-technician    # Performance de técnicos
├── sla/
│   ├── compliance       # Taxa de conformidade
│   └── violations       # Detalhes de violações
├── users/
│   ├── summary          # Resumo de usuários
│   └── requesters-top   # Top solicitantes
└── inventory/
    └── summary          # Resumo de inventário (opcional)
```

### 2. Custom Connector: DTIC Analytics

**Nome:** `DTIC Analytics Connector`

**Ações:**
1. **Get Tickets Metrics** - Métricas agregadas de tickets
2. **Get Tickets Trends** - Tendências ao longo do tempo
3. **Get SLA Compliance** - Taxa de conformidade com SLA
4. **Get Technician Performance** - Performance de técnicos
5. **Get Category Distribution** - Distribuição por categoria

### 3. Estrutura de Topics

```
Topics/
├── System Topics/
│   └── Conversation Start          # Inicialização: carregar contexto
├── Analytics Request               # Topic principal
│   ├── Metrics Analysis           # Análise de métricas
│   ├── SLA Analysis               # Análise de SLA
│   ├── Technician Performance     # Performance de técnicos
│   └── Trend Analysis             # Análise de tendências
└── Utilities/
    ├── Context Reset              # Reset de variáveis
    └── Period Selection           # Seleção de período
```

### 4. Variáveis Globais

```javascript
// Contexto de Período
{
  selected_start_date: Date,
  selected_end_date: Date,
  selected_period_label: String // "Novembro 2025", "Últimos 30 dias"
}

// Cache de Dados
{
  last_metrics_dtic: Object,      // Último resultado de metrics
  last_sla_data: Object,          // Último resultado de SLA
  cache_timestamp: DateTime       // Quando foi carregado
}

// Preferências do Usuário
{
  user_default_period: String,    // "current_month", "last_30_days"
  user_default_view: String       // "metrics", "sla", "trends"
}
```

## Fluxos de Análise

### Fluxo 1: Métricas Gerais

**Pergunta do Usuário:** "Quantos tickets tivemos este mês?"

**Orquestração:**
1. Agente identifica: necessita métricas de tickets
2. Verifica cache: tem dados do mês corrente?
   - Se sim e < 5 min: usar cache
   - Se não ou expirado: chamar `Get Tickets Metrics`
3. Armazena em `last_metrics_dtic`
4. Envia JSON para prompt de análise
5. Retorna resposta formatada

**Prompt de Análise:**
```
System: Você é analista de dados especializado em help desk DTIC.
Analise as métricas e forneça resumo executivo.

User: Métricas de tickets:
{last_metrics_dtic}

Formate: resumo (2-3 linhas) + tabela + insights principais
```

### Fluxo 2: Análise de SLA

**Pergunta do Usuário:** "Como está o SLA da DTIC?"

**Orquestração:**
1. Chamar `Get SLA Compliance`
2. Processar JSON
3. Identificar problemas (< 90%)
4. Gerar recomendações

**Prompt de Análise:**
```
Analise o SLA e identifique:
- Taxa de conformidade atual
- Tendência (melhorando/piorando)
- Categorias/técnicos com problemas
- Ações recomendadas
```

### Fluxo 3: Comparação Temporal

**Pergunta do Usuário:** "Compare este mês com o anterior"

**Orquestração:**
1. Chamar `Get Tickets Metrics` para mês corrente
2. Chamar `Get Tickets Metrics` para mês anterior
3. Enviar ambos JSONs para prompt de comparação
4. Retorna análise de variações

## Especificação de Dados

### Payload: Tickets Metrics

```json
{
  "period": {
    "start": "2025-11-01",
    "end": "2025-11-30",
    "label": "Novembro 2025"
  },
  "summary": {
    "total_tickets": 842,
    "open_tickets": 132,
    "closed_tickets": 710,
    "resolution_rate": 84.3
  },
  "sla": {
    "compliance_percent": 87.5,
    "total_violations": 16,
    "avg_resolution_hours": 28.5
  },
  "by_priority": {
    "critical": 12,
    "high": 85,
    "medium": 324,
    "low": 421
  },
  "by_category": {
    "hardware": 215,
    "software": 298,
    "network": 156,
    "access": 173
  },
  "top_requesters": [
    {"name": "SEFAZ", "count": 127},
    {"name": "DETRAN", "count": 98}
  ]
}
```

### Payload: SLA Compliance

```json
{
  "overall": {
    "compliance_percent": 87.5,
    "total_tickets": 842,
    "within_sla": 737,
    "violated_sla": 105
  },
  "by_priority": {
    "critical": {"compliance": 91.7, "violated": 1},
    "high": {"compliance": 85.9, "violated": 12},
    "medium": {"compliance": 88.3, "violated": 38},
    "low": {"compliance": 87.2, "violated": 54}
  },
  "avg_times": {
    "first_response_hours": 2.3,
    "resolution_hours": 28.5,
    "target_resolution_hours": 24.0
  },
  "violations_detail": [
    {
      "ticket_id": 10245,
      "category": "network",
      "hours_over_sla": 12.5,
      "assigned_to": "João Silva"
    }
  ]
}
```

### Payload: Technician Performance

```json
{
  "period": "2025-11-01 to 2025-11-30",
  "technicians": [
    {
      "name": "João Silva",
      "total_assigned": 45,
      "resolved": 38,
      "resolution_rate": 84.4,
      "avg_resolution_hours": 22.3,
      "sla_compliance": 89.5
    },
    {
      "name": "Maria Santos",
      "total_assigned": 52,
      "resolved": 48,
      "resolution_rate": 92.3,
      "avg_resolution_hours": 18.7,
      "sla_compliance": 94.2
    }
  ],
  "team_averages": {
    "avg_resolution_rate": 86.7,
    "avg_resolution_hours": 28.5,
    "avg_sla_compliance": 87.5
  }
}
```

## Templates de Prompts

### Template: Análise de Métricas

```markdown
System Instructions:
Você é um analista de dados da DTIC especializado em help desk.
Responda de forma executiva, destacando números importantes.
Use tabelas markdown quando apropriado.

User Prompt Template:
Analise as seguintes métricas de tickets da DTIC:
{json_metrics}

Forneça:
1. Resumo executivo (2-3 linhas)
2. Tabela com métricas principais
3. Destaques positivos e negativos
4. Alertas (se SLA < 90%, tempo > 24h, etc.)
```

### Template: Comparação de Períodos

```markdown
Compare os dados de tickets DTIC:

**Período Atual:**
{json_current}

**Período Anterior:**
{json_previous}

Identifique:
- Variações percentuais em volume, SLA, tempo de resolução
- Tendências (melhora, piora, estabilidade)
- Possíveis causas das variações
- Recomendações para gestão
```

### Template: Análise de Técnicos

```markdown
Analise a performance dos técnicos DTIC:
{json_technicians}

Para cada técnico:
- Compare com média do time
- Identifique outliers (> 1.5 desvio padrão)
- Destaque alto desempenho (reconhecimento)
- Identifique necessidade de suporte/treinamento

Retorne ranking e recomendações.
```

## Regras de Cache e Performance

### Quando Usar Cache
- Métricas do período corrente (< 5 minutos)
- Dados históricos (não mudam)
- Configurações de usuário

### Quando Invalidar Cache
- Usuário muda período/filtros
- Dados > 5 minutos (para período corrente)
- Usuário solicita "atualizar"

### Otimização de Payloads
- APIs retornam apenas campos necessários
- Paginação: máximo 10 técnicos, 5 categorias na primeira resposta
- Se usuário pedir detalhes, nova chamada com filtro específico

## Limitações e Contornos

| Limitação | Estratégia |
|-----------|------------|
| 28KB por mensagem | APIs retornam dados agregados |
| Contexto de análise | Usar apenas resumos estatísticos |
| Token window | Limpar histórico após 10 turnos |
| Performance | Cache de 5 min para dados agregados |

## Checklist de Implementação

### Backend (APIs DTIC)
- [ ] Endpoint `/metrics` (agregados por período)
- [ ] Endpoint `/sla/compliance` (taxa e violações)
- [ ] Endpoint `/trends` (séries temporais)
- [ ] Endpoint `/technicians` (performance)
- [ ] Cache no backend (5 min)
- [ ] Especificação OpenAPI v2

### Copilot Studio
- [ ] Importar custom connector
- [ ] Criar variáveis globais
- [ ] Topic: Conversation Start (init)
- [ ] Topic: Metrics Analysis
- [ ] Topic: SLA Analysis
- [ ] Topic: Technician Performance
- [ ] Prompts de análise configurados
- [ ] Testes end-to-end

---

**Este blueprint é a base para implementação do agente DTIC. Próximo passo: criar as APIs analytics no backend.**

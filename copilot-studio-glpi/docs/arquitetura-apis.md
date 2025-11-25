# Arquitetura de APIs Analytics para DTIC

## Princípios de Design

### 1. APIs Especializadas para Análise
As APIs analytics são **otimizadas para consumo pelo agente**, retornando dados agregados ao invés de registros brutos.

### 2. Estrutura de Endpoints

```
Base URL: https://api.dtic.rs.gov.br/api/v1/analytics/dtic
```

## Endpoints Detalhados

### 1. GET `/tickets/metrics`

**Descrição:** Retorna métricas agregadas de tickets para um período específico.

**Parâmetros Query:**
| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `start_date` | string (date) | Sim | Data início (YYYY-MM-DD) |
| `end_date` | string (date) | Sim | Data fim (YYYY-MM-DD) |
| `category` | string | Não | Filtrar por categoria específica |
| `priority` | string | Não | Filtrar por prioridade |

**Response (200 OK):**
```json
{
  "period": {
    "start": "2025-11-01",
    "end": "2025-11-30",
    "label": "Novembro 2025",
    "days": 30
  },
  "summary": {
    "total_tickets": 842,
    "open_tickets": 132,
    "closed_tickets": 710,
    "in_progress": 98,
    "pending": 34,
    "resolution_rate_percent": 84.3
  },
  "sla": {
    "compliance_percent": 87.5,
    "within_sla": 737,
    "violated_sla": 105,
    "avg_resolution_hours": 28.5,
    "target_hours": 24.0
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
  "by_status": {
    "new": 45,
    "assigned": 53,
    "in_progress": 98,
    "pending": 34,
    "resolved": 612,
    "closed": 98
  },
  "top_requesters": [
    {"entity": "SEFAZ", "count": 127},
    {"entity": "DETRAN", "count": 98},
    {"entity": "SEDA", "count": 76},
    {"entity": "SSP", "count": 65},
    {"entity": "SEDUC", "count": 58}
  ],
  "metadata": {
    "generated_at": "2025-11-25T03:22:00Z",
    "cache_ttl_seconds": 300
  }
}
```

**Tamanho Estimado:** ~2KB (bem abaixo do limite de 28KB)

---

### 2. GET `/tickets/trends`

**Descrição:** Retorna série temporal de tickets para análise de tendências.

**Parâmetros Query:**
| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `start_date` | string (date) | Sim | Data início |
| `end_date` | string (date) | Sim | Data fim |
| `granularity` | enum | Não | day, week, month (padrão: day) |
| `metric` | enum | Não | count, resolution_time, sla_compliance |

**Response (200 OK):**
```json
{
  "period": {
    "start": "2025-10-01",
    "end": "2025-11-30",
    "granularity": "week"
  },
  "series": [
    {
      "date": "2025-10-01",
      "count": 187,
      "avg_resolution_hours": 26.3,
      "sla_compliance_percent": 88.2
    },
    {
      "date": "2025-10-08",
      "count": 203,
      "avg_resolution_hours": 29.1,
      "sla_compliance_percent": 85.7
    }
    // ... mais pontos
  ],
  "statistics": {
    "avg_count": 195.4,
    "std_dev_count": 18.7,
    "trend": "increasing",  // increasing, decreasing, stable
    "variation_percent": 8.6
  }
}
```

---

### 3. GET `/sla/compliance`

**Descrição:** Detalhes de conformidade com SLA.

**Parâmetros Query:**
| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `start_date` | string (date) | Sim | Data início |
| `end_date` | string (date) | Sim | Data fim |
| `include_violations` | boolean | Não | Incluir detalhes de violações (padrão: false) |

**Response (200 OK):**
```json
{
  "overall": {
    "compliance_percent": 87.5,
    "total_tickets": 842,
    "within_sla": 737,
    "violated_sla": 105
  },
  "by_priority": {
    "critical": {
      "compliance_percent": 91.7,
      "total": 12,
      "violated": 1,
      "avg_resolution_hours": 8.3,
      "target_hours": 4.0
    },
    "high": {
      "compliance_percent": 85.9,
      "total": 85,
      "violated": 12,
      "avg_resolution_hours": 14.5,
      "target_hours": 12.0
    },
    "medium": {
      "compliance_percent": 88.3,
      "total": 324,
      "violated": 38,
      "avg_resolution_hours": 22.1,
      "target_hours": 24.0
    },
    "low": {
      "compliance_percent": 87.2,
      "total": 421,
      "violated": 54,
      "avg_resolution_hours": 46.8,
      "target_hours": 48.0
    }
  },
  "by_category": {
    "hardware": {"compliance_percent": 89.3, "violated": 23},
    "software": {"compliance_percent": 85.6, "violated": 43},
    "network": {"compliance_percent": 88.5, "violated": 18},
    "access": {"compliance_percent": 87.9, "violated": 21}
  },
  "avg_times": {
    "first_response_hours": 2.3,
    "resolution_hours": 28.5,
    "target_resolution_hours": 24.0,
    "variance_hours": 4.5
  },
  "violations_summary": {
    "total": 105,
    "by_severity": {
      "minor": 67,      // < 6h over
      "moderate": 28,   // 6-24h over
      "severe": 10      // > 24h over
    }
  }
}
```

**Com `include_violations=true` (adiciona):**
```json
{
  "violations_detail": [
    {
      "ticket_id": 10245,
      "title": "Impressora não funciona",
      "category": "hardware",
      "priority": "medium",
      "assigned_to": "João Silva",
      "hours_over_sla": 12.5,
      "opened_at": "2025-11-15T08:30:00Z",
      "resolved_at": "2025-11-17T20:30:00Z"
    }
    // ... máximo 10 violações mais graves
  ]
}
```

---

### 4. GET `/technicians/performance`

**Descrição:** Performance de técnicos por período.

**Parâmetros Query:**
| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `start_date` | string (date) | Sim | Data início |
| `end_date` | string (date) | Sim | Data fim |
| `top_n` | integer | Não | Retornar top N técnicos (padrão: 10) |

**Response (200 OK):**
```json
{
  "period": "2025-11-01 to 2025-11-30",
  "technicians": [
    {
      "id": 42,
      "name": "Maria Santos",
      "total_assigned": 52,
      "resolved": 48,
      "in_progress": 3,
      "pending": 1,
      "resolution_rate_percent": 92.3,
      "avg_resolution_hours": 18.7,
      "sla_compliance_percent": 94.2,
      "first_response_avg_hours": 1.2
    },
    {
      "id": 38,
      "name": "João Silva",
      "total_assigned": 45,
      "resolved": 38,
      "in_progress": 5,
      "pending": 2,
      "resolution_rate_percent": 84.4,
      "avg_resolution_hours": 22.3,
      "sla_compliance_percent": 89.5,
      "first_response_avg_hours": 2.1
    }
    // ... até top_n
  ],
  "team_statistics": {
    "total_technicians": 12,
    "avg_resolution_rate_percent": 86.7,
    "avg_resolution_hours": 28.5,
    "avg_sla_compliance_percent": 87.5,
    "std_dev_resolution_hours": 8.3
  },
  "outliers": {
    "high_performers": ["Maria Santos"],  // > 1.5 std dev above mean
    "need_support": ["Carlos Mendes"]     // > 1.5 std dev below mean
  }
}
```

---

### 5. GET `/tickets/by-category`

**Descrição:** Distribuição detalhada por categoria.

**Response (200 OK):**
```json
{
  "categories": [
    {
      "name": "Software",
      "total": 298,
      "open": 45,
      "closed": 253,
      "avg_resolution_hours": 24.3,
      "sla_compliance_percent": 85.6,
      "subcategories": [
        {"name": "Office", "count": 87},
        {"name": "ERP", "count": 65},
        {"name": "Browser", "count": 52}
      ]
    },
    {
      "name": "Hardware",
      "total": 215,
      "open": 32,
      "closed": 183,
      "avg_resolution_hours": 31.2,
      "sla_compliance_percent": 89.3,
      "subcategories": [
        {"name": "Impressora", "count": 78},
        {"name": "Desktop", "count": 54},
        {"name": "Notebook", "count": 43}
      ]
    }
  ]
}
```

---

## Estrutura de Erros

Todas as APIs seguem o mesmo padrão de erro:

```json
{
  "error": {
    "code": "INVALID_DATE_RANGE",
    "message": "Data de início deve ser anterior à data de fim",
    "details": {
      "start_date": "2025-11-30",
      "end_date": "2025-11-01"
    }
  }
}
```

**Códigos de Erro Comuns:**
- `INVALID_DATE_RANGE` (400)
- `MISSING_REQUIRED_PARAM` (400)
- `UNAUTHORIZED` (401)
- `FORBIDDEN` (403)
- `INTERNAL_SERVER_ERROR` (500)

---

## Autenticação

**Método Recomendado:** OAuth 2.0 (Client Credentials)

```
POST /oauth/token
Content-Type: application/x-www-form-urlencoded

grant_type=client_credentials
&client_id={client_id}
&client_secret={client_secret}
&scope=analytics:read

Response:
{
  "access_token": "eyJ...",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

**Uso:**
```
GET /api/v1/analytics/dtic/tickets/metrics?start_date=2025-11-01&end_date=2025-11-30
Authorization: Bearer eyJ...
```

**Alternativa:** API Key

```
GET /api/v1/analytics/dtic/tickets/metrics?start_date=2025-11-01&end_date=2025-11-30
X-API-Key: {api_key}
```

---

## Cache e Performance

### Backend Caching
- Dados agregados: cache de **5 minutos**
- Dados históricos (> 30 dias): cache de **1 hora**
- Headers HTTP: `Cache-Control`, `ETag`

### Rate Limiting
- 100 requisições por minuto por cliente
- Header de resposta: `X-RateLimit-Remaining`

---

## Checklist de Implementação Backend

- [ ] Endpoint `/tickets/metrics` com agregações
- [ ] Endpoint `/tickets/trends` com séries temporais
- [ ] Endpoint `/sla/compliance` com detalhes de SLA
- [ ] Endpoint `/technicians/performance` com rankings
- [ ] Endpoint `/tickets/by-category` com distribuição
- [ ] Cache Redis (5 min para dados correntes)
- [ ] Autenticação OAuth 2.0
- [ ] Rate limiting (100 req/min)
- [ ] Logs de auditoria
- [ ] Testes unitários e integração
- [ ] Geração de especificação OpenAPI v2

---

**Próximo passo:** Gerar especificação OpenAPI v2 e configurar custom connector no Copilot Studio.

# GLPI Data Service - Guia de Uso da API

## 🚀 Iniciar Serviço

### 1. Configurar Ambiente
```bash
# Copiar template de variáveis
cp .env.example .env

# Editar com suas credenciais GLPI
nano .env
```

### 2. Iniciar PostgreSQL
```bash
docker-compose up -d postgres pgadmin
```

### 3. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 4. Iniciar API
```bash
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

## 📡 Endpoints da API

### Base URL
```
http://localhost:8000
```

### Documentação Interativa
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🎯 Endpoints Disponíveis

### 1. Health Check

```http
GET /health
```

**Resposta:**
```json
{
  "status": "healthy",
  "timestamp": "2024-11-22T01:00:00",
  "contextos": {
    "dtic": {
      "banco_dados": "ok",
      "total_tickets": 11080,
      "ultima_sincronizacao": "2024-11-22T00:50:00"
    },
    "sis": {
      "banco_dados": "ok",
      "total_tickets": 4890,
      "ultima_sincronizacao": "2024-11-22T00:50:00"
    }
  }
}
```

### 2. Listar Tickets (por Contexto)

```http
GET /api/v1/{contexto}/tickets
```

**Parâmetros:**
- `contexto`: `dtic` ou `sis` (obrigatório)
- `limite`: Número de resultados (1-500, padrão: 50)
- `pagina`: Número da página (padrão: 1)
- `status`: Filtrar por status (opcional)
- `tecnico`: Filtrar por técnico (opcional)
- `categoria`: Filtrar por categoria (opcional)
- `prioridade`: Filtrar por prioridade (opcional)

**Exemplos:**
```bash
# Listar tickets DTIC (primeira página)
GET /api/v1/dtic/tickets?limite=20&pagina=1

# Listar tickets SIS com status NOVO
GET /api/v1/sis/tickets?status=NOVO

# Filtrar por técnico
GET /api/v1/dtic/tickets?tecnico=Anderson

# Filtrar por categoria e prioridade
GET /api/v1/dtic/tickets?categoria=Impressão&prioridade=ALTA
```

**Resposta:**
```json
{
  "contexto": "dtic",
  "total": 11080,
  "pagina": 1,
  "limite": 20,
  "total_paginas": 554,
  "tickets": [
    {
      "id": 1,
      "glpi_id": 12345,
      "titulo": "Problema com impressora",
      "status": "ATRIBUIDO",
      "prioridade": "MEDIA",
      "tecnico": "Anderson Souza",
      "categoria": "Impressão",
      "criado_em": "2024-11-20T10:00:00",
      "atualizado_em": "2024-11-20T15:30:00",
      "url": "http://glpi/ticket.form.php?id=12345"
    }
  ]
}
```

### 3. Obter Ticket Específico

```http
GET /api/v1/{contexto}/tickets/{glpi_id}
```

**Exemplo:**
```bash
GET /api/v1/dtic/tickets/12345
```

**Resposta (todos os campos):**
```json
{
  "id": 1,
  "glpi_id": 12345,
  "titulo": "Problema com impressora Canon",
  "descricao": "<p>Descrição HTML...</p>",
  "descricao_md": "Descrição em Markdown...",
  "status": "ATRIBUIDO",
  "prioridade": "MEDIA",
  "tipo": "INCIDENT",
  "impact": 3,
  "urgency": 3,
  "categoria": "Impressão",
  "entidade": "DTIC",
  "tecnico": "Anderson Souza",
  "grupo": "Suporte N1" ,
  "grupo_nivel": "N1",
  "requerente": "Maria Santos",
  "localizacao": "Prédio A - Sala 101",
  "tempo_acao_total": 1800,
  "custo_tempo": 50.00,
  "criado_em": "2024-11-20T10:00:00Z",
  "atualizado_em": "2024-11-20T15:30:00Z",
  "solucionado_em": null,
  "fechado_em": null,
  "url": "http://glpi/ticket.form.php?id=12345"
}
```

### 4. Estatísticas Resumidas

```http
GET /api/v1/{contexto}/estatisticas/resumo
```

**Exemplo:**
```bash
GET /api/v1/dtic/estatisticas/resumo
```

**Resposta:**
```json
{
  "contexto": "dtic",
  "periodo": {
    "data_inicio": null,
    "data_fim": null
  },
  "total_tickets": 11080,
  "por_status": {
    "novos": 150,
    "atribuidos": 300,
    "pendentes": 50,
    "solucionados": 8500,
    "fechados": 2080
  }
}
```

### 5. Ranking de Técnicos

```http
GET /api/v1/{contexto}/estatisticas/tecnicos
```

**Parâmetros:**
- `limite`: Número de técnicos no ranking (1-100, padrão: 20)

**Exemplo:**
```bash
GET /api/v1/dtic/estatisticas/tecnicos?limite=10
```

**Resposta:**
```json
{
  "contexto": "dtic",
  "ranking": [
    {
      "posicao": 1,
      "tecnico": "Anderson Souza",
      "total_tickets": 2808,
      "tickets_resolvidos": 2650,
      "taxa_resolucao": 94.37
    },
    {
      "posicao": 2,
      "tecnico": "João Silva",
      "total_tickets": 1850,
      "tickets_resolvidos": 1720,
      "taxa_resolucao": 92.97
    }
  ]
}
```

### 6. Disparar Sincronização Manual

```http
POST /api/v1/{contexto}/sincronizar
```

**Parâmetros:**
- `completa`: Se `true`, executa sync completa (padrão: `false`)

**Exemplos:**
```bash
# Sincronização incremental (últimas mudanças)
POST /api/v1/dtic/sincronizar

# Sincronização completa
POST /api/v1/dtic/sincronizar?completa=true
```

**Resposta:**
```json
{
  "status": "success",
  "tipo": "incremental",
  "contexto": "dtic"
}
```

### 7. Histórico de Sincronizações

```http
GET /api/v1/{contexto}/sincronizacao/historico
```

**Parâmetros:**
- `limite`: Número de registros (1-100, padrão: 10)

**Exemplo:**
```bash
GET /api/v1/dtic/sincronizacao/historico?limite=5
```

**Resposta:**
```json
{
  "contexto": "dtic",
  "historico": [
    {
      "id": 42,
      "tipo": "INCREMENTAL",
      "tickets_novos": 5,
      "tickets_atualizados": 12,
      "tickets_total": 17,
      "erros": 0,
      "duracao_segundos": 3.45,
      "iniciado_em": "2024-11-22T00:50:00Z",
      "finalizado_em": "2024-11-22T00:50:03Z",
      "sucesso": true
    }
  ]
}
```

## 🔗 Nomenclaturas e Convenções

### Contextos
- `dtic` - Tickets do departamento DTIC
- `sis` - Tickets do  SIS (Manutenção)

### Status de Tickets
- `NOVO` - Ticket recém criado
- `ATRIBUIDO` - Atribuído a um técnico/grupo
- `PLANEJADO` - Planejado para execução
- `PENDENTE` - Aguardando informações/recursos
- `SOLUCIONADO` - Solução aplicada
- `FECHADO` - Ticket encerrado

### Prioridades
- `MUITO_BAIXA` - Prioridade 1
- `BAIXA` - Prioridade 2
- `MEDIA` - Prioridade 3
- `ALTA` - Prioridade 4
- `MUITO_ALTA` - Prioridade 5
- `CRITICA` - Prioridade 6

### Níveis de Suporte
- `N1` - Nível 1 (Suporte básico)
- `N2` - Nível 2 (Suporte intermediário)
- `N3` - Nível 3 (Especializado)
- `N4` - Nível 4 (Avançado/Desenvolvimento)

## 📊 Integração com Frontend

### Exemplo React (Axios)

```javascript
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

// Listar tickets DTIC
const getTicketsDTIC = async (page = 1, limit = 50) => {
  const response = await axios.get(`${API_BASE_URL}/api/v1/dtic/tickets`, {
    params: { pagina: page, limite: limit }
  });
  return response.data;
};

// Obter estatísticas
const getStats = async (contexto = 'dtic') => {
  const response = await axios.get(`${API_BASE_URL}/api/v1/${contexto}/estatisticas/resumo`);
  return response.data;
};

// Ranking de técnicos
const getRanking = async (contexto = 'dtic') => {
  const response = await axios.get(`${API_BASE_URL}/api/v1/${contexto}/estatisticas/tecnicos`);
  return response.data;
};
```

## 🐛 Tratamento de Erros

### Códigos de Status HTTP
- `200` - Sucesso
- `400` - Requisição inválida (contexto inválido, parâmetros errados)
- `404` - Recurso não encontrado (ticket não existe)
- `500` - Erro interno do servidor

### Exemplo de Erro
```json
{
  "detail": "Contexto inválido. Use 'dtic' ou 'sis'."
}
```

## 🔐 Acesso ao pgAdmin

- **URL**: http://localhost:5050
- **Login**: admin@localhost.com
- **Senha**: admin

### Explorar Dados no pgAdmin

1. Expandir `Servers` → `GLPI Database (Local)`
2. Expandir `Databases` → `glpi_data`
3. Expandir `Schemas`:
   - `dtic` - Ver tabelas DTIC
   - `sis` - Ver tabelas SIS

### Consultas SQL Úteis

```sql
-- Total de tickets por status (DTIC)
SELECT status, COUNT(*) as total
FROM dtic.tickets
WHERE is_deleted = false
GROUP BY status
ORDER BY total DESC;

-- Ranking de técnicos (SIS)
SELECT tecnico, COUNT(*) as total_resolvido
FROM sis.tickets
WHERE status IN ('SOLUCIONADO', 'FECHADO')
  AND tecnico IS NOT NULL
GROUP BY tecnico
ORDER BY total_resolvido DESC
LIMIT 20;

-- Tickets por categoria (DTIC)
SELECT categoria, COUNT(*) as total
FROM dtic.tickets
WHERE categoria IS NOT NULL
GROUP BY categoria
ORDER BY total DESC;
```

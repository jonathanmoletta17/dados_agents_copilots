# GLPI Data Service - PostgreSQL Edition

Serviço centralizado para sincronização de dados do GLPI usando **PostgreSQL** com schemas separados para DTIC e SIS.

## 🎯 Objetivo

Fornecer uma camada de dados consistente e escalável para dashboards e aplicações internas, com:

- ✅ **PostgreSQL** - Banco robusto sem limites de tamanho
- ✅ **Schemas Separados** - DTIC e SIS isolados
- ✅ **Sincronização em Tempo Real** - Máximo 15 segundos de delay
- ✅ **Campos Expandidos** - 50+ campos do GLPI (SLA, custos, localização, etc.)
- ✅ **API RESTful** - Endpoints limpos e bem documentados
- ✅ **Validação Automática** - Consistency check no startup

## 🏗️ Arquitetura

```
┌─────────────────┐    ┌──────────────────────┐    ┌─────────────────┐
│   GLPI Server   │◄──►│  GLPI Data Service   │◄──►│   Dashboards    │
│  (API REST)     │    │  (PostgreSQL/FastAPI)│    │  (React/Next)   │
└─────────────────┘    └──────────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │   PostgreSQL     │
                       │  ┌─────────────┐ │
                       │  │ dtic schema │ │
                       │  │ sis schema  │ │
                       │  └─────────────┘ │
                       └──────────────────┘
```

## 📋 Componentes

### 1. GLPI Client (`src/glpi_client/`)
- Autenticação com tokens GLPI
- Sincronização incremental com paginação
- Retry automático e tratamento de erros
- Suporte a múltiplos endpoints GLPI

### 2. ETL - Extract, Transform, Load (`src/etl/`)
- **Transformer**: Converte dados GLPI para formato interno
- **Sync**: Orquestra sincronização com controle de erros
- Derivação automática de departamentos por palavras-chave

### 3. Database (`src/db/`)
- SQLite nativo (evita problemas de compatibilidade)
- Tabelas: tickets, sync_meta, sync_errors
- Índices otimizados para consultas
- Operações de upsert para consistência

### 4. API (`src/api/`)
- FastAPI com documentação automática
- Endpoints RESTful com filtros e paginação
- CORS configurado para acesso cross-origin
- Modelos de dados tipados com Pydantic

## 🚀 Instalação e Configuração

### 1. Clone e instale dependências
```bash
cd 05-glpi-data-service
pip install -r requirements.txt
```

### 2. Configure as variáveis de ambiente
```bash
cp .env.example .env
# Edite .env com seus tokens GLPI
```

### 3. Inicialize o banco de dados
```bash
python init_db.py
```

### 4. Teste o serviço
```bash
# Teste completo
python test_service.py

# Teste da API
python test_api.py
```

## 📡 API Endpoints

### Health Check
```http
GET /health
```

### Listar Tickets
```http
GET /tickets?org=DTIC&status=NOVO&limit=50&offset=0
```

### Buscar Ticket Específico
```http
GET /tickets/{glpi_id}
```

### Estatísticas
```http
GET /stats?org=DTIC
```

### Departamentos
```http
GET /departments
```

### Status de Sincronização
```http
GET /sync/status
```

### Disparar Sincronização Manual
```http
POST /sync/trigger?full_sync=false
```

## 🔄 Sincronização

### Incremental (Padrão)
```bash
# Via código
from src.etl.sync import SyncOrchestrator
orchestrator = SyncOrchestrator('DTIC')
result = orchestrator.sync_tickets(full_sync=False)

# Via API
curl -X POST "http://localhost:8000/sync/trigger?full_sync=false"
```

### Completa
```bash
# Busca tickets dos últimos 365 dias
orchestrator.sync_tickets(full_sync=True)
```

## 🏢 Derivação de Departamentos

O serviço identifica automaticamente o departamento com base em:

1. **Nome da Entidade** (entities_id)
2. **Nome do Grupo** (groups_id)  
3. **Título e Descrição** (palavras-chave)
4. **Padrões de departamento**:
   - DTIC: tecnologia, informação, sistema, tic
   - MANUTENCAO: manutenção, conservação, predial
   - SECOM: comunicação, imprensa, mídia
   - FINANCEIRO: financeiro, orçamento, contabilidade
   - RH: recursos humanos, pessoal, funcionário
   - JURIDICO: jurídico, legal, processo

## 📊 Estrutura dos Dados

### Ticket
```json
{
  "id": 1,
  "glpi_id": 12345,
  "titulo": "Problema com impressora",
  "descricao": "Descrição detalhada...",
  "status": "ATRIBUIDO",
  "prioridade": "MEDIA",
  "org": "DTIC",
  "categoria": "Impressão",
  "entidade": "DTIC",
  "tecnico": "João Silva",
  "grupo": "Suporte Técnico",
  "requerente": "Maria Santos",
  "created_at": "2024-11-20T10:00:00",
  "updated_at": "2024-11-20T11:30:00",
  "solved_at": null,
  "closed_at": null,
  "url": "http://glpi/ticket.form.php?id=12345",
  "is_deleted": false
}
```

## 🔧 Configuração GLPI

### Obter Tokens
1. Acesse: Configuração > Geral > API
2. Crie um **App Token** (para a aplicação)
3. Crie um **User Token** (para o usuário)

### Permissões Necessárias
- Ler tickets (`ticket:read`)
- Ler entidades (`entity:read`)
- Ler grupos (`group:read`)

## 🚨 Tratamento de Erros

- **Retry automático**: 3 tentativas com backoff
- **Sessão renovada**: Automaticamente em caso de 401
- **Erros registrados**: Tabela `sync_errors` com contexto
- **Timeout configurável**: 30s por requisição, 1h limite total

## 📈 Performance

- **Paginação**: 50 tickets por lote (configurável)
- **Índices otimizados**: Por glpi_id, status, org, updated_at
- **Upsert eficiente**: Evita duplicatas
- **Cache de referência**: Entidades e grupos carregados uma vez

## 🔒 Segurança

- Tokens armazenados em variáveis de ambiente
- Sem exposição de credenciais no código
- CORS configurável
- Rate limiting implícito via intervalos de sincronização

## 🧪 Testes

```bash
# Teste unitário
python test_service.py

# Teste de API
python test_api.py

# Teste manual de endpoints
http://localhost:8000/docs  # Documentação Swagger
```

## 🚀 Deploy

### Produção com Docker (recomendado)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "-m", "uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Produção com Systemd
```ini
[Unit]
Description=GLPI Data Service
After=network.target

[Service]
Type=simple
User=glpi
WorkingDirectory=/opt/glpi-data-service
ExecStart=/usr/bin/python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

## 📚 Próximos Passos

- [ ] Adicionar autenticação JWT na API
- [ ] Implementar cache Redis para performance
- [ ] Adicionar métricas Prometheus
- [ ] Suporte a PostgreSQL
- [ ] Interface web para monitoramento
- [ ] Notificações de erro (email/Slack)
- [ ] Backup automático do banco

## 🤝 Contribuindo

1. Faça fork do projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT.
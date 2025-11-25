# Guia de Implementação: Agente DTIC Copilot Studio

## Visão Geral

Este guia fornece um roteiro passo-a-passo para implementar o agente analista de dados DTIC no Microsoft Copilot Studio.

## Pré-requisitos

- [ ] Acesso ao **Microsoft Copilot Studio** com permissões de criação de agente
- [ ] Acesso ao **Power Platform** (mesmo tenant)
- [ ] Credenciais OAuth 2.0 ou API Key para as APIs DTIC
- [ ] Especificação OpenAPI v2 (`dtic-analytics-connector.yaml`) pronta
- [ ] APIs backend implementadas e acessíveis via HTTPS

---

## Fase 1: Preparação do Backend

### 1.1 Implementar APIs Analytics

Baseado na [arquitetura de APIs](arquitetura-apis.md), implementar os seguintes endpoints:

- [ ] `GET /tickets/metrics` - Métricas agregadas
- [ ] `GET /tickets/trends` - Tendências temporais
- [ ] `GET /sla/compliance` - Conformidade com SLA
- [ ] `GET /technicians/performance` - Performance de técnicos
- [ ] `GET /tickets/by-category` - Distribuição por categoria

**Checklist por Endpoint:**
- [ ] Validação de parâmetros (datas, filtros)
- [ ] Agregação de dados (queries otimizadas)
- [ ] Cache (Redis recomendado, TTL 5 min)
- [ ] Tratamento de erros (retornar JSON estruturado)
- [ ] Logging e auditoria
- [ ] Testes unitários e de integração

### 1.2 Configurar Autenticação

**Opção 1: OAuth 2.0 (Recomendado)**
```bash
# Endpoint de token
POST https://api.dtic.rs.gov.br/oauth/token

# Configurar:
- grant_type: client_credentials
- client_id: {fornecido_pela_dtic}
- client_secret: {fornecido_pela_dtic}
- scope: analytics:read
```

**Opção 2: API Key**
```
X-API-Key: {chave_fornecida}
```

- [ ] Endpoint de autenticação configurado
- [ ] Credenciais geradas para Copilot Studio
- [ ] Rate limiting implementado (100 req/min)

### 1.3 Gerar e Validar OpenAPI v2

- [ ] Usar ferramenta de conversão se necessário (v3 → v2)
- [ ] Validar spec com [Swagger Editor](https://editor.swagger.io/)
- [ ] Garantir descrições claras em todos os `operationId`
- [ ] Testar endpoints manualmente (Postman/Insomnia)

---

## Fase 2: Configurar Custom Connector

### 2.1 Acessar Copilot Studio

1. Acessar [https://copilotstudio.microsoft.com/](https://copilotstudio.microsoft.com/)
2. Selecionar ambiente correto (produção/desenvolvimento)
3. Criar novo agente ou usar existente

### 2.2 Importar Custom Connector

**Passo a Passo:**

1. No menu lateral, ir em **Settings** → **Security** → **Authentication** (se necessário configurar primeiro)
2. No menu **Tools**, clicar em **+ Add a tool**
3. Selecionar **Custom Connector** → **Create from blank**
4. Nomear: `DTIC Analytics Connector`
5. Em **Connector Configuration:**
   - Upload do arquivo `dtic-analytics-connector.yaml`
   - Aguardar processamento
   - Revisar ações importadas (devem aparecer 5 ações)

**Checklist:**
- [ ] Arquivo OpenAPI importado com sucesso
- [ ] 5 ações aparecem:
  - [ ] `getTicketsMetrics`
  - [ ] `getTicketsTrends`
  - [ ] `getSLACompliance`
  - [ ] `getTechnicianPerformance`
  - [ ] `getTicketsByCategory`

### 2.3 Configurar Autenticação no Connector

**Para OAuth 2.0:**
1. Em **Security**, selecionar **OAuth 2.0**
2. Configurar:
   - **Identity Provider:** Custom
   - **Client ID:** `{seu_client_id}`
   - **Client Secret:** `{seu_client_secret}` (usar secret value)
   - **Authorization URL:** (se aplicável)
   - **Token URL:** `https://api.dtic.rs.gov.br/oauth/token`
   - **Refresh URL:** (se aplicável)
   - **Scope:** `analytics:read`

**Para API Key:**
1. Em **Security**, selecionar **API Key**
2. Configurar:
   - **Parameter Location:** Header
   - **Parameter Name:** `X-API-Key`
   - **Value:** `{sua_api_key}`

- [ ] Autenticação configurada
- [ ] Testar conexão (Test → Run test)

### 2.4 Validar Ações Individuais

Para cada ação, testar no Copilot Studio:

**Exemplo: `getTicketsMetrics`**
1. Ir em **Tools** → **DTIC Analytics Connector** → **getTicketsMetrics**
2. Preencher parâmetros de teste:
   - `start_date`: `2025-11-01`
   - `end_date`: `2025-11-30`
3. Clicar em **Test**
4. Verificar resposta JSON

- [ ] `getTicketsMetrics` testado
- [ ] `getTicketsTrends` testado
- [ ] `getSLACompliance` testado
- [ ] `getTechnicianPerformance` testado
- [ ] `getTicketsByCategory` testado

---

## Fase 3: Criar Estrutura de Topics

### 3.1 Configurar Variáveis Globais

**No Copilot Studio:**
1. Ir em **Topics** → **Variables** → **Global Variables**
2. Criar as seguintes variáveis:

| Nome | Tipo | Valor Inicial | Descrição |
|------|------|---------------|-----------|
| `selected_start_date` | Date | (vazio) | Data início do período |
| `selected_end_date` | Date | (vazio) | Data fim do período |
| `selected_period_label` | String | (vazio) | Label do período (ex: "Novembro 2025") |
| `last_metrics_dtic` | Object | (vazio) | Cache de últimas métricas |
| `last_sla_data` | Object | (vazio) | Cache de dados SLA |
| `cache_timestamp` | DateTime | (vazio) | Quando cache foi carregado |

- [ ] Variáveis globais criadas

### 3.2 Configurar Topic: Conversation Start

**Objetivo:** Inicializar contexto e carregar período padrão.

**Fluxo:**
1. **Message node:** "Olá! Sou o assistente de análise DTIC. Posso ajudar com métricas de tickets, SLA e performance."
2. **Set variable:** `selected_period_label` = "Mês corrente"
3. **Set variable:** `selected_start_date` = Power Fx: `DateAdd(Today(), -Day(Today()) + 1, Days)` (primeiro dia do mês)
4. **Set variable:** `selected_end_date` = Power Fx: `Today()` (hoje)

- [ ] Topic "Conversation Start" configurado
- [ ] Período padrão inicializado

### 3.3 Criar Topic: Analytics Request (Principal)

**Objetivo:** Topic principal que recebe perguntas e roteia para análises específicas.

**Trigger Phrases:**
- "Quantos tickets"
- "Como está o SLA"
- "Mostrar métricas"
- "Performance dos técnicos"
- "Tendências"

**Fluxo:**
1. **Question node:** "O que você gostaria de analisar?" (se trigger vago)
2. **Condition branches:**
   - Se menção a "SLA" → Redirect to "SLA Analysis"
   - Se menção a "técnico/performance" → Redirect to "Technician Performance"
   - Se menção a "tendência/evolução" → Redirect to "Trend Analysis"
   - Padrão → Redirect to "Metrics Analysis"

- [ ] Topic criado
- [ ] Trigger phrases configuradas
- [ ] Condições de roteamento implementadas

### 3.4 Criar Topic: Metrics Analysis

**Fluxo:**
1. **Condition:** Verificar se `cache_timestamp` existe e < 5 min
   - Se sim: usar `last_metrics_dtic`
   - Se não: ir para passo 2
2. **Call an action:** `getTicketsMetrics`
   - Inputs:
     - `start_date`: `{selected_start_date}`
     - `end_date`: `{selected_end_date}`
   - Output: salvar em variável `metricsResponse`
3. **Set variable:** `last_metrics_dtic` = `{metricsResponse}`
4. **Set variable:** `cache_timestamp` = Power Fx: `Now()`
5. **Create generative answers:**
   - System Instructions: (copiar do `prompts/analise-templates.md` → "System Prompt Principal" + "Análise de Métricas")
   - Prompt: "Analise as seguintes métricas: {last_metrics_dtic}"
   - Data sources: `{last_metrics_dtic}`
6. **Message node:** Exibir resposta gerada

- [ ] Topic criado
- [ ] Lógica de cache implementada
- [ ] Prompt de análise configurado

### 3.5 Criar Topic: SLA Analysis

**Similar ao anterior, mas:**
- **Call an action:** `getSLACompliance`
- **Salvar em:** `last_sla_data`
- **Prompt:** Template de "Análise de SLA"

- [ ] Topic criado
- [ ] Prompt SLA configurado

### 3.6 Criar Topic: Technician Performance

- **Call an action:** `getTechnicianPerformance`
- **Prompt:** Template de "Análise de Técnicos"

- [ ] Topic criado

### 3.7 Criar Topic: Trend Analysis

- **Call an action:** `getTicketsTrends`
- **Params:** `granularity` = "week"
- **Prompt:** Template de "Análise de Tendências"

- [ ] Topic criado

### 3.8 Criar Topic Utilitário: Context Reset

**Trigger:** "/reset" ou "limpar contexto"

**Fluxo:**
1. **Set variable:** `last_metrics_dtic` = (clear)
2. **Set variable:** `last_sla_data` = (clear)
3. **Set variable:** `cache_timestamp` = (clear)
4. **Message:** "Contexto limpo. Inicializando novamente..."
5. **Redirect to:** "Conversation Start"

- [ ] Topic criado

---

## Fase 4: Configurar Prompts de Análise

### 4.1 Criar Generative Answers Nodes

Para cada topic de análise, configurar nó "Create generative answers":

**Configuração Padrão:**
```
System Instructions:
{copiar de prompts/analise-templates.md}

Knowledge Sources:
- None (usar apenas dados de APIs)

Content Moderation:
- Medium

Response Length:
- Long (para análises detalhadas)
```

- [ ] Prompts configurados em todos os topics
- [ ] Templates testados com dados reais

### 4.2 Ajustar Tone e Style

No nível do agente:
1. **Settings** → **Generative AI** → **Content moderation:** Medium
2. **Settings** → **Generative AI** → **How should your agent respond?**
   - Tom: Profissional e executivo
   - Estilo: Objetivo e direto
   - Formato: Usar tabelas e listas quando apropriado

- [ ] Tone configurado

---

## Fase 5: Testes e Validação

### 5.1 Testes Unitários (Por Topic)

**Para cada topic:**
- [ ] Testar com período válido
- [ ] Testar com período inválido (esperar erro)
- [ ] Testar cache (segunda chamada deve reusar dados)
- [ ] Testar reset de contexto

**Exemplos de Perguntas:**
- "Quantos tickets tivemos em novembro?"
- "Como está o SLA?"
- "Quem são os melhores técnicos?"
- "Mostre a evolução dos tickets"

### 5.2 Testes de Integração

**Fluxo completo:**
1. Iniciar conversa → "Conversation Start"
2. Perguntar sobre métricas → verificar chamada de API
3. Perguntar segund vez → verificar uso de cache
4. Perguntar sobre SLA → verificar nova chamada de API
5. Resetar contexto → verificar limpeza

- [ ] Fluxo completo testado
- [ ] Cache funcionando corretamente
- [ ] Orquestração multi-API validada

### 5.3 Testes de Limites

- [ ] Payload grande (verificar < 28KB)
- [ ] Timeout de API (verificar tratamento de erro)
- [ ] Dados ausentes (verificar respostas apropriadas)
- [ ] Token limit (verificar contexto não estoura)

### 5.4 Testes com Usuários Reais

- [ ] Sessão com diretor/gestor DTIC
- [ ] Coletar feedback sobre:
  - Clareza das respostas
  - Relevância dos insights
  - Facilidade de uso
  - Sugestões de melhoria

---

## Fase 6: Deploy e Monitoramento

### 6.1 Publicar Agente

1. No Copilot Studio, clicar em **Publish**
2. Selecionar canal:
   - **Microsoft Teams** (recomendado para usuários internos)
   - **Web** (para acesso externo)
   - **Power Apps**
3. Configurar permissões de acesso

- [ ] Agente publicado
- [ ] Canal configurado (Teams/Web)

### 6.2 Configurar Monitoramento

**Analytics do Copilot Studio:**
1. **Analytics** → **Conversations**
   - Monitorar volume de conversas
   - Taxa de resolução
   - Tópicos mais acionados

2. **Analytics** → **Performance**
   - Tempo de resposta
   - Taxa de erro
   - Satisfação do usuário

**External Monitoring (opcional):**
- [ ] Application Insights configurado
- [ ] Logs de erro sendo capturados

### 6.3 Documentar para Usuários

Criar guia de uso:
- [ ] Exemplos de perguntas comuns
- [ ] Comandos especiais (/reset)
- [ ] Limitações conhecidas
- [ ] Contato para suporte

---

## Checklist Final

### Backend
- [ ] APIs implementadas e testadas
- [ ] Autenticação configurada (OAuth 2.0 ou API Key)
- [ ] Cache implementado (5 min)
- [ ] Rate limiting ativo (100 req/min)
- [ ] Especificação OpenAPI v2 validada

### Copilot Studio
- [ ] Custom connector importado
- [ ] 5 ações funcionando
- [ ] Variáveis globais criadas
- [ ] 7 topics implementados:
  - [ ] Conversation Start
  - [ ] Analytics Request (principal)
  - [ ] Metrics Analysis
  - [ ] SLA Analysis
  - [ ] Technician Performance
  - [ ] Trend Analysis
  - [ ] Context Reset
- [ ] Prompts de análise configurados

### Testes
- [ ] Testes unitários por topic
- [ ] Testes de integração (fluxo completo)
- [ ] Testes de limites (payload, timeout, token)
- [ ] Testes com usuários reais

### Deploy
- [ ] Agente publicado
- [ ] Canal configurado (Teams/Web)
- [ ] Monitoramento ativo
- [ ] Documentação de usuário criada

---

## Próximos Passos (Melhorias Futuras)

- [ ] Implementar comparação de períodos (automática)
- [ ] Adicionar gráficos via Adaptive Cards
- [ ] Integração com Power BI para visualizações
- [ ] Alertas proativos (SLA < 85%)
- [ ] Multi-agente (SIS + DTIC combinados)
- [ ] Análise preditiva com ML

---

**Tempo Estimado de Implementação:**
- Fase 1 (Backend): 3-5 dias
- Fase 2 (Connector): 1 dia
- Fase 3-4 (Topics + Prompts): 2-3 dias
- Fase 5 (Testes): 2 dias
- Fase 6 (Deploy): 1 dia

**Total: 9-12 dias úteis** (1 pessoa, tempo integral)

---

**Em caso de dúvidas, consulte:**
- [Blueprint Conceitual](blueprint-conceitual.md)
- [Arquitetura de APIs](arquitetura-apis.md)
- [Templates de Prompts](../prompts/analise-templates.md)
- [Referências Oficiais Microsoft](../referencias.md)

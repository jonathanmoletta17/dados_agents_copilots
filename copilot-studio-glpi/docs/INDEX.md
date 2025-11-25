# Índice da Documentação - Projeto Copilot Studio DTIC

## 📚 Ordem de Leitura Recomendada

### 1. Início Rápido
- [README.md](../README.md) - Visão geral do projeto, objetivos e estrutura

### 2. Compreensão Conceitual
- [blueprint-conceitual.md](blueprint-conceitual.md) - Arquitetura geral, fluxos e estratégias
- [arquitetura-apis.md](arquitetura-apis.md) - Especificação detalhada dos 5 endpoints analytics

### 3. Implementação Técnica
- [guia-implementacao.md](guia-implementacao.md) - Passo-a-passo completo de implementação
- [../openapi/dtic-analytics-connector.yaml](../openapi/dtic-analytics-connector.yaml) - Especificação OpenAPI v2
- [../prompts/analise-templates.md](../prompts/analise-templates.md) - Templates de prompts para análises

### 4. Materiais de Apoio
- [../referencias.md](../referencias.md) - Links para documentação oficial Microsoft
- [../guia-analitico-copilot-studio.md](../guia-analitico-copilot-studio.md) - Guia técnico original

---

## 📋 Checklists por Fase

### Fase 1: Backend (APIs)
Consulte: [arquitetura-apis.md](arquitetura-apis.md)
- [ ] Implementar 5 endpoints analytics
- [ ] Configurar autenticação OAuth 2.0
- [ ] Implementar cache (5 min)
- [ ] Validar OpenAPI v2

### Fase 2: Custom Connector
Consulte: [guia-implementacao.md](guia-implementacao.md#fase-2-configurar-custom-connector)
- [ ] Importar especificação no Copilot Studio
- [ ] Configurar autenticação
- [ ] Testar 5 ações individualmente

### Fase 3: Topics e Prompts
Consulte: [guia-implementacao.md](guia-implementacao.md#fase-3-criar-estrutura-de-topics)
- [ ] Criar 7 topics (Conversation Start + 6 análises)
- [ ] Configurar variáveis globais
- [ ] Implementar prompts de análise

### Fase 4: Testes
Consulte: [guia-implementacao.md](guia-implementacao.md#fase-5-testes-e-validação)
- [ ] Testes unitários por topic
- [ ] Testes de integração
- [ ] Testes com usuários reais

### Fase 5: Deploy
Consulte: [guia-implementacao.md](guia-implementacao.md#fase-6-deploy-e-monitoramento)
- [ ] Publicar agente
- [ ] Configurar canal (Teams/Web)
- [ ] Ativar monitoramento

---

## 🎯 Documentos por Persona

### Para **Desenvolvedores Backend**
1. [arquitetura-apis.md](arquitetura-apis.md) - Especificação completa de endpoints
2. [../openapi/dtic-analytics-connector.yaml](../openapi/dtic-analytics-connector.yaml) - Contrato OpenAPI

### Para **Desenvolvedores Copilot Studio**
1. [blueprint-conceitual.md](blueprint-conceitual.md) - Arquitetura de topics e fluxos
2. [guia-implementacao.md](guia-implementacao.md) - Passo-a-passo de configuração
3. [../prompts/analise-templates.md](../prompts/analise-templates.md) - Templates de prompts

### Para **Gestores/Product Owners**
1. [README.md](../README.md) - Visão geral e objetivos
2. [blueprint-conceitual.md](blueprint-conceitual.md#fluxos-de-análise) - Exemplos de uso
3. [guia-implementacao.md](guia-implementacao.md#checklist-final) - Estimativas de tempo

### Para **Analistas de Dados**
1. [arquitetura-apis.md](arquitetura-apis.md#especificação-de-dados) - Estrutura de dados
2. [../prompts/analise-templates.md](../prompts/analise-templates.md) - Tipos de análise disponíveis

---

## 🔗 Referências Rápidas

### Endpoints da API
- `GET /tickets/metrics` - Métricas agregadas ([doc](arquitetura-apis.md#1-get-ticketsmetrics))
- `GET /tickets/trends` - Tendências temporais ([doc](arquitetura-apis.md#2-get-ticketstrends))
- `GET /sla/compliance` - Conformidade SLA ([doc](arquitetura-apis.md#3-get-slacompliance))
- `GET /technicians/performance` - Performance técnicos ([doc](arquitetura-apis.md#4-get-techniciansperformance))
- `GET /tickets/by-category` - Distribuição categorias ([doc](arquitetura-apis.md#5-get-ticketsby-category))

### Topics do Copilot Studio
- **Conversation Start** ([doc](guia-implementacao.md#32-configurar-topic-conversation-start))
- **Analytics Request** ([doc](guia-implementacao.md#33-criar-topic-analytics-request-principal))
- **Metrics Analysis** ([doc](guia-implementacao.md#34-criar-topic-metrics-analysis))
- **SLA Analysis** ([doc](guia-implementacao.md#35-criar-topic-sla-analysis))
- **Technician Performance** ([doc](guia-implementacao.md#36-criar-topic-technician-performance))
- **Trend Analysis** ([doc](guia-implementacao.md#37-criar-topic-trend-analysis))
- **Context Reset** ([doc](guia-implementacao.md#38-criar-topic-utilitário-context-reset))

### Variáveis Globais
- `selected_start_date` - Data início período
- `selected_end_date` - Data fim período
- `selected_period_label` - Label do período
- `last_metrics_dtic` - Cache de métricas
- `last_sla_data` - Cache de SLA
- `cache_timestamp` - Timestamp do cache

([ver todas](guia-implementacao.md#31-configurar-variáveis-globais))

---

## 📞 Suporte

**Dúvidas Técnicas:**
- Consulte [referencias.md](../referencias.md) para links oficiais Microsoft
- Revise o [guia de implementação](guia-implementacao.md)

**Feedback do Projeto:**
- Registre issues ou sugestões com a equipe DTIC

---

**Última atualização:** 2025-11-25

# Agente Copilot Studio para Análise DTIC/GLPI

> **Projeto de agente analítico inteligente para análise de dados do GLPI DTIC, construído com Microsoft Copilot Studio**

## 📋 Visão Geral

Este projeto implementa um agente conversacional capaz de:
- **Entender perguntas** de usuários (diretores, gestores) sobre dados do GLPI DTIC
- **Descobrir fontes de dados** necessárias (APIs internas do GLPI)
- **Buscar dados sob demanda** via custom connectors
- **Realizar análises** (métricas, comparações, tendências, insights)

## 🎯 Objetivo

Permitir que gestores da DTIC obtenham insights e análises de tickets, usuários e métricas do GLPI através de **conversação natural**, sem necessidade de acessar dashboards ou executar queries manualmente.

## 📂 Estrutura do Projeto

```
copilot-studio-glpi/
├── README.md                           # Este arquivo
├── docs/
│   ├── blueprint-conceitual.md         # Blueprint de alto nível
│   ├── arquitetura-apis.md             # Estrutura das APIs analytics
│   ├── custom-connectors.md            # Documentação de conectores
│   ├── prompts-analise.md              # Templates de prompts
│   └── guia-implementacao.md           # Passo-a-passo de implementação
├── openapi/
│   ├── dtic-analytics-connector.yaml   # Spec OpenAPI v2 do conector
│   └── exemplos-payloads.json          # Exemplos de request/response
├── prompts/
│   ├── system-prompts.md               # Instruções de sistema
│   ├── analise-metricas.md             # Prompts para métricas
│   ├── analise-comparacao.md           # Prompts para comparações
│   └── analise-trends.md               # Prompts para tendências
├── topics/
│   ├── estrutura-topics.md             # Organização de tópicos
│   └── variaveis-contexto.md           # Definição de variáveis
├── referencias.md                       # Links oficiais Microsoft
└── guia-analitico-copilot-studio.md   # Guia técnico original
```

## 🚀 Funcionalidades Principais

### 1. Análise de Métricas (KPIs)
- Total de tickets por período
- Taxa de conformidade com SLA
- Tempo médio de resolução
- Distribuição por prioridade/categoria/status

### 2. Comparações Temporais
- Mês atual vs mês anterior
- Identificação de variações significativas
- Análise de tendências (crescimento/queda)

### 3. Rankings e Outliers
- Top técnicos por tickets resolvidos
- Identificação de gargalos
- Detecção de valores anormais

### 4. Análise de Tendências
- Séries temporais de tickets
- Sazonalidade e picos
- Previsões simples baseadas em tendências

## 🔧 Tecnologias Utilizadas

- **Microsoft Copilot Studio** - Plataforma de agente conversacional
- **Custom Connectors** - Integração com APIs GLPI
- **OpenAPI v2** - Especificação de APIs
- **Power Automate** (opcional) - Fluxos complexos
- **Azure OpenAI / GPT-4o** - Modelo de linguagem

## 📊 Limitações Técnicas

| Limite | Valor | Impacto |
|--------|-------|---------|
| Mensagem (Omnichannel) | 28KB | APIs retornam dados agregados |
| Upload Knowledge Base | 512MB | Documentação de referência |
| Contexto de Análise | ~300 páginas | Usar resumos estatísticos |
| Contexto de Reescrita | ~3,000 palavras | Limitar JSON em prompts |
| Token Window (GPT-4o) | 128K in / 16K out | Gerenciar contexto ativamente |

## 📖 Documentação

### Para Começar
1. Leia o [Blueprint Conceitual](docs/blueprint-conceitual.md) para entender a arquitetura
2. Revise a [Arquitetura de APIs](docs/arquitetura-apis.md) para estruturar endpoints
3. Consulte o [Guia de Implementação](docs/guia-implementacao.md) para passo-a-passo

### Referências Técnicas
- [Custom Connectors](docs/custom-connectors.md) - Como criar e configurar conectores
- [Prompts de Análise](docs/prompts-analise.md) - Templates de prompts para diferentes análises
- [Referências Oficiais](referencias.md) - Links para documentação Microsoft

## 🎨 Exemplo de Uso

**Usuário:** "Quantos tickets tivemos na DTIC no último mês?"

**Agente:**
> **Análise de Tickets - Novembro 2025**
> 
> | Métrica | Valor |
> |---------|-------|
> | Total de Tickets | 842 |
> | Abertos | 132 |
> | Fechados | 710 |
> | SLA Compliance | 87% ⚠️ |
> 
> **Insights:**
> - O SLA está **3% abaixo da meta de 90%** - recomendo priorizar tickets antigos
> - Taxa de resolução: 84% (710 de 842 tickets resolvidos)

## 🔐 Segurança e Governança

- Autenticação via **OAuth 2.0** ou **API Key**
- Tokens/credenciais apenas em conectores (nunca em variáveis do bot)
- Respeito a políticas organizacionais (identity access, conditional access)
- Dados sensíveis não persistidos em variáveis de conversação

## 🛠️ Próximos Passos

### Fase 1: Backend (APIs)
- [ ] Criar endpoints `/api/v1/analytics/dtic/tickets/metrics`
- [ ] Implementar filtros por período/entidade
- [ ] Gerar especificação OpenAPI v2

### Fase 2: Custom Connectors
- [ ] Importar OpenAPI no Copilot Studio
- [ ] Configurar autenticação
- [ ] Testar ações individuais

### Fase 3: Agente
- [ ] Criar topics de análise
- [ ] Configurar variáveis globais
- [ ] Implementar prompts de análise
- [ ] Testar orquestração multi-API

## 📚 Recursos Adicionais

- [Microsoft Copilot Studio Documentation](https://learn.microsoft.com/microsoft-copilot-studio/)
- [Power Platform Connectors](https://learn.microsoft.com/connectors/)
- [Azure OpenAI Service](https://learn.microsoft.com/azure/ai-services/openai/)

## 📝 Licença

Projeto interno - Governo do Estado do Rio Grande do Sul / DTIC

---

**Versão:** 1.0.0  
**Última atualização:** 2025-11-25  
**Autor:** Equipe DTIC

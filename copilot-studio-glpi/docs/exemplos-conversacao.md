# Exemplos Práticos de Conversação

## Cenário 1: Consulta Rápida de Métricas

### Conversa

**👤 Usuário:** "Quantos tickets tivemos este mês?"

**🤖 Agente:**
> **842 tickets** no período de 01/11 a 30/11/2025.
> 
> | Métrica | Valor |
> |---------|-------|
> | Total | 842 |
> | Abertos | 132 |
> | Fechados | 710 |
> | Taxa de Resolução | 84.3% |
> 
> O SLA está em **87.5%** (⚠️ 2.5% abaixo da meta).

### Fluxo Técnico
1. Topic: **Analytics Request** identifica menção a "tickets"
2. Redireciona para: **Metrics Analysis**
3. Chama API: `getTicketsMetrics(start_date=2025-11-01, end_date=2025-11-30)`
4. Armazena em: `last_metrics_dtic`
5. Prompt: "Análise de Métricas"
6. Retorna resposta formatada

---

## Cenário 2: Análise de SLA

### Conversa

**👤 Usuário:** "Como está o SLA?"

**🤖 Agente:**
> **Status Geral do SLA:**
> A taxa de conformidade está em **87.5% (⚠️ abaixo da meta de 90%)**. 105 violações registradas.
> 
> | Prioridade | SLA | Meta | Violações |
> |------------|-----|------|-----------|
> | Crítica | 91.7% | 95% | 1 ⚠️ |
> | Alta | 85.9% | 90% | 12 ❌ |
> | Média | 88.3% | 90% | 38 ⚠️ |
> | Baixa | 87.2% | 85% | 54 ✅ |
> 
> **Recomendações:**
> - Priorizar tickets de alta prioridade (12 violações)
> - Reforçar equipe de software (pior SLA: 85.6%)

### Fluxo Técnico
1. Topic: **Analytics Request** identifica menção a "SLA"
2. Redireciona para: **SLA Analysis**
3. Chama API: `getSLACompliance(start_date=..., end_date=..., include_violations=false)`
4. Armazena em: `last_sla_data`
5. Prompt: "Análise de SLA"
6. Retorna análise com recomendações

---

## Cenário 3: Ranking de Técnicos

### Conversa

**👤 Usuário:** "Quem são os melhores técnicos este mês?"

**🤖 Agente:**
> **Ranking de Técnicos - Novembro 2025**
> 
> | Técnico | Resolvidos | Taxa | Tempo Médio | SLA |
> |---------|------------|------|-------------|-----|
> | ⭐ Maria Santos | 48/52 | 92.3% | 18.7h | 94.2% |
> | João Silva | 38/45 | 84.4% | 22.3h | 89.5% |
> | Pedro Costa | 35/42 | 83.3% | 24.1h | 88.7% |
> 
> **Destaques:**
> - **Maria Santos** lidera com 92.3% de taxa de resolução (5.6pp acima da média)
> - Tempo médio 9.8h mais rápido que a média do time
> - SLA de 94.2% (melhor do time)

### Fluxo Técnico
1. Topic: **Analytics Request** identifica "técnicos" ou "melhores"
2. Redireciona para: **Technician Performance**
3. Chama API: `getTechnicianPerformance(start_date=..., end_date=..., top_n=10)`
4. Prompt: "Análise de Técnicos"
5. Retorna ranking + insights

---

## Cenário 4: Comparação de Períodos

### Conversa

**👤 Usuário:** "Compare este mês com o anterior"

**🤖 Agente:**
> **Comparação: Novembro vs Outubro 2025**
> 
> | Métrica | Nov | Out | Variação |
> |---------|-----|-----|----------|
> | Total Tickets | 842 | 756 | +11.4% 📈 |
> | SLA | 87.5% | 89.3% | -1.8pp 📉 |
> | Tempo Médio | 28.5h | 26.1h | +9.2% 📉 |
> 
> **Tendências:**
> - 📈 Demanda cresceu 11.4% (86 tickets a mais)
> - 📉 SLA caiu 1.8 pontos percentuais
> - 📉 Tempo de resolução aumentou 2.4h
> 
> **Recomendação:** Reforçar equipe para lidar com aumento de demanda.

### Fluxo Técnico
1. Topic: **Analytics Request** identifica "comparar"
2. Redireciona para: **Metrics Analysis** (modificado para comparação)
3. Chama API 2x:
   - `getTicketsMetrics(start_date=2025-11-01, end_date=2025-11-30)` (atual)
   - `getTicketsMetrics(start_date=2025-10-01, end_date=2025-10-31)` (anterior)
4. Prompt: "Comparação de Períodos"
5. Retorna análise de variações

---

## Cenário 5: Análise de Tendências

### Conversa

**👤 Usuário:** "Mostre a evolução dos tickets nas últimas 8 semanas"

**🤖 Agente:**
> **Análise de Tendências - Outubro a Novembro 2025**
> 
> **Tendência Geral: 📈 Crescente (+8.6%)**
> 
> A demanda passou de 187 tickets/semana (início Out) para 203 tickets/semana (fim Nov).
> 
> **Sazonalidade:**
> - Picos às **segundas-feiras** (42 tickets, +23% da média)
> - Vale às **sextas-feiras** (28 tickets, -18% da média)
> 
> **Anomalia Detectada:**
> - **15 de novembro:** 67 tickets (2.3x acima do normal) - investigar causa
> 
> **Previsão Dezembro:**
> Se tendência continuar: **~920 tickets** (+9% vs novembro)

### Fluxo Técnico
1. Topic: **Analytics Request** identifica "tendências" ou "evolução"
2. Redireciona para: **Trend Analysis**
3. Chama API: `getTicketsTrends(start_date=2025-10-01, end_date=2025-11-30, granularity=week)`
4. Prompt: "Análise de Tendências"
5. Retorna série temporal + insights + previsão

---

## Cenário 6: Reutilização de Cache

### Conversa

**👤 Usuário:** "Quantos tickets tivemos?"  
**🤖 Agente:** [Retorna 842 tickets + métricas completas]

**👤 Usuário:** "E qual foi o SLA?"  
**🤖 Agente:** "Dentro das métricas já carregadas: SLA de **87.5%** (⚠️ abaixo da meta)."

### Fluxo Técnico
1. Primeira pergunta: Chama API `getTicketsMetrics`, armazena em `last_metrics_dtic`
2. Segunda pergunta: **Não chama API novamente**, usa `last_metrics_dtic.sla.compliance_percent`
3. Economia: 1 chamada de API evitada
4. Performance: Resposta instantânea

---

## Cenário 7: Reset de Contexto

### Conversa

**👤 Usuário:** "Agora quero ver dados de outubro"  
**🤖 Agente:** [Detecta mudança de período]  
"Entendido. Configurando período para outubro 2025..."  
[Limpa cache, atualiza variáveis de período]  
"Pronto! O que você gostaria de analisar sobre outubro?"

**Ou via comando:**

**👤 Usuário:** "/reset"  
**🤖 Agente:** "Contexto limpo. Inicializando novamente com período padrão (mês corrente)."

### Fluxo Técnico
- Usuário muda período ou usa `/reset`
- Topic: **Context Reset**
- Limpa: `last_metrics_dtic`, `last_sla_data`, `cache_timestamp`
- Reseta variáveis de período
- Reinicializa com "Conversation Start"

---

## Cenário 8: Pergunta Composta (Multi-API)

### Conversa

**👤 Usuário:** "Compare o SLA da DTIC com a performance dos técnicos"

**🤖 Agente:**
> **Análise Integrada: SLA vs Performance de Técnicos**
> 
> **SLA Geral:** 87.5% (⚠️ abaixo da meta de 90%)
> 
> **Correlação com Performance:**
> - Técnicos com SLA > 90%: Maria Santos (94.2%), Ana Lima (91.3%)  
>   → Média de resolução: 19.2h
> - Técnicos com SLA < 85%: Carlos Mendes (78.3%), Roberto Alves (82.1%)  
>   → Média de resolução: 35.7h
> 
> **Insight:** Técnicos de alto SLA resolvem tickets **45% mais rápido** que técnicos com SLA baixo.
> 
> **Recomendação:** Mentoria de Maria Santos para Carlos Mendes pode elevar SLA geral.

### Fluxo Técnico
1. Agente identifica necessidade de **2 APIs**
2. Orquestra chamadas:
   - `getSLACompliance()`
   - `getTechnicianPerformance()`
3. Prompt: "Análise Cruzada" (combina ambos JSONs)
4. Retorna insights correlacionados

---

## Cenário 9: Tratamento de Erro

### Conversa

**👤 Usuário:** "Quantos tickets tivemos de 01/12 a 30/11?"  
(Data inválida: início depois do fim)

**🤖 Agente:**
> ⚠️ **Erro:** A data de início (01/12) deve ser anterior à data de fim (30/11).
> 
> Por favor, forneça um período válido. Exemplo:
> - "Tickets de novembro"
> - "Tickets dos últimos 30 dias"
> - "Tickets de 01/11 a 30/11"

### Fluxo Técnico
1. API retorna erro 400: `INVALID_DATE_RANGE`
2. Topic captura erro
3. Responde com mensagem clara ao usuário
4. Sugere correção

---

## Cenário 10: Pergunta Ambígua → Clarificação

### Conversa

**👤 Usuário:** "Mostre os dados"

**🤖 Agente:**
> Claro! Qual análise você gostaria de ver?
> 
> 1. **Métricas gerais** (total de tickets, SLA, tempo médio)
> 2. **Análise de SLA** (conformidade por prioridade/categoria)
> 3. **Performance de técnicos** (ranking e estatísticas)
> 4. **Tendências** (evolução ao longo do tempo)
> 
> Ou me diga especificamente o que você precisa!

**👤 Usuário:** "Performance dos técnicos"

**🤖 Agente:** [Retorna ranking de técnicos]

### Fluxo Técnico
1. Trigger vago → Topic: **Analytics Request**
2. Condição: nenhuma palavra-chave específica
3. Question node: solicita clarificação
4. Após resposta, redireciona para topic apropriado

---

## Perguntas de Exemplo para Testar

### ✅ Métricas Gerais
- "Quantos tickets tivemos este mês?"
- "Como está a taxa de resolução?"
- "Mostre as métricas de novembro"
- "Quantos tickets estão abertos?"

### ✅ SLA
- "Como está o SLA?"
- "Qual a taxa de conformidade com SLA?"
- "Temos muitas violações de SLA?"
- "SLA por prioridade"

### ✅ Técnicos
- "Quem são os melhores técnicos?"
- "Ranking de performance"
- "Qual técnico resolveu mais tickets?"
- "Performance da equipe"

### ✅ Tendências
- "Mostre a evolução dos tickets"
- "Tendências das últimas semanas"
- "Estamos crescendo ou caindo?"
- "Há algum padrão semanal?"

### ✅ Comparações
- "Compare este mês com o anterior"
- "Melhoramos em relação a outubro?"
- "Variação mês a mês"

### ✅ Categorias
- "Quais categorias têm mais tickets?"
- "Distribuição por tipo de demanda"
- "SLA de software vs hardware"

### ✅ Compostas
- "Compare SLA com performance dos técnicos"
- "Mostre métricas e tendências"
- "Análise completa de novembro"

---

**Use estes exemplos para validar a implementação do agente!**

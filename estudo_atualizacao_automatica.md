# Estudo de Atualização Automática e Arquitetura de Dados

Este documento apresenta o diagnóstico, mapeamento e planejamento para implementação de atualização automática de dados nos frontends do ecossistema, com foco no problema do **Dashboard de Carregadores**.

---

## 1. Diagnóstico: Por que o Dashboard de Carregadores não atualiza?

**Sintoma:** O dashboard possui lógica de atualização automática, mas os dados não mudam na tela a menos que o usuário faça um refresh manual (F5).

**Causa Identificada:**
O código **já possui** um mecanismo de polling implementado via `setInterval` a cada 30 segundos em dois pontos principais:
1. `App.tsx`: Atualiza listas e rankings.
2. `CarregadoresKanban.tsx`: Atualiza as colunas do Kanban.

**O Problema Real (Hipótese de Cache):**
A implementação atual utiliza `fetch` nativo sem controle de cache.
```typescript
// Exemplo atual em services/api.ts
const response = await fetch(url);
```
Navegadores modernos tendem a cachear requisições GET agressivamente. Quando o `setInterval` dispara a função `loadData` novamente, o navegador provavelmente está retornando a **mesma resposta cacheada** da primeira requisição, sem nem bater no backend. O React recebe os mesmos dados, o `setState` não detecta mudança, e a tela não renderiza nada novo.

**Veredito:** O mecanismo existe, mas é ingênuo. Falta invalidação de cache (ex: headers `Cache-Control: no-cache` ou timestamp na URL) ou uso de uma biblioteca de data fetching robusta.

---

## 2. Inventário de Mecanismos de Atualização Existentes

Mapeamento de como cada projeto lida com atualização de dados hoje:

| Projeto | Componente/Hook | Estratégia | Intervalo | Observação |
|---------|----------------|------------|-----------|------------|
| **06.1.1-sis-carregadores** | `App.tsx` | `setInterval` | 30s | **Falho.** Provável cache do browser impedindo atualização real. |
| **06.1.1-sis-carregadores** | `CarregadoresKanban.tsx` | `setInterval` | 30s | Lógica duplicada de fetch dentro do componente. |
| **06-dtic-dashboard** | `useGLPIData.ts` | **SWR** (Polling) | 30s | **Melhor implementação.** Usa biblioteca `swr` com `refreshInterval` e `revalidateOnFocus`. |
| **06.1-sis-dashboard** | `useDashboardData.ts` | `setInterval` | 15s (env) | Implementação manual customizada com debounce. Funcional, mas reinventa a roda. |
| **glpi-smart-search** | `App.tsx` | Nenhuma | - | Busca apenas sob demanda (input do usuário). Correto para busca. |
| **sis-smart-search** | `App.tsx` | Nenhuma | - | Busca apenas sob demanda. |

---

## 3. Arquitetura Atual de Dados (GLPI → Backend → Frontend)

O fluxo de dados segue uma arquitetura de **Sincronização Assíncrona (Near Real-time)**.

1.  **Origem (GLPI):** A fonte da verdade.
2.  **Sincronização (Worker Python):**
    *   O serviço `glpi-data-service` possui um `RealtimeSyncWorker`.
    *   **Frequência:** Roda a cada **15 segundos** (configurável).
    *   **Lógica:** Faz polling no GLPI buscando tickets modificados recentemente (`incremental_sync`).
    *   **Persistência:** Salva/Atualiza dados no banco PostgreSQL (`glpi_data`).
    *   **Eficiência:** Calcula hash dos tickets para evitar writes desnecessários no banco.
3.  **API (FastAPI):**
    *   Expõe endpoints REST (ex: `/api/v1/sis/carregadores/kanban`).
    *   Lê diretamente do PostgreSQL.
    *   Não possui mecanismos de Push (WebSocket/SSE).
4.  **Frontend (React):**
    *   Consome a API via HTTP GET.

**Latência Total Estimada:**
*   Sync GLPI -> Postgres: ~15-20s (pior caso).
*   Polling Frontend -> API: ~30s.
*   **Atraso máximo percebido:** ~45-50 segundos. (Aceitável para dashboards operacionais).

---

## 4. Pesquisa de Boas Práticas e Padrões

Para dashboards administrativos que não exigem latência de milissegundos (como trading ou jogos), a indústria convergiu para padrões específicos:

### A. Polling Inteligente (Recomendado)
Uso de bibliotecas como **SWR (Stale-While-Revalidate)** ou **TanStack Query (React Query)**.
*   **Como funciona:** Mantém os dados em cache, mas revalida em background periodicamente ou quando o usuário foca na janela.
*   **Prós:** Extremamente simples de implementar, resolve cache automaticamente, trata retentativas de erro, evita "flicker" de loading.
*   **Contras:** Gera tráfego constante de rede (mesmo sem mudanças), mas para intervalos de 30s+ é irrelevante.

### B. Server-Sent Events (SSE)
*   **Como funciona:** O servidor mantém uma conexão HTTP aberta e empurra atualizações.
*   **Prós:** Atualização instantânea, menos tráfego se houver poucas mudanças.
*   **Contras:** Exige refatoração do backend (FastAPI suporta bem, mas precisa mudar a arquitetura para Event-Driven), mantém conexões estaduais abertas (consumo de memória no server).

### C. WebSockets
*   **Prós:** Bidirecional, real-time real.
*   **Contras:** Complexidade alta (handshake, reconexão, load balancing), overkill para dashboards de leitura.

**Conclusão da Pesquisa:**
Para o nosso cenário (atualização a cada 30s-1min), **Polling Inteligente (SWR/React Query)** é a escolha arquitetural correta. É robusto, stateless no backend e resolve o problema de cache do navegador nativamente.

---

## 5. Proposta de Padrão Unificado

Adotar a biblioteca **SWR** (já usada no `06-dtic-dashboard`) como padrão para todos os dashboards.

**Por que SWR?**
*   Leve (< 5kb).
*   Já está no `package.json` de um dos projetos.
*   API simples (`useSWR(key, fetcher, options)`).
*   Funcionalidades nativas cruciais:
    *   `refreshInterval`: Polling automático.
    *   `revalidateOnFocus`: Atualiza quando o usuário volta para a aba (ótimo para UX).
    *   `dedupingInterval`: Evita requisições duplicadas se dois componentes pedirem o mesmo dado.

**Estrutura Proposta para Hooks:**

```typescript
// Exemplo de padrão a ser adotado
import useSWR from 'swr';

export function useCarregadoresData() {
    const { data, error, isLoading } = useSWR(
        '/api/v1/sis/carregadores/kanban', 
        fetcher, 
        { 
            refreshInterval: 30000, // 30s
            revalidateOnFocus: true 
        }
    );
    
    return { data, isError: error, isLoading };
}
```

---

## 6. Plano Conceitual para o Dashboard de Carregadores

**Objetivo:** Corrigir o problema de atualização e limpar o código.

**Passos de Implementação (Futuro):**

1.  **Instalação:** Adicionar `swr` ao `package.json` do `06.1.1-sis-carregadores-dashboard`.
2.  **Criação de Hooks:**
    *   Criar `src/hooks/useCarregadores.ts`.
    *   Mover a lógica de fetch do `api.ts` para dentro do fetcher do SWR ou manter `api.ts` apenas como wrapper do `fetch`.
3.  **Refatoração do `App.tsx`:**
    *   Remover `useState` complexo (`chargers`, `ranking`, `loading`).
    *   Remover `useEffect` com `setInterval`.
    *   Substituir por: `const { chargers, ranking } = useCarregadores(dateRange);`
4.  **Refatoração do `CarregadoresKanban.tsx`:**
    *   Remover o `setInterval` interno (que hoje duplica a lógica).
    *   Receber dados via props ou usar o mesmo hook `useCarregadores` (o SWR fará a de-duplicação das chamadas, então podemos chamar o hook em vários lugares sem medo).

**Resultado Esperado:**
*   Código mais limpo (menos 40-50 linhas de gestão de estado manual).
*   Atualização automática garantida (SWR lida com cache busting).
*   Atualização imediata ao trocar de aba (revalidateOnFocus).

---

## 7. Checklist de Entrega

- [x] **Diagnóstico:** Problema identificado (Cache de navegador + Polling manual ingênuo).
- [x] **Inventário:** Projetos mapeados. `06-dtic-dashboard` é a referência positiva.
- [x] **Arquitetura:** Fluxo GLPI -> Worker (15s) -> Postgres -> API -> Frontend mapeado.
- [x] **Boas Práticas:** Polling Inteligente (SWR) selecionado como melhor custo-benefício.
- [x] **Plano Unificado:** Padronizar uso de SWR em todos os dashboards.
- [x] **Plano Específico:** Roteiro para refatorar `sis-carregadores-dashboard` removendo `setInterval` e adotando `useSWR`.

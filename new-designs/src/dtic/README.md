# Dashboard DTIC - Departamento de Tecnologia da Informação

## Descrição
Dashboard de métricas em tempo real para monitoramento de tickets do GLPI - DTIC.

## Estrutura de Arquivos

```
dtic/
├── App.tsx                              # Componente principal
└── components/
    ├── DashboardHeader.tsx              # Cabeçalho com navegação e relógio
    ├── MetricsCardsCompact.tsx          # Cards de métricas (Novos, Em Progresso, Pendentes, Resolvidos)
    ├── LevelCharts.tsx                  # Gráficos de distribuição por níveis (N1-N4)
    ├── QuickStats.tsx                   # Indicadores rápidos (Taxa de Resolução, SLA, Tempo Médio)
    ├── TechnicianRankingCompact.tsx     # Ranking de técnicos
    └── RecentTicketsCompact.tsx         # Tickets recentes e atividades
```

## Dependências Externas
- `lucide-react` - Ícones
- `recharts` - Gráficos (Bar Chart e Pie Chart)
- React hooks (useState, useEffect)

## Props da Aplicação
```typescript
interface DashboardDTICProps {
  onSwitchToDashboard: () => void;  // Função para navegar para dashboard SIS
  onSwitchToSearch: () => void;     // Função para navegar para busca DTIC
}
```

## Dados Principais
- **Métricas**: 2 Novos, 20 Em Progresso, 4 Pendentes, 387 Resolvidos
- **Níveis**: N1 (60), N2 (140), N3 (239), N4 (0)
- **Técnicos**: 9 técnicos no ranking
- **Período**: 21/10/2025 - 20/11/2025

## Características
- Layout fixo sem scroll (otimizado para TV)
- Tema dark com gradientes azuis
- Relógio em tempo real
- Gráficos interativos
- Animações suaves

# Dashboard SIS - Divisão de Manutenção

## Descrição
Dashboard de métricas para monitoramento de tickets de manutenção e conservação do GLPI - SIS.

## Estrutura de Arquivos

```
sis/
├── App.tsx                              # Componente principal
└── components/
    ├── DashboardHeader.tsx              # Cabeçalho com navegação e relógio
    ├── MetricsCardsCompact.tsx          # Cards de métricas (Novos, Em Atendimento, Pendentes, Planejados, Resolvidos)
    ├── EntityDistribution.tsx           # Distribuição por entidades com gráfico de barras
    ├── CategoryDistribution.tsx         # Distribuição por categorias com gráfico de pizza
    ├── TechnicianRanking.tsx            # Ranking de técnicos de manutenção
    ├── RecentTickets.tsx                # Tickets recentes
    └── QuickStats.tsx                   # Indicadores rápidos
```

## Dependências Externas
- `lucide-react` - Ícones
- `recharts` - Gráficos (Bar Chart, Pie Chart)
- React hooks (useState, useEffect)

## Props da Aplicação
```typescript
interface DashboardSISProps {
  onSwitchToDashboard: () => void;  // Função para navegar para dashboard DTIC
  onSwitchToSearch: () => void;     // Função para navegar para busca SIS
}
```

## Dados Principais
- **Métricas**: 1 Novo, 13 Em Atendimento, 7 Pendentes, 11 Planejados, 653 Resolvidos
- **Entidades**: Depto Conservação (160), PIRATINI (116), Outros (85)
- **Categorias**: Marcenaria (34), Marc. Outras (32), Elétrica (25), Pedreiro (24), etc.
- **Técnicos**: 5 técnicos no ranking, líder: Vera M. (220 tickets)
- **Período**: 07/09/2025 - 07/10/2025

## Características
- Layout fixo sem scroll (otimizado para TV)
- Tema dark com gradientes azuis
- Relógio em tempo real
- Gráficos de distribuição visual
- Ranking destacado

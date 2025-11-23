# Dashboard de Carregadores

## Descrição
Sistema de monitoramento em tempo real de carregadores com rastreamento de status, localização e ranking de produtividade.

## Estrutura de Arquivos

```
carregadores/
├── App.tsx                              # Componente principal
└── components/
    ├── CarregadoresHeader.tsx           # Cabeçalho com filtros de data e navegação
    ├── StatusOverview.tsx               # Cards de status (Disponíveis, Ocupados, Offline, Total)
    ├── CarregadoresList.tsx             # Tabela com lista de todos os carregadores
    └── CarregadoresRanking.tsx          # Ranking de produtividade (últimos 30 dias)
```

## Dependências Externas
- `lucide-react` - Ícones
- React hooks (useState, useEffect)

## Props da Aplicação
```typescript
interface CarregadoresProps {
  onNavigate: (view: string) => void;  // Função para navegar entre aplicações
}
```

## Dados Principais
- **Status**: 4 Disponíveis, 1 Ocupado, 0 Offline, 5 Total
- **Carregadores**: 5 carregadores cadastrados
- **Localização padrão**: Casa Civil 1005
- **Período do ranking**: últimos 30 dias
- **Período de filtro**: 22/10/2025 - 21/11/2025

## Funcionalidades
- Monitoramento em tempo real com relógio
- Status visual com indicadores coloridos (verde/laranja)
- Filtros de período (data início e fim)
- Tabela com informações completas:
  - Nome do carregador
  - Status atual (Disponível/Ocupado)
  - Localização
  - Tempo de atividade
  - Ticket associado
- Ranking de produtividade com:
  - Top 1 em destaque (troféu dourado)
  - Medalhas para top 3
  - Total de tickets atribuídos

## Características
- Tema dark com gradientes sutis
- Badges coloridos por status
- Animações de pulse nos indicadores ativos
- Hover effects nas linhas da tabela
- Layout responsivo e clean
- Navegação para outros dashboards

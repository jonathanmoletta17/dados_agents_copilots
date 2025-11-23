# GLPI Smart Search - DTIC

## Descrição
Sistema inteligente de busca de tickets do GLPI para o Departamento de Tecnologia da Informação.

## Estrutura de Arquivos

```
dtic-search/
├── App.tsx                              # Componente principal
└── components/
    ├── SearchHeader.tsx                 # Cabeçalho com navegação
    ├── SearchBar.tsx                    # Barra de pesquisa com filtros
    ├── MetricsCards.tsx                 # Cards com totais (Fechados, Resolvidos, Em andamento, Pendentes)
    └── ResultsList.tsx                  # Lista de resultados com paginação
```

## Dependências Externas
- `lucide-react` - Ícones
- React hooks (useState)

## Props da Aplicação
```typescript
interface SearchDTICProps {
  onSwitchToDashboard: () => void;  // Função para navegar para dashboard DTIC
  onSwitchToSearch: () => void;     // Função para navegar para busca SIS
}
```

## Dados Principais
- **Totais**: 7,167 Fechados, 3,846 Resolvidos, 40 Em andamento, 15 Pendentes
- **Total de resultados**: 11,080 tickets
- **Campos exibidos**: ID, Status, Título, Entidade, Categoria, Requerente, Técnico, Grupo, Datas

## Funcionalidades
- Busca por texto livre
- Filtros avançados
- Ordenação por Relevância ou Recentes
- Paginação de resultados
- Cards de tickets detalhados com todos os metadados

## Características
- Design moderno com tema dark
- Barra de busca responsiva
- Badges coloridos por status
- Hover effects nos resultados
- Layout scrollable para grandes volumes de dados

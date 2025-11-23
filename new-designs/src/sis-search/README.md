# GLPI SIS Smart Search

## Descrição
Sistema de busca de tickets para a Divisão de Manutenção e Conservação (SIS).

## Estrutura de Arquivos

```
sis-search/
├── App.tsx                              # Componente principal
└── components/
    ├── SearchHeader.tsx                 # Cabeçalho com navegação
    ├── SearchBar.tsx                    # Barra de pesquisa com filtros
    ├── MetricsCards.tsx                 # Cards com totais (Fechados, Em andamento, Resolvidos, Pendentes)
    └── ResultsList.tsx                  # Lista de resultados com paginação
```

## Dependências Externas
- `lucide-react` - Ícones
- React hooks (useState)

## Props da Aplicação
```typescript
interface SearchSISProps {
  onSwitchToDashboard: () => void;  // Função para navegar para dashboard SIS
  onSwitchToSearch: () => void;     // Função para navegar para busca DTIC
}
```

## Dados Principais
- **Totais**: 4,822 Fechados, 26 Em andamento, 24 Resolvidos, 10 Pendentes
- **Total de resultados**: 4,890 tickets
- **Campos exibidos**: ID, Status, Título, Entidade, Categoria, Requerente, Técnico, Grupo, Datas

## Funcionalidades
- Busca por texto livre (tickets, descrições, categorias, técnicos)
- Botão de filtros avançados
- Ordenação por Relevância ou Recentes
- Paginação de resultados
- Detalhamento completo de cada ticket

## Características
- Interface consistente com busca DTIC
- Tema dark moderno
- Badges coloridos por status
- Dados específicos de manutenção (Marcenaria, Elétrica, Pedreiro, etc.)
- Layout responsivo e profissional

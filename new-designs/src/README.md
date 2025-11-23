# Sistema GLPI - Dashboards e Buscadores

Sistema completo de dashboards e buscadores para GLPI com design moderno, otimizado para visualização em tempo real.

## 📁 Estrutura do Projeto

```
/
├── App.tsx                    # Componente raiz com navegação entre aplicações
│
├── dtic/                      # Dashboard DTIC
│   ├── App.tsx
│   ├── README.md
│   └── components/
│
├── sis/                       # Dashboard SIS (Manutenção)
│   ├── App.tsx
│   ├── README.md
│   └── components/
│
├── dtic-search/               # Buscador DTIC
│   ├── App.tsx
│   ├── README.md
│   └── components/
│
├── sis-search/                # Buscador SIS
│   ├── App.tsx
│   ├── README.md
│   └── components/
│
└── carregadores/              # Dashboard de Carregadores
    ├── App.tsx
    ├── README.md
    └── components/
```

## 🎯 Aplicações Disponíveis

### 1. **Dashboard DTIC** (`/dtic/`)
- Dashboard de métricas do Departamento de Tecnologia da Informação
- Métricas: Novos, Em Progresso, Pendentes, Resolvidos
- Gráficos por níveis (N1-N4)
- Ranking de técnicos
- Otimizado para TV (sem scroll)

### 2. **Dashboard SIS** (`/sis/`)
- Dashboard da Divisão de Manutenção
- Métricas: Novos, Em Atendimento, Pendentes, Planejados, Resolvidos
- Distribuição por entidades e categorias
- Ranking de técnicos de manutenção
- Otimizado para TV (sem scroll)

### 3. **Buscador DTIC** (`/dtic-search/`)
- Sistema de busca inteligente de tickets DTIC
- 11,080+ tickets indexados
- Filtros avançados
- Ordenação por relevância ou data

### 4. **Buscador SIS** (`/sis-search/`)
- Sistema de busca para tickets de manutenção
- 4,890+ tickets indexados
- Busca por categorias específicas de manutenção
- Interface consistente com buscador DTIC

### 5. **Dashboard Carregadores** (`/carregadores/`)
- Monitoramento em tempo real de carregadores
- Status: Disponíveis, Ocupados, Offline
- Ranking de produtividade
- Rastreamento de localização e tickets

## 🔧 Tecnologias Utilizadas

- **React** + **TypeScript**
- **Tailwind CSS** - Estilização
- **Lucide React** - Ícones
- **Recharts** - Gráficos (Bar Chart, Pie Chart)
- React Hooks (useState, useEffect)

## 📦 Como Extrair uma Aplicação

Cada pasta é **completamente independente** e pode ser extraída separadamente:

1. Copie a pasta desejada (ex: `/dtic/`)
2. Todos os componentes necessários estão dentro de `/components/`
3. Consulte o `README.md` da pasta para entender as dependências
4. Instale as dependências externas listadas
5. Implemente as funções de navegação conforme seu contexto

## 🎨 Design System

### Cores Principais
- **Azul**: `from-blue-600 to-blue-800` - Headers e elementos principais
- **Verde**: `from-green-500 to-green-600` - Status positivo (Resolvidos, Disponíveis)
- **Laranja**: `from-orange-500 to-orange-600` - Em progresso/atenção
- **Amarelo**: `from-yellow-500 to-yellow-600` - Pendentes/alertas
- **Slate**: `from-slate-900 to-slate-800` - Background

### Tema
- **Dark Mode** predominante
- Gradientes sutis
- Backdrop blur effects
- Borders com transparência
- Hover states com scale

## 🔄 Sistema de Navegação

A navegação entre aplicações é feita através de callbacks:

```typescript
// Exemplo de navegação
<DashboardDTIC 
  onSwitchToDashboard={() => navigateTo("sis-dashboard")}
  onSwitchToSearch={() => navigateTo("dtic-search")}
/>
```

## 📊 Características Gerais

- ✅ Layouts responsivos
- ✅ Relógios em tempo real
- ✅ Animações suaves
- ✅ Gráficos interativos
- ✅ Paginação de dados
- ✅ Filtros de período
- ✅ Status com cores semânticas
- ✅ Badges e indicadores visuais
- ✅ Hover effects
- ✅ Design consistente entre todas as aplicações

## 📝 Notas de Implementação

1. **Independência**: Cada aplicação é autocontida
2. **Props**: Adapte as funções de callback para seu sistema de rotas
3. **Dados**: Os dados são mock - substitua pelos seus endpoints reais
4. **Estilo**: Tailwind CSS configurado na versão 4.0
5. **Ícones**: Todos os ícones são do pacote `lucide-react`

## 🚀 Início Rápido

```bash
# Instalar dependências
npm install lucide-react recharts

# Para usar uma aplicação específica:
# 1. Copie a pasta desejada
# 2. Importe no seu projeto
# 3. Passe as funções de navegação necessárias
```

---

**Desenvolvido com foco em:** Ciência de dados, Data storytelling, Visualização moderna e UX otimizada para análise rápida.

import { useState } from 'react';
import { Search, SlidersHorizontal, X } from 'lucide-react';

interface SearchBarProps {
  value: string;
  onChange: (value: string) => void;
  onFilterChange: (filters: Record<string, any>) => void;
}

export default function SearchBar({ value, onChange, onFilterChange }: SearchBarProps) {
  const [showFilters, setShowFilters] = useState(false);
  const [localFilters, setLocalFilters] = useState<any>({});

  const apply = () => {
    onFilterChange(localFilters);
    setShowFilters(false);
  };

  const clearFilters = () => {
    setLocalFilters({});
    onFilterChange({});
    setShowFilters(false);
  };

  return (
    <div className="space-y-4">
      {/* Search Input Row */}
      <div className="flex gap-3">
        <div className="flex-1 relative">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
          <input
            type="text"
            value={value}
            onChange={(e) => onChange(e.target.value)}
            placeholder="Pesquise por tickets, descrições, categorias, técnicos..."
            className="w-full bg-slate-800/50 backdrop-blur-sm border border-slate-700/50 rounded-xl pl-12 pr-4 py-4 text-slate-200 placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 transition-all shadow-lg"
          />
        </div>

        <button
          onClick={() => setShowFilters(!showFilters)}
          className={`px-6 py-4 rounded-xl transition-all shadow-lg hover:shadow-xl hover:scale-105 flex items-center gap-2 border ${showFilters
              ? 'bg-blue-600 border-blue-500/30 text-white'
              : 'bg-blue-600 hover:bg-blue-700 border-blue-500/30 text-white'
            }`}
        >
          <SlidersHorizontal className="w-5 h-5" />
          <span>Filtros</span>
        </button>
      </div>

      {/* Advanced Filters Panel */}
      {showFilters && (
        <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl shadow-2xl p-6 border border-slate-700/50">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-slate-200 flex items-center gap-2">
              <SlidersHorizontal className="w-5 h-5" />
              Filtros Avançados
            </h3>
            <button
              onClick={() => setShowFilters(false)}
              className="text-slate-400 hover:text-slate-200 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Filters Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            {/* Status Filter */}
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Status</label>
              <select
                value={localFilters.status || ''}
                onChange={(e) => setLocalFilters({ ...localFilters, status: e.target.value })}
                className="w-full px-3 py-2 bg-slate-700/50 border border-slate-600/50 rounded-lg text-slate-200 focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 transition-all"
              >
                <option value="">Todos</option>
                <option value="novo">Novo</option>
                <option value="processando (atribuído)">Em Andamento</option>
                <option value="pendente">Pendente</option>
                <option value="solucionado">Solucionado</option>
                <option value="fechado">Fechado</option>
              </select>
            </div>

            {/* Entidade Filter */}
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Entidade</label>
              <input
                type="text"
                value={localFilters.entidade || ''}
                onChange={(e) => setLocalFilters({ ...localFilters, entidade: e.target.value })}
                className="w-full px-3 py-2 bg-slate-700/50 border border-slate-600/50 rounded-lg text-slate-200 placeholder:text-slate-500 focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 transition-all"
                placeholder="Digite a entidade..."
              />
            </div>

            {/* Categoria Filter */}
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Categoria</label>
              <input
                type="text"
                value={localFilters.categoria || ''}
                onChange={(e) => setLocalFilters({ ...localFilters, categoria: e.target.value })}
                className="w-full px-3 py-2 bg-slate-700/50 border border-slate-600/50 rounded-lg text-slate-200 placeholder:text-slate-500 focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 transition-all"
                placeholder="Digite a categoria..."
              />
            </div>

            {/* Técnico Filter */}
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Técnico</label>
              <input
                type="text"
                value={localFilters.tecnico || ''}
                onChange={(e) => setLocalFilters({ ...localFilters, tecnico: e.target.value })}
                className="w-full px-3 py-2 bg-slate-700/50 border border-slate-600/50 rounded-lg text-slate-200 placeholder:text-slate-500 focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 transition-all"
                placeholder="Digite o técnico..."
              />
            </div>

            {/* Requerente Filter */}
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Requerente</label>
              <input
                type="text"
                value={localFilters.requerente || ''}
                onChange={(e) => setLocalFilters({ ...localFilters, requerente: e.target.value })}
                className="w-full px-3 py-2 bg-slate-700/50 border border-slate-600/50 rounded-lg text-slate-200 placeholder:text-slate-500 focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 transition-all"
                placeholder="Digite o requerente..."
              />
            </div>
          </div>

          {/* Date Filters */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Data Início</label>
              <input
                type="date"
                value={localFilters.dt_ini || ''}
                onChange={(e) => setLocalFilters({ ...localFilters, dt_ini: e.target.value })}
                className="w-full px-3 py-2 bg-slate-700/50 border border-slate-600/50 rounded-lg text-slate-200 focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 transition-all"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Data Fim</label>
              <input
                type="date"
                value={localFilters.dt_fim || ''} onChange={(e) => setLocalFilters({ ...localFilters, dt_fim: e.target.value })}
                className="w-full px-3 py-2 bg-slate-700/50 border border-slate-600/50 rounded-lg text-slate-200 focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 transition-all"
              />
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex justify-end gap-3">
            <button
              onClick={clearFilters}
              className="px-6 py-2 text-slate-300 hover:bg-slate-700/50 rounded-lg transition-colors border border-slate-600/50"
            >
              Limpar
            </button>
            <button
              onClick={apply}
              className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors shadow-lg"
            >
              Aplicar Filtros
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
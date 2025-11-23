import { useState } from 'react'
import { Search, SlidersHorizontal, X } from 'lucide-react'

export default function SearchBar({ value, onChange, onFilterChange }: any) {
  const [showFilters, setShowFilters] = useState(false)
  const [localFilters, setLocalFilters] = useState<any>({})

  const handleFilterApply = () => {
    onFilterChange(localFilters)
    setShowFilters(false)
  }

  return (
    <div className="space-y-4">
      {/* Search Input */}
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
          className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-4 rounded-xl transition-all shadow-lg hover:shadow-xl hover:scale-105 flex items-center gap-2 border border-blue-500/30"
        >
          <SlidersHorizontal className="w-5 h-5" />
          <span>Filtros</span>
        </button>
      </div>

      {/* Filters Panel */}
      {showFilters && (
        <div className="bg-slate-800/90 backdrop-blur-sm rounded-xl shadow-xl p-6 border border-slate-700/50">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-semibold text-slate-200">Filtros Avançados</h3>
            <button onClick={() => setShowFilters(false)} className="text-slate-400 hover:text-white">
              <X className="w-5 h-5" />
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-400 mb-2">Status</label>
              <select
                value={localFilters.status || ''}
                onChange={(e) => setLocalFilters({ ...localFilters, status: e.target.value })}
                className="w-full px-3 py-2 bg-slate-700/50 border border-slate-600/50 rounded-lg text-slate-200 focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50"
              >
                <option value="">Todos</option>
                <option value="novo">Novo</option>
                <option value="processando (atribuído)">Em Andamento</option>
                <option value="pendente">Pendente</option>
                <option value="solucionado">Solucionado</option>
                <option value="fechado">Fechado</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-400 mb-2">Motivo de Pendência</label>
              <select
                value={localFilters.motivo_pendencia || ''}
                onChange={(e) => setLocalFilters({ ...localFilters, motivo_pendencia: e.target.value })}
                className="w-full px-3 py-2 bg-slate-700/50 border border-slate-600/50 rounded-lg text-slate-200 focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50"
              >
                <option value="">Todos</option>
                <option value="Aguardando Ação do Usuário">Aguardando Ação do Usuário</option>
                <option value="Aguardando Disponibilidade de Material">Aguardando Disponibilidade de Material</option>
                <option value="Aguardando Transferência">Aguardando Transferência</option>
                <option value="Aguardando Validação">Aguardando Validação</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-400 mb-2">Entidade</label>
              <input
                type="text"
                value={localFilters.entidade || ''}
                onChange={(e) => setLocalFilters({ ...localFilters, entidade: e.target.value })}
                placeholder="Digite a entidade..."
                className="w-full px-3 py-2 bg-slate-700/50 border border-slate-600/50 rounded-lg text-slate-200 placeholder:text-slate-500 focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-400 mb-2">Categoria</label>
              <input
                type="text"
                value={localFilters.categoria || ''}
                onChange={(e) => setLocalFilters({ ...localFilters, categoria: e.target.value })}
                placeholder="Digite a categoria..."
                className="w-full px-3 py-2 bg-slate-700/50 border border-slate-600/50 rounded-lg text-slate-200 placeholder:text-slate-500 focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-400 mb-2">Técnico</label>
              <input
                type="text"
                value={localFilters.tecnico || ''}
                onChange={(e) => setLocalFilters({ ...localFilters, tecnico: e.target.value })}
                placeholder="Digite o técnico..."
                className="w-full px-3 py-2 bg-slate-700/50 border border-slate-600/50 rounded-lg text-slate-200 placeholder:text-slate-500 focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-400 mb-2">Requerente</label>
              <input
                type="text"
                value={localFilters.requerente || ''}
                onChange={(e) => setLocalFilters({ ...localFilters, requerente: e.target.value })}
                placeholder="Digite o requerente..."
                className="w-full px-3 py-2 bg-slate-700/50 border border-slate-600/50 rounded-lg text-slate-200 placeholder:text-slate-500 focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50"
              />
            </div>
          </div>

          {/* Filtros de Data */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
            <div>
              <label className="block text-sm font-medium text-slate-400 mb-2">Data Início</label>
              <input
                type="date"
                value={localFilters.dt_ini || ''}
                onChange={(e) => setLocalFilters({ ...localFilters, dt_ini: e.target.value })}
                className="w-full px-3 py-2 bg-slate-700/50 border border-slate-600/50 rounded-lg text-slate-200 focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-400 mb-2">Data Fim</label>
              <input
                type="date"
                value={localFilters.dt_fim || ''}
                onChange={(e) => setLocalFilters({ ...localFilters, dt_fim: e.target.value })}
                className="w-full px-3 py-2 bg-slate-700/50 border border-slate-600/50 rounded-lg text-slate-200 focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50"
              />
            </div>
          </div>

          <div className="flex justify-end gap-3 mt-6">
            <button
              onClick={() => {
                setLocalFilters({})
                onFilterChange({})
                setShowFilters(false)
              }}
              className="px-4 py-2 text-slate-400 hover:text-white hover:bg-slate-700/50 rounded-lg transition-colors"
            >
              Limpar
            </button>
            <button
              onClick={handleFilterApply}
              className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors shadow-lg"
            >
              Aplicar Filtros
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
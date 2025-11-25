import { useEffect, useRef, useState } from 'react'
import { Search, SlidersHorizontal, X, ChevronDown } from 'lucide-react'
import { suggestApi } from '../services/api'

type EntitySuggestion = { id?: number | string, label: string }

function useEntityDropdown() {
  const [entityOpen, setEntityOpen] = useState(false)
  const [entityQuery, setEntityQuery] = useState('')
  const [entityLoading, setEntityLoading] = useState(false)
  const [entitySuggestions, setEntitySuggestions] = useState<EntitySuggestion[]>([])
  const dropdownRef = useRef<HTMLDivElement | null>(null)

  useEffect(() => {
    let cancelled = false
    if (entityOpen) {
      setEntityLoading(true)
      const prefix = entityQuery.trim()
      const timer = setTimeout(() => {
        suggestApi('entidade', prefix).then((list: any) => {
          if (cancelled) return
          const arr = Array.isArray(list) ? list : []
          const normalized: EntitySuggestion[] = arr.map((it: any) => {
            if (typeof it === 'string') return { label: it }
            const id = it?.id ?? it?.entities_id ?? it?.value
            const label = it?.name ?? it?.label ?? it?.completename ?? it?.text ?? String(id ?? '')
            return { id, label }
          })
          setEntitySuggestions(normalized)
        }).finally(() => { if (!cancelled) setEntityLoading(false) })
      }, 250)
      return () => { cancelled = true; clearTimeout(timer) }
    }
  }, [entityOpen, entityQuery])

  useEffect(() => {
    const onDocClick = (e: MouseEvent) => {
      if (!dropdownRef.current) return
      const t = e.target as Node
      if (entityOpen && t && !dropdownRef.current.contains(t)) setEntityOpen(false)
    }
    document.addEventListener('mousedown', onDocClick)
    return () => document.removeEventListener('mousedown', onDocClick)
  }, [entityOpen])

  return { entityOpen, setEntityOpen, entityQuery, setEntityQuery, entityLoading, entitySuggestions, dropdownRef }
}

export default function SearchBar({ value, onChange, onFilterChange }: any) {
  const [showFilters, setShowFilters] = useState(false)
  const [localFilters, setLocalFilters] = useState<any>({})
  const { entityOpen, setEntityOpen, entityQuery, setEntityQuery, entityLoading, entitySuggestions, dropdownRef } = useEntityDropdown()

  const handleFilterApply = () => {
    onFilterChange(localFilters)
    setShowFilters(false)
  }

  const handleClear = () => {
    setLocalFilters({})
    onFilterChange({})
    setShowFilters(false)
  }

  return (
    <div className="space-y-4">
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

            <div className="relative">
              <label className="block text-sm font-medium text-slate-400 mb-2">Entidade</label>
              <button
                type="button"
                onClick={() => setEntityOpen((o) => !o)}
                className="w-full px-3 py-2 bg-slate-700/50 border border-slate-600/50 rounded-lg text-slate-200 flex items-center justify-between"
              >
                <span className="truncate">{localFilters.entidade || 'Selecione ou pesquise...'}</span>
                <ChevronDown className="w-4 h-4 text-slate-300" />
              </button>
              {entityOpen && (
                <div ref={dropdownRef} className="absolute z-50 mt-2 w-full bg-slate-800 border border-slate-700 rounded-lg shadow-xl">
                  <div className="p-2 border-b border-slate-700">
                    <input
                      type="text"
                      value={entityQuery}
                      onChange={(e) => setEntityQuery(e.target.value)}
                      placeholder="Buscar entidade..."
                      className="w-full px-3 py-2 bg-slate-700/50 border border-slate-600/50 rounded-md text-slate-200 placeholder:text-slate-500 focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50"
                    />
                  </div>
                  <div className="max-h-48 overflow-auto">
                    {entityLoading ? (
                      <div className="p-3 text-slate-400 text-sm">Carregando...</div>
                    ) : entitySuggestions.length === 0 ? (
                      <div className="p-3 text-slate-400 text-sm">Nenhuma entidade encontrada</div>
                    ) : (
                      entitySuggestions.map((s) => (
                        <button
                          key={`${s.id ?? s.label}`}
                          type="button"
                          onClick={() => {
                            const nf = { ...localFilters, entidade: s.label }
                            if (s.id !== undefined && s.id !== null) (nf as any).entidadeId = s.id
                            setLocalFilters(nf)
                            setEntityOpen(false)
                          }}
                          className="w-full text-left px-3 py-2 hover:bg-slate-700/50 text-slate-200"
                          title={s.label}
                        >
                          {s.label}
                        </button>
                      ))
                    )}
                  </div>
                </div>
              )}
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
              <label className="block text sm font-medium text-slate-400 mb-2">Data Fim</label>
              <input
                type="date"
                value={localFilters.dt_fim || ''}
                onChange={(e) => setLocalFilters({ ...localFilters, dt_fim: e.target.value })}
                className="w-full px-3 py-2 bg-slate-700/50 border border-slate-600/50 rounded-lg text-slate-200 focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50"
              />
            </div>
          </div>

          <div className="flex justify-end gap-3 mt-6">
            <button onClick={handleClear} className="px-4 py-2 text-slate-400 hover:text-white hover:bg-slate-700/50 rounded-lg transition-colors">Limpar</button>
            <button onClick={handleFilterApply} className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors shadow-lg">Aplicar Filtros</button>
          </div>
        </div>
      )}
    </div>
  )
}

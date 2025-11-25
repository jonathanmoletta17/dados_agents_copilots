import { X } from "lucide-react";

export default function FilterChips({ filters, onRemove }: { filters: Record<string, any>, onRemove: (k: string) => void }) {
  const entries = Object.entries(filters)
    .filter(([k, v]) => v !== '' && v !== undefined && v !== null && k !== 'entidadeId')

  if (entries.length === 0) return null

  const getLabel = (key: string) => {
    const labels: Record<string, string> = {
      status: 'Status',
      entidade: 'Entidade',
      entidadeId: 'Entidade',
      categoria: 'Categoria',
      tecnico: 'Técnico',
      grupo: 'Grupo',
      requerente: 'Requerente',
      motivo_pendencia: 'Motivo Pendência',
      dt_ini: 'Data Início',
      dt_fim: 'Data Fim'
    }
    return labels[key] || key
  }

  return (
    <div className="flex flex-wrap gap-2 items-center">
      <span className="text-sm font-medium text-slate-400">Filtros ativos:</span>
      {entries.map(([key, value]) => (
        <div
          key={key}
          className="inline-flex items-center gap-2 px-3 py-1.5 bg-blue-500/20 text-blue-400 rounded-lg text-sm font-medium border border-blue-400/30"
        >
          <span className="font-semibold text-blue-300">{getLabel(key)}:</span>
          <span>{value}</span>
          <button
            onClick={() => onRemove(key)}
            className="ml-1 hover:bg-blue-500/30 rounded-full p-0.5 transition-colors text-blue-400"
          >
            <X className="w-3 h-3" />
          </button>
        </div>
      ))}
      <button
        onClick={() => entries.forEach(([k]) => onRemove(k))}
        className="text-sm text-red-400 hover:text-red-300 font-medium hover:underline transition-colors"
      >
        Limpar todos
      </button>
    </div>
  )
}

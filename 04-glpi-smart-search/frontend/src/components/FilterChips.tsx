export default function FilterChips({ filters, onRemove }: { filters: Record<string, any>, onRemove: (k: string) => void }) {
  const entries = Object.entries(filters).filter(([_, v]) => v !== '' && v !== undefined && v !== null)

  if (entries.length === 0) return null

  const getLabel = (key: string) => {
    const labels: Record<string, string> = {
      status: 'Status',
      entidade: 'Entidade',
      categoria: 'Categoria',
      tecnico: 'Técnico',
      grupo: 'Grupo',
      requerente: 'Requerente'
    }
    return labels[key] || key
  }

  return (
    <div className="flex flex-wrap gap-2 items-center">
      <span className="text-sm font-medium text-gray-600">Filtros ativos:</span>
      {entries.map(([key, value]) => (
        <div
          key={key}
          className="inline-flex items-center gap-2 px-3 py-1.5 bg-blue-100 text-blue-800 rounded-lg text-sm font-medium border border-blue-300"
        >
          <span className="font-semibold">{getLabel(key)}:</span>
          <span>{value}</span>
          <button
            onClick={() => onRemove(key)}
            className="ml-1 hover:bg-blue-200 rounded-full p-0.5 transition-colors"
          >
            <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      ))}
      <button
        onClick={() => entries.forEach(([k]) => onRemove(k))}
        className="text-sm text-red-600 hover:text-red-700 font-medium hover:underline"
      >
        Limpar todos
      </button>
    </div>
  )
}
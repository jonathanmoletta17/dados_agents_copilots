export default function ResultsTable({ rows, sort, setSort, page, setPage }: { rows: any[], sort: string, setSort: (v: string) => void, page: number, setPage: (n: number) => void }) {
  const glpiUrl = (id: number) => `http://cau.ppiratini.intra.rs.gov.br/glpi/front/ticket.form.php?id=${id}`

  const getStatusStyle = (status: string) => {
    const s = status?.toLowerCase() || ''
    if (s.includes('novo')) return 'bg-blue-100 text-blue-800 border-blue-300'
    if (s.includes('progresso') || s.includes('atribuído')) return 'bg-orange-100 text-orange-800 border-orange-300'
    if (s.includes('pendente')) return 'bg-yellow-100 text-yellow-800 border-yellow-300'
    if (s.includes('solucionado')) return 'bg-green-100 text-green-800 border-green-300'
    if (s.includes('fechado')) return 'bg-gray-100 text-gray-800 border-gray-300'
    return 'bg-gray-100 text-gray-600 border-gray-200'
  }

  return (
    <div className="space-y-4">
      {/* Sort Controls */}
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold text-gray-800">
          Resultados <span className="text-blue-600">({rows.length})</span>
        </h2>
        <div className="flex gap-2">
          <button
            onClick={() => setSort('score')}
            className={`px-4 py-2 rounded-lg font-medium transition-all ${sort === 'score'
                ? 'bg-blue-500 text-white shadow-md'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
          >
            🎯 Relevância
          </button>
          <button
            onClick={() => setSort('recent')}
            className={`px-4 py-2 rounded-lg font-medium transition-all ${sort === 'recent'
                ? 'bg-blue-500 text-white shadow-md'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
          >
            🕐 Recentes
          </button>
        </div>
      </div>

      {/* Results Grid */}
      <div className="space-y-3">
        {rows.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            <svg className="mx-auto h-12 w-12 text-gray-400 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p className="text-lg font-medium">Nenhum resultado encontrado</p>
            <p className="text-sm mt-1">Tente ajustar sua busca ou filtros</p>
          </div>
        ) : (
          rows.map(r => {
            const hasHighlight = !!(r.highlight && r.highlight.trim())
            const isNumericTitle = !hasHighlight && r.titulo && String(r.titulo).trim() === String(r.id)
            const displayTitle = isNumericTitle ? (r.descricao || `Ticket #${r.id}`) : (r.titulo || `Ticket #${r.id}`)

            return (
              <div
                key={r.id}
                onClick={() => window.open(r.url || glpiUrl(r.id), '_blank')}
                className="group bg-white border border-gray-200 rounded-xl p-5 hover:shadow-xl hover:border-blue-300 transition-all duration-300 cursor-pointer"
              >
                <div className="flex items-start justify-between gap-4">
                  {/* Left: ID & Content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-3 mb-2">
                      <span className="inline-flex items-center px-3 py-1 rounded-lg bg-blue-50 text-blue-700 font-mono text-sm font-semibold">
                        #{r.id}
                      </span>
                      <span className={`inline-flex items-center px-3 py-1 rounded-lg border text-xs font-semibold ${getStatusStyle(r.status)}`}>
                        {r.status}
                      </span>
                    </div>

                    <h3 className="text-lg font-semibold text-gray-900 mb-2 group-hover:text-blue-600 transition-colors">
                      {hasHighlight ? (
                        <span dangerouslySetInnerHTML={{ __html: r.highlight }} />
                      ) : (
                        <span className="line-clamp-2">{displayTitle}</span>
                      )}
                    </h3>

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                      <div>
                        <span className="text-gray-500 font-medium">Entidade:</span>
                        <p className="text-gray-800 truncate">{r.entidade || 'N/A'}</p>
                      </div>
                      <div>
                        <span className="text-gray-500 font-medium">Categoria:</span>
                        <p className="text-gray-800 truncate">{r.categoria || 'N/A'}</p>
                      </div>
                      <div>
                        <span className="text-gray-500 font-medium">Requerente:</span>
                        <p className="text-gray-800 truncate">{r.requerente || 'N/A'}</p>
                      </div>
                      <div>
                        <span className="text-gray-500 font-medium">Técnico:</span>
                        <p className="text-gray-800 truncate">{r.tecnico || 'N/A'}</p>
                      </div>
                    </div>
                  </div>

                  {/* Right: Arrow */}
                  <div className="flex-shrink-0">
                    <svg className="h-6 w-6 text-gray-400 group-hover:text-blue-500 group-hover:translate-x-1 transition-all" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                  </div>
                </div>
              </div>
            )
          })
        )}
      </div>

      {/* Pagination */}
      {rows.length > 0 && (
        <div className="flex items-center justify-center gap-3 pt-6">
          <button
            onClick={() => setPage(Math.max(1, page - 1))}
            disabled={page <= 1}
            className="px-4 py-2 bg-white border-2 border-gray-300 rounded-lg font-medium text-gray-700 hover:bg-gray-50 hover:border-blue-400 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
          >
            ← Anterior
          </button>
          <span className="px-4 py-2 bg-blue-500 text-white rounded-lg font-semibold">
            {page}
          </span>
          <button
            onClick={() => setPage(page + 1)}
            className="px-4 py-2 bg-white border-2 border-gray-300 rounded-lg font-medium text-gray-700 hover:bg-gray-50 hover:border-blue-400 transition-all"
          >
            Próxima →
          </button>
        </div>
      )}
    </div>
  )
}
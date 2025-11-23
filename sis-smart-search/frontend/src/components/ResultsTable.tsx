export default function ResultsTable({ rows = [], total = 0, pageSize, sort, setSort, page, setPage }: { rows?: any[], total?: number, pageSize: number, sort: string, setSort: (v: string) => void, page: number, setPage: (n: number) => void }) {
  const getStatusStyle = (status: string) => {
    const s = status?.toLowerCase() || ''
    if (s.includes('novo')) return 'bg-blue-100 text-blue-800 border-blue-300'
    if (s.includes('progresso') || s.includes('atribuído')) return 'bg-orange-100 text-orange-800 border-orange-300'
    if (s.includes('pendente')) return 'bg-yellow-100 text-yellow-800 border-yellow-300'
    if (s.includes('solucionado')) return 'bg-green-100 text-green-800 border-green-300'
    if (s.includes('fechado')) return 'bg-gray-100 text-gray-800 border-gray-300'
    return 'bg-gray-100 text-gray-600 border-gray-200'
  }
  const getStatusDate = (r: any) => {
    const status = (r.status || '').toLowerCase()
    if (status.includes('fechado') && r.data_fechamento) return { label: 'Data Fechamento', date: r.data_fechamento, color: 'text-gray-600' }
    if (status.includes('solucionado') && r.data_solucao) return { label: 'Data Solução', date: r.data_solucao, color: 'text-green-600' }
    return { label: 'Última Modificação', date: r.data_modificacao, color: 'text-blue-600' }
  }
  const totalPages = Math.ceil(total / pageSize)
  const startItem = (page - 1) * pageSize + 1
  const endItem = Math.min(page * pageSize, total)
  const getPageNumbers = () => {
    const pages: (number | string)[] = []
    if (totalPages <= 7) { for (let i = 1; i <= totalPages; i++) pages.push(i) }
    else if (page <= 4) pages.push(1, 2, 3, 4, 5, '...', totalPages)
    else if (page >= totalPages - 3) pages.push(1, '...', totalPages - 4, totalPages - 3, totalPages - 2, totalPages - 1, totalPages)
    else pages.push(1, '...', page - 1, page, page + 1, '...', totalPages)
    return pages
  }
  const formatDateTime = (dateStr: string) => {
    if (!dateStr) return 'N/A'
    const date = new Date(dateStr)
    return date.toLocaleString('pt-BR', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' })
  }
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold text-gray-800">Resultados <span className="text-blue-600">({total})</span></h2>
        <div className="flex gap-2">
          <button onClick={() => setSort('score')} className={`px-4 py-2 rounded-lg font-medium transition-all ${sort === 'score' ? 'bg-blue-500 text-white shadow-md' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'}`}>🎯 Relevância</button>
          <button onClick={() => setSort('recent')} className={`px-4 py-2 rounded-lg font-medium transition-all ${sort === 'recent' ? 'bg-blue-500 text-white shadow-md' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'}`}>🕐 Recentes</button>
        </div>
      </div>
      <div className="space-y-3">
        {rows && rows.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            <svg className="mx-auto h-12 w-12 text-gray-400 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
            <p className="text-lg font-medium">Nenhum resultado encontrado</p>
            <p className="text-sm mt-1">Tente ajustar sua busca ou filtros</p>
          </div>
        ) : (
          rows.map(r => {
            const hasHighlight = !!(r.highlight && r.highlight.trim())
            const isNumericTitle = !hasHighlight && r.titulo && String(r.titulo).trim() === String(r.id)
            const displayTitle = isNumericTitle ? (r.descricao || `Ticket #${r.id}`) : (r.titulo || `Ticket #${r.id}`)
            const statusDateInfo = getStatusDate(r)
            return (
              <div key={r.id} onClick={() => window.open(r.url, '_blank')} className="group bg-white border border-gray-200 rounded-xl p-5 hover:shadow-xl hover:border-blue-300 transition-all duration-300 cursor-pointer">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-3 mb-3">
                      <span className="inline-flex items-center px-3 py-1 rounded-lg bg-blue-50 text-blue-700 font-mono text-sm font-semibold">#{r.id}</span>
                      <span className={`inline-flex items-center px-3 py-1 rounded-lg border text-xs font-semibold ${getStatusStyle(r.status)}`}>{r.status}</span>
                    </div>
                    <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-3 mb-3 border border-blue-100">
                      <div className="flex items-start gap-2">
                        <span className="text-xs font-semibold text-blue-600 uppercase tracking-wide min-w-[70px]">Título:</span>
                        <span className="text-sm text-gray-900 font-medium flex-1" title={r.titulo}>{displayTitle}</span>
                      </div>
                    </div>
                    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
                      <div className="bg-gray-50 rounded-lg p-2 border border-gray-200"><span className="text-xs font-semibold text-gray-500 uppercase tracking-wide block mb-1">Entidade</span><p className="text-sm text-gray-900 font-medium truncate" title={r.entidade}>{r.entidade || 'N/A'}</p></div>
                      <div className="bg-gray-50 rounded-lg p-2 border border-gray-200"><span className="text-xs font-semibold text-gray-500 uppercase tracking-wide block mb-1">Categoria</span><p className="text-sm text-gray-900 font-medium truncate" title={r.categoria}>{r.categoria || 'N/A'}</p></div>
                      <div className="bg-gray-50 rounded-lg p-2 border border-gray-200"><span className="text-xs font-semibold text-gray-500 uppercase tracking-wide block mb-1">Requerente</span><p className="text-sm text-gray-900 font-medium truncate" title={r.requerente}>{r.requerente || 'N/A'}</p></div>
                      <div className="bg-gray-50 rounded-lg p-2 border border-gray-200"><span className="text-xs font-semibold text-gray-500 uppercase tracking-wide block mb-1">Técnico</span><p className="text-sm text-gray-900 font-medium truncate" title={r.tecnico}>{r.tecnico || 'N/A'}</p></div>
                      <div className="bg-gray-50 rounded-lg p-2 border border-gray-200"><span className="text-xs font-semibold text-gray-500 uppercase tracking-wide block mb-1">Grupo</span><p className="text-sm text-gray-900 font-medium truncate" title={r.grupo}>{r.grupo || 'N/A'}</p></div>
                    </div>
                  </div>
                  <div className="flex-shrink-0 flex flex-col gap-2 min-w-[180px]">
                    <div className="bg-blue-50 rounded-lg p-3 border border-blue-200"><span className="text-xs font-semibold text-blue-600 uppercase tracking-wide block mb-1">Data Abertura</span><p className="text-sm text-gray-900 font-medium">{formatDateTime(r.data_criacao)}</p></div>
                    <div className={`rounded-lg p-3 border ${statusDateInfo.color === 'text-gray-600' ? 'bg-gray-50 border-gray-200' : statusDateInfo.color === 'text-green-600' ? 'bg-green-50 border-green-200' : 'bg-blue-50 border-blue-200'}`}>
                      <span className={`text-xs font-semibold uppercase tracking-wide block mb-1 ${statusDateInfo.color}`}>{statusDateInfo.label}</span>
                      <p className="text-sm text-gray-900 font-medium">{formatDateTime(statusDateInfo.date)}</p>
                    </div>
                  </div>
                </div>
              </div>
            )
          })
        )}
      </div>
      {total > 0 && (
        <div className="flex items-center justify-between border-t border-gray-200 pt-4 mt-6">
          <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
            <div><p className="text-sm text-gray-700">Exibindo <span className="font-medium">{startItem}</span> a <span className="font-medium">{endItem}</span> de <span className="font-medium">{total}</span> linhas</p></div>
            <div>
              <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
                <button onClick={() => setPage(Math.max(1, page - 1))} disabled={page === 1} className="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"><span className="sr-only">Anterior</span><svg className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor"><path fillRule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clipRule="evenodd" /></svg></button>
                {getPageNumbers().map((p, i) => (
                  <button key={i} onClick={() => typeof p === 'number' && setPage(p)} disabled={p === '...'} className={`relative inline-flex items-center px-4 py-2 border text-sm font-medium ${p === page ? 'z-10 bg-blue-50 border-blue-500 text-blue-600' : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50'} ${p === '...' ? 'cursor-default' : ''}`}>{p}</button>
                ))}
                <button onClick={() => setPage(Math.min(totalPages, page + 1))} disabled={page === totalPages} className="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"><span className="sr-only">Próxima</span><svg className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor"><path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" /></svg></button>
              </nav>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
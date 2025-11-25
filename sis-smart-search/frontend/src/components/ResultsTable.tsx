import { Target, Clock } from "lucide-react";
import ResultRow from "./ResultRow";

export default function ResultsTable({ rows = [], total = 0, pageSize, sort, setSort, page, setPage, query }: { rows?: any[], total?: number, pageSize: number, sort: string, setSort: (v: string) => void, page: number, setPage: (n: number) => void, query?: string }) {
  const visualStyle: 'cards' | 'grid' | 'zebra' = 'grid'
  const glpiUrl = (id: number) => `http://cau.ppiratini.intra.rs.gov.br/glpi/front/ticket.form.php?id=${id}`

  const getStatusStyle = (status: string) => {
    const s = status?.toLowerCase() || ''
    if (s.includes('novo')) return 'bg-blue-500/20 text-blue-400 border-blue-400/30'
    if (s.includes('progresso') || s.includes('atribuído')) return 'bg-orange-500/20 text-orange-400 border-orange-400/30'
    if (s.includes('pendente')) return 'bg-yellow-500/20 text-yellow-400 border-yellow-400/30'
    if (s.includes('solucionado')) return 'bg-green-500/20 text-green-400 border-green-400/30'
    if (s.includes('fechado')) return 'bg-slate-500/20 text-slate-400 border-slate-400/30'
    return 'bg-slate-500/20 text-slate-400 border-slate-400/30'
  }

  // Função para determinar qual data mostrar baseado no status
  const getStatusDate = (r: any) => {
    const status = (r.status || '').toLowerCase()

    // Se está fechado, mostra data de fechamento
    if (status.includes('fechado') && r.data_fechamento) {
      return {
        label: 'Data Fechamento',
        date: r.data_fechamento,
        color: 'text-slate-400'
      }
    }

    // Se está solucionado, mostra data de solução
    if (status.includes('solucionado') && r.data_solucao) {
      return {
        label: 'Data Solução',
        date: r.data_solucao,
        color: 'text-green-400'
      }
    }

    // Caso contrário, mostra data de última modificação
    return {
      label: 'Última Modificação',
      date: r.data_modificacao,
      color: 'text-blue-400'
    }
  }

  const formatDateTime = (dateStr: string) => {
    if (!dateStr) return 'N/A'
    const date = new Date(dateStr)
    return date.toLocaleString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const totalPages = Math.ceil(total / pageSize)
  const startItem = (page - 1) * pageSize + 1
  const endItem = Math.min(page * pageSize, total)

  // Pagination Logic
  const getPageNumbers = () => {
    const pages = []
    if (totalPages <= 7) {
      for (let i = 1; i <= totalPages; i++) pages.push(i)
    } else {
      if (page <= 4) {
        pages.push(1, 2, 3, 4, 5, '...', totalPages)
      } else if (page >= totalPages - 3) {
        pages.push(1, '...', totalPages - 4, totalPages - 3, totalPages - 2, totalPages - 1, totalPages)
      } else {
        pages.push(1, '...', page - 1, page, page + 1, '...', totalPages)
      }
    }
    return pages
  }

  return (
    <div className="bg-slate-800/30 backdrop-blur-sm rounded-xl border border-slate-700/50 shadow-xl">
      <div className="p-6 border-b border-slate-700/50">
        <div className="flex items-center justify-between">
          <h2 className="text-xl text-white">
            Resultados <span className="text-blue-400">({total})</span>
          </h2>

          <div className="flex gap-2">
            <button
              onClick={() => setSort('score')}
              className={`px-4 py-2 rounded-lg transition-all ${sort === 'score'
                ? 'bg-blue-600 text-white shadow-lg'
                : 'bg-slate-700/50 text-slate-400 hover:bg-slate-700'
                }`}
            >
              <div className="flex items-center gap-2">
                <Target className="w-4 h-4" />
                <span className="text-sm">Relevância</span>
              </div>
            </button>

            <button
              onClick={() => setSort('recent')}
              className={`px-4 py-2 rounded-lg transition-all ${sort === 'recent'
                ? 'bg-blue-600 text-white shadow-lg'
                : 'bg-slate-700/50 text-slate-400 hover:bg-slate-700'
                }`}
            >
              <div className="flex items-center gap-2">
                <Clock className="w-4 h-4" />
                <span className="text-sm">Recentes</span>
              </div>
            </button>
          </div>
        </div>
      </div>

      <div className="divide-y divide-slate-700/50">
        {rows.length === 0 ? (
          <div className="text-center py-12 text-slate-500">
            <Target className="mx-auto h-12 w-12 text-slate-600 mb-3" />
            <p className="text-lg font-medium">Nenhum resultado encontrado</p>
            <p className="text-sm mt-1">Tente ajustar sua busca ou filtros</p>
          </div>
        ) : (
          rows.map((r) => (
            <ResultRow
              key={r.id}
              r={r}
              query={query}
              visualStyle={visualStyle}
              glpiUrl={glpiUrl}
              getStatusStyle={getStatusStyle}
              formatDateTime={formatDateTime}
            />
          ))
        )}
      </div>

      {/* Pagination */}
      {total > 0 && (
        <div className="p-6 border-t border-slate-700/50 flex items-center justify-between">
          <div className="text-sm text-slate-400">
            Mostrando <span className="font-medium text-slate-300">{startItem}</span> a <span className="font-medium text-slate-300">{endItem}</span> de <span className="font-medium text-slate-300">{total}</span> resultados
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => setPage(Math.max(1, page - 1))}
              disabled={page === 1}
              className="px-4 py-2 bg-slate-700/50 text-slate-400 rounded-lg hover:bg-slate-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Anterior
            </button>

            {getPageNumbers().map((p, i) => (
              <button
                key={i}
                onClick={() => typeof p === 'number' && setPage(p)}
                disabled={p === '...'}
                className={`px-4 py-2 rounded-lg transition-colors ${p === page
                  ? 'bg-blue-600 text-white shadow-lg'
                  : 'bg-slate-700/50 text-slate-400 hover:bg-slate-700'
                  } ${p === '...' ? 'cursor-default' : ''}`}
              >
                {p}
              </button>
            ))}

            <button
              onClick={() => setPage(Math.min(totalPages, page + 1))}
              disabled={page === totalPages}
              className="px-4 py-2 bg-slate-700/50 text-slate-400 rounded-lg hover:bg-slate-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Próximo
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
//

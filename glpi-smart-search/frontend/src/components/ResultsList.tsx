import { Target, Clock, Building2, Tag, User, Users } from "lucide-react";

export default function ResultsList({ rows, total, pageSize, sort, setSort, page, setPage }: { rows: any[], total: number, pageSize: number, sort: string, setSort: (v: string) => void, page: number, setPage: (n: number) => void }) {
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
                    rows.map(r => {
                        const hasHighlight = !!(r.highlight && r.highlight.trim())
                        const isNumericTitle = !hasHighlight && r.titulo && String(r.titulo).trim() === String(r.id)
                        const displayTitle = isNumericTitle ? (r.descricao || `Ticket #${r.id}`) : (r.titulo || `Ticket #${r.id}`)
                        const statusDateInfo = getStatusDate(r)

                        return (
                            <div
                                key={r.id}
                                onClick={() => window.open(r.url || glpiUrl(r.id), '_blank')}
                                className="p-6 hover:bg-slate-700/20 transition-colors group cursor-pointer"
                            >
                                <div className="flex items-start gap-4">
                                    <div className="flex-1 space-y-4">
                                        {/* Header */}
                                        <div className="flex items-center gap-3">
                                            <div className="bg-blue-500/20 text-blue-400 px-3 py-1 rounded-lg border border-blue-400/30 text-sm">
                                                #{r.id}
                                            </div>
                                            <div className={`px-3 py-1 rounded-lg border text-sm ${getStatusStyle(r.status)}`}>
                                                {r.status}
                                            </div>
                                        </div>

                                        {/* Title */}
                                        <div className="text-lg text-slate-200 group-hover:text-white transition-colors">
                                            <span className="text-slate-500 text-sm mr-2">TÍTULO:</span>
                                            {displayTitle}
                                        </div>

                                        {/* Details Grid */}
                                        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
                                            <div className="space-y-1">
                                                <div className="text-xs text-slate-500 uppercase flex items-center gap-1">
                                                    <Building2 className="w-3 h-3" />
                                                    Entidade
                                                </div>
                                                <div className="text-sm text-slate-300 truncate" title={r.entidade}>{r.entidade || 'N/A'}</div>
                                            </div>

                                            <div className="space-y-1">
                                                <div className="text-xs text-slate-500 uppercase flex items-center gap-1">
                                                    <Tag className="w-3 h-3" />
                                                    Categoria
                                                </div>
                                                <div className="text-sm text-slate-300 truncate" title={r.categoria}>{r.categoria || 'N/A'}</div>
                                            </div>

                                            <div className="space-y-1">
                                                <div className="text-xs text-slate-500 uppercase flex items-center gap-1">
                                                    <User className="w-3 h-3" />
                                                    Requerente
                                                </div>
                                                <div className="text-sm text-slate-300 truncate" title={r.requerente}>{r.requerente || 'N/A'}</div>
                                            </div>

                                            <div className="space-y-1">
                                                <div className="text-xs text-slate-500 uppercase flex items-center gap-1">
                                                    <User className="w-3 h-3" />
                                                    Técnico
                                                </div>
                                                <div className="text-sm text-slate-300 truncate" title={r.tecnico}>{r.tecnico || 'N/A'}</div>
                                            </div>

                                            <div className="space-y-1">
                                                <div className="text-xs text-slate-500 uppercase flex items-center gap-1">
                                                    <Users className="w-3 h-3" />
                                                    Grupo
                                                </div>
                                                <div className="text-sm text-slate-300 truncate" title={r.grupo}>{r.grupo || 'N/A'}</div>
                                            </div>
                                        </div>
                                    </div>

                                    {/* Dates */}
                                    <div className="text-right space-y-3 shrink-0 min-w-[140px]">
                                        <div>
                                            <div className="text-xs text-blue-400 uppercase mb-1">Data Abertura</div>
                                            <div className="text-sm text-slate-300">{formatDateTime(r.data_criacao)}</div>
                                        </div>
                                        <div>
                                            <div className={`text-xs uppercase mb-1 ${statusDateInfo.color === 'text-green-400' ? 'text-green-400' : 'text-blue-400'}`}>
                                                {statusDateInfo.label}
                                            </div>
                                            <div className="text-sm text-slate-300">{formatDateTime(statusDateInfo.date)}</div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        )
                    })
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

import { useState, useMemo } from "react"
import { Building2, Tag, User, Users } from "lucide-react"
import { useInView } from "../hooks/useInView"
import { computeHighlights } from "../utils/highlightTerms"
import styles from "../styles/highlight.module.css"
import descStyles from "../styles/description.module.css"

export default function ResultRow({ r, query, visualStyle, glpiUrl, getStatusStyle, formatDateTime }: { r: any, query?: string, visualStyle: 'cards' | 'grid' | 'zebra', glpiUrl: (id: number) => string, getStatusStyle: (s: string) => string, formatDateTime: (d: string) => string }) {
  const { ref, inView } = useInView<HTMLDivElement>()
  const [expanded, setExpanded] = useState(false)
  const hasHighlight = !!(r.highlight && r.highlight.trim())
  const isNumericTitle = !hasHighlight && r.titulo && String(r.titulo).trim() === String(r.id)
  const displayTitle = isNumericTitle ? (r.descricao || `Ticket #${r.id}`) : (r.titulo || `Ticket #${r.id}`)
  const rowBg = visualStyle === 'zebra' ? (r.id % 2 === 0 ? 'bg-slate-800/25' : 'bg-slate-800/10') : ''
  const cellBase = 'space-y-1'
  const cellCards = 'rounded-lg border border-slate-600/40 bg-slate-800/40 shadow-sm p-3'
  const cellGrid = 'rounded-md border border-slate-700/40 bg-slate-800/20 p-2'
  const valueZebra = 'bg-slate-700/30 rounded px-2 py-1'
  const cellClass = visualStyle === 'cards' ? `${cellBase} ${cellCards}` : visualStyle === 'grid' ? `${cellBase} ${cellGrid}` : cellBase
  const valueClass = visualStyle === 'zebra' ? valueZebra : 'text-sm text-slate-300 truncate'
  const titleParts = useMemo(() => (inView && query ? computeHighlights(displayTitle, query) : null), [inView, query, displayTitle])
  const entidadeParts = useMemo(() => (inView && query ? computeHighlights(r.entidade || 'N/A', query) : null), [inView, query, r.entidade])
  const categoriaParts = useMemo(() => (inView && query ? computeHighlights(r.categoria || 'N/A', query) : null), [inView, query, r.categoria])
  const requerenteParts = useMemo(() => (inView && query ? computeHighlights(r.requerente || 'N/A', query) : null), [inView, query, r.requerente])
  const tecnicoParts = useMemo(() => (inView && query ? computeHighlights(r.tecnico || 'N/A', query) : null), [inView, query, r.tecnico])
  const previewText = r.descricao_preview || r.descricao || ''
  const fullText = r.descricao_full || r.descricao || ''
  const previewParts = useMemo(() => (inView && query ? computeHighlights(previewText, query) : null), [inView, query, previewText])
  const fullParts = useMemo(() => (inView && query ? computeHighlights(fullText, query) : null), [inView, query, fullText])
  const status = (r.status || '').toLowerCase()
  const statusDateInfo = status.includes('fechado') && r.data_fechamento ? { label: 'Data Fechamento', date: r.data_fechamento, color: 'text-slate-400' } : (status.includes('solucionado') && r.data_solucao ? { label: 'Data Solução', date: r.data_solucao, color: 'text-green-400' } : { label: 'Última Modificação', date: r.data_modificacao, color: 'text-blue-400' })
  return (
    <div
      onClick={() => window.open(r.url || glpiUrl(r.id), '_blank')}
      className={`p-6 hover:bg-slate-700/20 transition-colors group cursor-pointer ${rowBg}`}
      ref={ref}
    >
      <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4">
        <div className="flex-1 space-y-4">
          <div className="flex flex-wrap items-center gap-3">
            <div className="bg-blue-500/20 text-blue-400 px-3 py-1 rounded-lg border border-blue-400/30 text-sm">#{r.id}</div>
            <div className={`px-3 py-1 rounded-lg border text-sm ${getStatusStyle(r.status)}`}>{r.status}</div>
            <div className="rounded-lg border border-slate-700/40 bg-slate-800/20 px-3 py-2 text-slate-200">
              <span className="text-slate-500 text-xs mr-2 uppercase">Título</span>
              <span className="text-sm">{titleParts ? renderParts(titleParts) : displayTitle}</span>
            </div>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-5">
            <div className={cellClass}>
              <div className="text-xs text-slate-500 uppercase flex items-center gap-1"><Building2 className="w-3 h-3" />Entidade</div>
              <div className={valueClass} title={r.entidade}>{visualStyle === 'zebra' ? (r.entidade || 'N/A') : <span className="text-sm text-slate-300 truncate">{entidadeParts ? renderParts(entidadeParts) : (r.entidade || 'N/A')}</span>}</div>
            </div>
            <div className={cellClass}>
              <div className="text-xs text-slate-500 uppercase flex items-center gap-1"><Tag className="w-3 h-3" />Categoria</div>
              <div className={valueClass} title={r.categoria}>{visualStyle === 'zebra' ? (r.categoria || 'N/A') : <span className="text-sm text-slate-300 truncate">{categoriaParts ? renderParts(categoriaParts) : (r.categoria || 'N/A')}</span>}</div>
            </div>
            <div className={cellClass}>
              <div className="text-xs text-slate-500 uppercase flex items-center gap-1"><User className="w-3 h-3" />Requerente</div>
              <div className={valueClass} title={r.requerente}>{visualStyle === 'zebra' ? (r.requerente || 'N/A') : <span className="text-sm text-slate-300 truncate">{requerenteParts ? renderParts(requerenteParts) : (r.requerente || 'N/A')}</span>}</div>
            </div>
            <div className={cellClass}>
              <div className="text-xs text-slate-500 uppercase flex items-center gap-1"><User className="w-3 h-3" />Técnico</div>
              <div className={valueClass} title={r.tecnico}>{visualStyle === 'zebra' ? (r.tecnico || 'N/A') : <span className="text-sm text-slate-300 truncate">{tecnicoParts ? renderParts(tecnicoParts) : (r.tecnico || 'N/A')}</span>}</div>
            </div>
            <div className={cellClass}>
              <div className="text-xs text-slate-500 uppercase flex items-center gap-1"><Users className="w-3 h-3" />Grupo</div>
              <div className={valueClass} title={r.grupo}>{visualStyle === 'zebra' ? (r.grupo || 'N/A') : <span className="text-sm text-slate-300 truncate">{r.grupo || 'N/A'}</span>}</div>
            </div>
          </div>
          {previewText && (
            <div className="mt-2 text-sm text-slate-300">
              <div className={expanded ? "" : descStyles.clamp3}>
                {expanded
                  ? (fullParts ? renderParts(fullParts) : fullText)
                  : (previewParts ? renderParts(previewParts) : previewText)
                }
              </div>
              <button onClick={(e) => { e.stopPropagation(); setExpanded(!expanded) }} className="mt-1 text-blue-400 hover:text-blue-300 text-xs">
                {expanded ? 'ver menos' : 'ver mais'}
              </button>
            </div>
          )}
        </div>
        <div className="flex flex-col gap-2 md:text-right md:items-end shrink-0 min-w-[180px]">
          <div className="rounded-lg border border-slate-700/40 bg-slate-800/20 px-3 py-2 w-full">
            <div className="text-xs text-blue-400 uppercase">Data Abertura</div>
            <div className="text-sm text-slate-300">{formatDateTime(r.data_criacao)}</div>
          </div>
          <div className="rounded-lg border border-slate-700/40 bg-slate-800/20 px-3 py-2 w-full">
            <div className={`text-xs uppercase ${statusDateInfo.color === 'text-green-400' ? 'text-green-400' : 'text-blue-400'}`}>{statusDateInfo.label}</div>
            <div className="text-sm text-slate-300">{formatDateTime(statusDateInfo.date)}</div>
          </div>
        </div>
      </div>
    </div>
  )
}

function renderParts(parts: ReturnType<typeof computeHighlights>) {
  return (
    <>
      {parts.map((p, idx) => p.highlight ? <span key={idx} className={styles.highlight} aria-label="termo destacado">{p.text}</span> : <span key={idx}>{p.text}</span>)}
    </>
  )
}


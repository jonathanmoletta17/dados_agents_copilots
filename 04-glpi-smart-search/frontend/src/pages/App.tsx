import { useEffect, useMemo, useState } from 'react'
import SearchBar from '../components/SearchBar'
import FilterChips from '../components/FilterChips'
import ResultsTable from '../components/ResultsTable'
import StatsPanel from '../components/StatsPanel'
import ErrorBoundary from '../components/ErrorBoundary'
import { exportUrl, searchApi, statsApi } from '../services/api'

export default function App() {
  const [q, setQ] = useState('')
  const [filters, setFilters] = useState<Record<string,string>>({})
  const [rows, setRows] = useState<any[]>([])
  const [page, setPage] = useState(1)
  const [size] = useState(20)
  const [sort, setSort] = useState('score')
  const [stats, setStats] = useState({ status: [], entidade: [] } as any)

  useEffect(()=>{(async()=>{try{const s=await statsApi();setStats(s)}catch(e){setStats({ status: [], entidade: [] })}})()},[])
  useEffect(()=>{
    const t = setTimeout(async ()=>{
      try{const r=await searchApi({ q, ...filters, page, size, sort });setRows(r)}catch(e){setRows([])}} , 250)
    return ()=>clearTimeout(t)
  },[q,filters,page,size,sort])

  const params = useMemo(()=>({ q, ...filters, page, size, sort }),[q,filters,page,size,sort])

  return (
    <div className="max-w-[1400px] mx-auto px-4 py-4">
      <div className="text-2xl font-bold mb-4">GLPI Smart Search</div>
      <ErrorBoundary>
        <SearchBar value={q} onChange={setQ} />
      </ErrorBoundary>
      <div className="mt-3">
        <ErrorBoundary>
          <FilterChips filters={filters} setFilters={setFilters} />
        </ErrorBoundary>
      </div>
      <div className="flex items-center gap-2 mt-3">
        <a className="px-3 py-2 border rounded" href={exportUrl(params,'csv')} target="_blank">exportar CSV</a>
        <a className="px-3 py-2 border rounded" href={exportUrl(params,'xlsx')} target="_blank">exportar XLSX</a>
      </div>
      <div className="grid grid-cols-12 gap-6 mt-4">
        <div className="col-span-9">
          <ErrorBoundary>
            <ResultsTable rows={rows} sort={sort} setSort={setSort} page={page} setPage={setPage} />
          </ErrorBoundary>
        </div>
        <div className="col-span-3">
          <ErrorBoundary>
            <StatsPanel stats={stats} />
          </ErrorBoundary>
        </div>
      </div>
    </div>
  )
}
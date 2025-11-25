import { useState, useEffect } from 'react'
import SearchBar from '../components/SearchBar'
import ResultsList from '../components/ResultsList'
import { MetricsCards } from '../components/MetricsCards'
import FilterChips from '../components/FilterChips'
import { SearchHeader } from '../components/SearchHeader'
import { searchApi, statsApi } from '../services/api'

export default function App() {
  const [q, setQ] = useState('')
  const [results, setResults] = useState([])
  const [total, setTotal] = useState(0)
  const [stats, setStats] = useState<any>(null)
  const [filters, setFilters] = useState<Record<string, any>>({})
  const [page, setPage] = useState(1)
  const [sort, setSort] = useState('score')
  const pageSize = 20

  useEffect(() => {
    const fetchStats = () => {
      statsApi(['novo', 'pendente', 'solucionado', 'fechado'])
        .then(setStats)
        .catch(err => {
          console.error('statsApi failed', err)
        })
    }

    // Initial fetch
    fetchStats()

    // Poll every 5 seconds for auto-update
    const interval = setInterval(fetchStats, 5000)

    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    const timer = setTimeout(() => {
      searchApi({ q, ...filters, page, size: pageSize, sort }).then(data => {
        setResults(data.items)
        setTotal(data.total)
      }).catch(err => {
        console.error('searchApi failed', err)
        setResults([])
        setTotal(0)
      })
    }, 300)
    return () => clearTimeout(timer)
  }, [q, filters, page, sort])

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      <SearchHeader />

      <div className="max-w-[1600px] mx-auto p-6 space-y-6">
        {/* Search Bar */}
        <SearchBar
          value={q}
          onChange={setQ}
          onFilterChange={(f: Record<string, any>) => { setPage(1); setFilters(f) }}
        />

        {/* Stats Panel */}
        {stats && (
          <MetricsCards stats={stats} />
        )}

        {/* Active Filters */}
        {Object.keys(filters).length > 0 && (
          <FilterChips filters={filters} onRemove={(k) => {
            const newF = { ...filters }
            delete newF[k]
            setPage(1)
            setFilters(newF)
          }} />
        )}

        {/* Results */}
        <ResultsList
          rows={results}
          total={total}
          pageSize={pageSize}
          sort={sort}
          setSort={setSort}
          page={page}
          setPage={setPage}
          query={q}
        />
      </div>
    </div>
  )
}

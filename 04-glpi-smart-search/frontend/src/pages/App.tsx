import { useState, useEffect } from 'react'
import SearchBar from '../components/SearchBar'
import ResultsTable from '../components/ResultsTable'
import StatsPanel from '../components/StatsPanel'
import FilterChips from '../components/FilterChips'
import { searchApi, statsApi } from '../services/api'

export default function App() {
  const [q, setQ] = useState('')
  const [results, setResults] = useState([])
  const [stats, setStats] = useState<any>(null)
  const [filters, setFilters] = useState({})
  const [page, setPage] = useState(1)
  const [sort, setSort] = useState('score')

  useEffect(() => {
    statsApi().then(setStats).catch(() => { })
  }, [])

  useEffect(() => {
    const timer = setTimeout(() => {
      searchApi({ q, ...filters, page, size: 20, sort }).then(setResults).catch(() => setResults([]))
    }, 300)
    return () => clearTimeout(timer)
  }, [q, filters, page, sort])

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="bg-gradient-to-r from-blue-600 to-blue-500 text-white shadow-lg">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <h1 className="text-2xl font-bold">GLPI Smart Search</h1>
          <p className="text-blue-100 text-sm mt-1">Sistema Inteligente de Busca de Tickets</p>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* Search Bar */}
        <div className="mb-8">
          <SearchBar
            value={q}
            onChange={setQ}
            onFilterChange={setFilters}
          />
        </div>

        {/* Stats Panel */}
        {stats && (
          <div className="mb-8">
            <StatsPanel stats={stats} />
          </div>
        )}

        {/* Active Filters */}
        {Object.keys(filters).length > 0 && (
          <div className="mb-6">
            <FilterChips filters={filters} onRemove={(k) => {
              const newF = { ...filters }
              delete newF[k]
              setFilters(newF)
            }} />
          </div>
        )}

        {/* Results */}
        <div className="bg-white rounded-2xl shadow-lg p-6">
          <ResultsTable
            rows={results}
            sort={sort}
            setSort={setSort}
            page={page}
            setPage={setPage}
          />
        </div>
      </main>
    </div>
  )
}
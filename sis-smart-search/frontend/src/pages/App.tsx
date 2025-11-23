import { useState, useEffect } from 'react';
import SearchHeader from '../components/SearchHeader';
import SearchBar from '../components/SearchBar';
import ResultsTable from '../components/ResultsTable';
import MetricsCards from '../components/MetricsCards';
import FilterChips from '../components/FilterChips';
import { searchApi, statsApi } from '../services/api';

export default function App() {
  const [q, setQ] = useState('');
  const [results, setResults] = useState([]);
  const [total, setTotal] = useState(0);
  const [stats, setStats] = useState<any>(null);
  const [filters, setFilters] = useState<Record<string, any>>({});
  const [page, setPage] = useState(1);
  const [sort, setSort] = useState('score');
  const pageSize = 20;

  useEffect(() => {
    statsApi().then(setStats).catch(err => {
      console.error('sis statsApi failed', err);
    });
  }, []);

  useEffect(() => {
    const timer = setTimeout(() => {
      searchApi({ q, ...filters, page, size: pageSize, sort }).then(data => {
        setResults(data.items || []);
        setTotal(data.total);
      }).catch(err => {
        console.error('sis searchApi failed', err);
        setResults([]);
        setTotal(0);
      });
    }, 300);
    return () => clearTimeout(timer);
  }, [q, filters, page, sort]);

  const handleNavigate = (view: string) => {
    console.log('Navigate to:', view);
    // Implementar navegação aqui
  };

  const handleFilterRemove = (key: string) => {
    const newFilters = { ...filters };
    delete newFilters[key];
    setFilters(newFilters);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      <SearchHeader onNavigate={handleNavigate} />

      <main className="max-w-[1600px] mx-auto px-6 py-8 space-y-6">
        <SearchBar value={q} onChange={setQ} onFilterChange={setFilters} />

        {stats && <MetricsCards stats={stats} />}

        {Object.keys(filters).length > 0 && (
          <FilterChips filters={filters} onRemove={handleFilterRemove} />
        )}

        <div className="bg-slate-800/30 backdrop-blur-sm rounded-xl shadow-2xl border border-slate-700/50">
          <ResultsTable
            rows={results}
            total={total}
            pageSize={pageSize}
            sort={sort}
            setSort={setSort}
            page={page}
            setPage={setPage}
          />
        </div>
      </main>
    </div>
  );
}
import { X } from 'lucide-react';

interface FilterChipsProps {
  filters: Record<string, any>;
  onRemove: (key: string) => void;
}

const filterLabels: Record<string, string> = {
  status: 'Status',
  entidade: 'Entidade',
  categoria: 'Categoria',
  tecnico: 'Técnico',
  requerente: 'Requerente',
  dt_ini: 'Data Início',
  dt_fim: 'Data Fim',
};

export default function FilterChips({ filters, onRemove }: FilterChipsProps) {
  const activeFilters = Object.entries(filters).filter(([_, value]) => value && value !== '');

  if (activeFilters.length === 0) return null;

  return (
    <div className="flex flex-wrap gap-2">
      <span className="text-sm text-slate-400 mr-2 self-center">Filtros ativos:</span>
      {activeFilters.map(([key, value]) => (
        <div
          key={key}
          className="inline-flex items-center gap-2 px-3 py-1.5 bg-slate-700/50 backdrop-blur-sm text-slate-200 rounded-lg text-sm border border-slate-600/50 hover:bg-slate-700 transition-colors"
        >
          <span className="font-medium text-slate-300">{filterLabels[key] || key}:</span>
          <span>{value}</span>
          <button
            onClick={() => onRemove(key)}
            className="ml-1 hover:bg-slate-600/50 rounded-full p-0.5 transition-colors"
          >
            <X className="w-3 h-3" />
          </button>
        </div>
      ))}
    </div>
  );
}
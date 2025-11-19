export default function FilterChips({ filters, setFilters }: { filters: Record<string,string>, setFilters: (f:Record<string,string>)=>void }) {
  const update = (k:string,v:string)=> setFilters({ ...filters, [k]: v })
  const Chip = ({label,k}:{label:string,k:string})=> (
    <div className="flex items-center gap-2">
      <span className="text-sm text-gray-600">{label}</span>
      <input className="border rounded px-2 py-1" value={filters[k]||''} onChange={e=>update(k,e.target.value)} />
    </div>
  )
  return (
    <div className="flex flex-wrap gap-4">
      <Chip label="status" k="status" />
      <Chip label="técnico" k="tecnico" />
      <Chip label="entidade" k="entidade" />
      <Chip label="categoria" k="categoria" />
      <Chip label="início" k="dt_ini" />
      <Chip label="fim" k="dt_fim" />
    </div>
  )
}
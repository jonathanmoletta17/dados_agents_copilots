export default function StatsPanel({ stats }: { stats: { status: [string, number][], entidade: [string, number][] } }) {
  return (
    <div className="border rounded p-3">
      <h3 className="font-semibold mb-2">estatísticas</h3>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <div className="font-medium">por status</div>
          {stats.status.map(([s,c],i)=> (
            <div key={i} className="flex justify-between"><span>{s}</span><span>{c}</span></div>
          ))}
        </div>
        <div>
          <div className="font-medium">principais entidades</div>
          {stats.entidade.map(([s,c],i)=> (
            <div key={i} className="flex justify-between"><span>{s}</span><span>{c}</span></div>
          ))}
        </div>
      </div>
    </div>
  )
}
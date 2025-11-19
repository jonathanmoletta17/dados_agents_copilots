export default function StatsPanel({ stats }: { stats: any }) {
  const statusData = stats?.status || []

  // Map status names to Portuguese and colors
  const statusMap: Record<string, { label: string; color: string; icon: string }> = {
    'novo': { label: 'Novos', color: 'bg-blue-500', icon: '📬' },
    'processando (atribuído)': { label: 'Em Progresso', color: 'bg-orange-500', icon: '⚡' },
    'processando (planejado)': { label: 'Em Progresso', color: 'bg-orange-500', icon: '⚡' },
    'pendente': { label: 'Pendentes', color: 'bg-yellow-500', icon: '⏱️' },
    'solucionado': { label: 'Resolvidos', color: 'bg-green-500', icon: '✅' },
    'fechado': { label: 'Fechados', color: 'bg-gray-500', icon: '🔒' }
  }

  // Aggregate related statuses
  const aggregated = statusData.reduce((acc: any[], [name, count]: [string, number]) => {
    const normalized = name.toLowerCase()
    const config = statusMap[normalized] || { label: name, color: 'bg-gray-400', icon: '📊' }

    const existing = acc.find(x => x.label === config.label)
    if (existing) {
      existing.count += count
    } else {
      acc.push({ label: config.label, count, color: config.color, icon: config.icon })
    }
    return acc
  }, [])

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {aggregated.slice(0, 4).map((item: any, i: number) => (
        <div
          key={i}
          className="bg-white rounded-xl shadow-md hover:shadow-xl transition-all duration-300 overflow-hidden border-l-4"
          style={{
            borderLeftColor: item.color.replace('bg-', '#') === item.color ? '#64B5F6' :
              item.color.includes('blue') ? '#2196F3' :
                item.color.includes('orange') ? '#FF9800' :
                  item.color.includes('yellow') ? '#FFC107' :
                    item.color.includes('green') ? '#4CAF50' : '#9E9E9E'
          }}
        >
          <div className="p-5">
            <div className="flex items-center justify-between mb-3">
              <span className="text-2xl">{item.icon}</span>
              <span className={`text-xs font-semibold px-3 py-1 rounded-full text-white ${item.color}`}>
                {item.count}
              </span>
            </div>
            <h3 className="text-gray-600 text-sm font-medium mb-1">{item.label}</h3>
            <p className="text-2xl font-bold text-gray-800">{item.count}</p>
          </div>
          <div className={`h-1 ${item.color}`}></div>
        </div>
      ))}
    </div>
  )
}
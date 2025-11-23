import { Clock, Target, TrendingUp, Zap } from "lucide-react";

const stats = [
  {
    label: "Taxa de Resolução",
    value: "93.8%",
    icon: Target,
    color: "from-green-500 to-emerald-600",
    progress: 93.8,
  },
  {
    label: "SLA Cumprido",
    value: "96%",
    icon: TrendingUp,
    color: "from-blue-500 to-cyan-600",
    progress: 96,
  },
  {
    label: "Tempo Médio",
    value: "4.2h",
    icon: Clock,
    color: "from-purple-500 to-violet-600",
    progress: 75,
  },
  {
    label: "Produtividade",
    value: "Alta",
    icon: Zap,
    color: "from-yellow-500 to-orange-600",
    progress: 88,
  },
];

export function QuickStats() {
  return (
    <div className="h-full bg-slate-800/50 backdrop-blur-sm rounded-xl border border-slate-700/50 p-4 shadow-xl flex flex-col gap-3">
      <h2 className="text-white mb-1 flex items-center gap-2">
        <div className="w-1 h-6 bg-gradient-to-b from-blue-500 to-purple-600 rounded-full" />
        Indicadores Rápidos
      </h2>
      
      {stats.map((stat, index) => {
        const Icon = stat.icon;
        return (
          <div
            key={index}
            className={`bg-gradient-to-br ${stat.color} rounded-lg p-3 shadow-lg border border-white/20 hover:scale-105 transition-transform`}
          >
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <Icon className="w-5 h-5 text-white" />
                <span className="text-sm text-white/90">{stat.label}</span>
              </div>
              <span className="text-xl text-white tabular-nums">
                {stat.value}
              </span>
            </div>
            <div className="h-1.5 bg-white/20 rounded-full overflow-hidden">
              <div
                className="h-full bg-white rounded-full transition-all duration-1000"
                style={{ width: `${stat.progress}%` }}
              />
            </div>
          </div>
        );
      })}

      {/* Total Summary */}
      <div className="mt-auto bg-slate-900/50 rounded-lg p-3 border border-slate-700/30">
        <div className="text-xs text-slate-400 mb-2">Resumo do Período</div>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <div className="text-2xl text-white tabular-nums">413</div>
            <div className="text-xs text-slate-400">Total de Tickets</div>
          </div>
          <div>
            <div className="text-2xl text-green-400 tabular-nums">387</div>
            <div className="text-xs text-slate-400">Concluídos</div>
          </div>
        </div>
      </div>
    </div>
  );
}

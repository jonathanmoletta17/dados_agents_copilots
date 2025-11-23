import { Target, TrendingUp, Clock, Wrench } from "lucide-react";

const stats = [
  {
    label: "Taxa de Resolução",
    value: "95.2%",
    icon: Target,
    color: "from-green-500 to-emerald-600",
    progress: 95.2,
  },
  {
    label: "Tempo Médio",
    value: "6.5h",
    icon: Clock,
    color: "from-purple-500 to-violet-600",
    progress: 70,
  },
  {
    label: "Produtividade",
    value: "Alta",
    icon: TrendingUp,
    color: "from-blue-500 to-cyan-600",
    progress: 92,
  },
];

export function QuickStats() {
  return (
    <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl border border-slate-700/50 p-4 shadow-xl flex flex-col gap-3 shrink-0">
      <h2 className="text-white mb-1 flex items-center gap-2">
        <div className="w-1 h-6 bg-gradient-to-b from-blue-500 to-purple-600 rounded-full" />
        Indicadores
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
      <div className="bg-slate-900/50 rounded-lg p-3 border border-slate-700/30">
        <div className="flex items-center gap-2 mb-2">
          <Wrench className="w-4 h-4 text-blue-400" />
          <div className="text-xs text-slate-400">Resumo do Período</div>
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <div className="text-2xl text-white tabular-nums">685</div>
            <div className="text-xs text-slate-400">Total</div>
          </div>
          <div>
            <div className="text-2xl text-green-400 tabular-nums">653</div>
            <div className="text-xs text-slate-400">Resolvidos</div>
          </div>
        </div>
      </div>
    </div>
  );
}

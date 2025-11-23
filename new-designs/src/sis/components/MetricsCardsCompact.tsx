import { TrendingUp, Clock, AlertCircle, CalendarClock, CheckCircle2 } from "lucide-react";

const metrics = [
  {
    id: "new",
    label: "Novos",
    value: 1,
    icon: TrendingUp,
    color: "from-blue-500 to-blue-600",
    shadowColor: "shadow-blue-500/20",
  },
  {
    id: "attendance",
    label: "Em Atendimento",
    value: 13,
    icon: Clock,
    color: "from-cyan-500 to-cyan-600",
    shadowColor: "shadow-cyan-500/20",
  },
  {
    id: "pending",
    label: "Pendentes",
    value: 7,
    icon: AlertCircle,
    color: "from-yellow-500 to-yellow-600",
    shadowColor: "shadow-yellow-500/20",
  },
  {
    id: "planned",
    label: "Planejados",
    value: 11,
    icon: CalendarClock,
    color: "from-orange-500 to-orange-600",
    shadowColor: "shadow-orange-500/20",
  },
  {
    id: "resolved",
    label: "Resolvidos",
    value: 653,
    icon: CheckCircle2,
    color: "from-green-500 to-green-600",
    shadowColor: "shadow-green-500/20",
  },
];

export function MetricsCardsCompact() {
  const total = metrics.reduce((sum, m) => sum + m.value, 0);
  
  return (
    <div className="grid grid-cols-5 gap-4">
      {metrics.map((metric) => {
        const Icon = metric.icon;
        const percentage = ((metric.value / total) * 100).toFixed(1);
        
        return (
          <div
            key={metric.id}
            className={`bg-gradient-to-br ${metric.color} rounded-xl p-4 shadow-xl ${metric.shadowColor} border border-white/20 hover:scale-105 transition-transform duration-300`}
          >
            <div className="flex items-center justify-between mb-2">
              <Icon className="w-8 h-8 text-white/90" />
              <div className="text-xs text-white/80 bg-white/20 px-2 py-1 rounded-full backdrop-blur-sm">
                {percentage}%
              </div>
            </div>
            
            <div className="text-white">
              <div className="text-4xl tabular-nums mb-0.5">
                {metric.value}
              </div>
              <div className="text-sm text-white/90">
                {metric.label}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}

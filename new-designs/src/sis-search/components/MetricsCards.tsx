import { Lock, Clock, CheckCircle2, AlertCircle } from "lucide-react";

const metrics = [
  {
    id: "closed",
    label: "Fechados",
    value: 4822,
    icon: Lock,
    color: "from-slate-600 to-slate-700",
    borderColor: "border-slate-600/30",
  },
  {
    id: "progress",
    label: "Em andamento (atribuído)",
    value: 26,
    icon: Clock,
    color: "from-slate-600 to-slate-700",
    borderColor: "border-slate-600/30",
  },
  {
    id: "resolved",
    label: "Resolvidos",
    value: 24,
    icon: CheckCircle2,
    color: "from-green-500 to-green-600",
    borderColor: "border-green-500/30",
  },
  {
    id: "pending",
    label: "Pendentes",
    value: 10,
    icon: AlertCircle,
    color: "from-yellow-500 to-yellow-600",
    borderColor: "border-yellow-500/30",
  },
];

export function MetricsCards() {
  return (
    <div className="grid grid-cols-4 gap-6">
      {metrics.map((metric) => {
        const Icon = metric.icon;
        return (
          <div
            key={metric.id}
            className={`bg-gradient-to-br ${metric.color} rounded-xl p-6 shadow-xl border ${metric.borderColor} hover:scale-105 transition-transform duration-300`}
          >
            <div className="flex items-center justify-between mb-3">
              <Icon className="w-8 h-8 text-white/90" />
              <div className="bg-white/20 backdrop-blur-sm px-3 py-1 rounded-full">
                <span className="text-xs text-white/90">Total</span>
              </div>
            </div>
            
            <div className="text-white">
              <div className="text-4xl tabular-nums mb-1">
                {metric.value.toLocaleString('pt-BR')}
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

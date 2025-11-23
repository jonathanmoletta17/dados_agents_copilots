import { TrendingUp, Clock, AlertCircle, CheckCircle2 } from "lucide-react";

const metrics = [
  {
    id: "new",
    label: "Novos",
    value: 2,
    icon: TrendingUp,
    color: "blue",
    gradient: "from-blue-500 to-blue-600",
    bgColor: "bg-blue-50",
    iconBg: "bg-blue-100",
    textColor: "text-blue-700",
  },
  {
    id: "progress",
    label: "Em Progresso",
    value: 20,
    icon: Clock,
    color: "orange",
    gradient: "from-orange-500 to-orange-600",
    bgColor: "bg-orange-50",
    iconBg: "bg-orange-100",
    textColor: "text-orange-700",
  },
  {
    id: "pending",
    label: "Pendentes",
    value: 4,
    icon: AlertCircle,
    color: "yellow",
    gradient: "from-yellow-500 to-yellow-600",
    bgColor: "bg-yellow-50",
    iconBg: "bg-yellow-100",
    textColor: "text-yellow-700",
  },
  {
    id: "resolved",
    label: "Resolvidos",
    value: 387,
    icon: CheckCircle2,
    color: "green",
    gradient: "from-green-500 to-green-600",
    bgColor: "bg-green-50",
    iconBg: "bg-green-100",
    textColor: "text-green-700",
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
            className={`${metric.bgColor} rounded-xl p-6 shadow-sm border border-${metric.color}-100 hover:shadow-md transition-all duration-200 group`}
          >
            <div className="flex items-start justify-between mb-4">
              <div className={`${metric.iconBg} p-3 rounded-lg group-hover:scale-110 transition-transform duration-200`}>
                <Icon className={`w-6 h-6 ${metric.textColor}`} />
              </div>
              <div className={`text-xs ${metric.textColor} opacity-75 px-2 py-1 rounded-full bg-white/50`}>
                Tickets
              </div>
            </div>
            
            <div className="space-y-1">
              <div className={`text-4xl ${metric.textColor}`}>
                {metric.value}
              </div>
              <div className={`text-sm ${metric.textColor} opacity-75`}>
                {metric.label}
              </div>
            </div>

            {/* Progress bar */}
            <div className="mt-4 h-1.5 bg-white/60 rounded-full overflow-hidden">
              <div 
                className={`h-full bg-gradient-to-r ${metric.gradient} rounded-full transition-all duration-500`}
                style={{ width: `${Math.min((metric.value / 400) * 100, 100)}%` }}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
}

import { TrendingUp, Clock, AlertCircle, CheckCircle2 } from "lucide-react";
import { GeneralStats } from "../types/api";

interface MetricsCardsProps {
  stats?: GeneralStats;
  isLoading?: boolean;
}

export function MetricsCards({ stats, isLoading }: MetricsCardsProps) {
  const metrics = [
    {
      id: "new",
      label: "Novos",
      value: stats?.novos ?? 0,
      icon: TrendingUp,
      color: "blue",
      gradient: "from-blue-600 to-blue-700",
      bgColor: "bg-blue-600",
      iconBg: "bg-blue-500/20",
      textColor: "text-white",
      borderColor: "border-blue-500",
    },
    {
      id: "progress",
      label: "Em Progresso",
      value: stats?.em_progresso ?? 0,
      icon: Clock,
      color: "orange",
      gradient: "from-orange-600 to-orange-700",
      bgColor: "bg-orange-500",
      iconBg: "bg-orange-400/20",
      textColor: "text-white",
      borderColor: "border-orange-400",
    },
    {
      id: "pending",
      label: "Pendentes",
      value: stats?.pendentes ?? 0,
      icon: AlertCircle,
      color: "yellow",
      gradient: "from-yellow-500 to-yellow-600",
      bgColor: "bg-yellow-500",
      iconBg: "bg-yellow-400/20",
      textColor: "text-white",
      borderColor: "border-yellow-400",
    },
    {
      id: "resolved",
      label: "Resolvidos",
      value: stats?.resolvidos ?? 0,
      icon: CheckCircle2,
      color: "green",
      gradient: "from-green-600 to-green-700",
      bgColor: "bg-green-500",
      iconBg: "bg-green-400/20",
      textColor: "text-white",
      borderColor: "border-green-400",
    },
  ];

  if (isLoading) {
    return (
      <div className="grid grid-cols-4 gap-4">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="bg-white rounded-xl p-4 border border-slate-200 animate-pulse h-24" />
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-4 gap-4">
      {metrics.map((metric) => {
        const Icon = metric.icon;
        return (
          <div
            key={metric.id}
            className={`${metric.bgColor} rounded-xl p-4 shadow-sm border ${metric.borderColor} hover:shadow-md transition-all duration-200 group`}
          >
            <div className="flex items-center gap-4">
              <div className={`${metric.iconBg} p-3 rounded-lg group-hover:scale-110 transition-transform duration-200`}>
                <Icon className={`w-6 h-6 ${metric.textColor}`} />
              </div>

              <div className="flex-1">
                <div className={`text-3xl font-bold ${metric.textColor} leading-none`}>
                  {metric.value}
                </div>
                <div className={`text-sm ${metric.textColor} opacity-90 font-medium mt-1`}>
                  {metric.label}
                </div>
              </div>
            </div>

            {/* Progress bar */}
            <div className="mt-3 h-1.5 bg-black/10 rounded-full overflow-hidden">
              <div
                className={`h-full bg-white/80 rounded-full transition-all duration-500`}
                style={{ width: `${Math.min((metric.value / 400) * 100, 100)}%` }}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
}

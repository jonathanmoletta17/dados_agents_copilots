import { CheckCircle, Clock, AlertCircle, XCircle, FileText } from "lucide-react";

interface MetricsCardsProps {
    stats: {
        fechados: number;
        em_andamento: number;
        resolvidos: number;
        pendentes: number;
        total: number;
    } | null;
}

export default function MetricsCards({ stats }: MetricsCardsProps) {
    if (!stats) return null;

    const metricsData = [
        {
            label: "Fechados",
            value: stats.fechados,
            icon: CheckCircle,
            color: "from-green-500 to-green-600",
            borderColor: "border-green-500/30",
        },
        {
            label: "Em Andamento",
            value: stats.em_andamento,
            icon: Clock,
            color: "from-blue-500 to-blue-600",
            borderColor: "border-blue-500/30",
        },
        {
            label: "Resolvidos",
            value: stats.resolvidos,
            icon: AlertCircle,
            color: "from-cyan-500 to-cyan-600",
            borderColor: "border-cyan-500/30",
        },
        {
            label: "Pendentes",
            value: stats.pendentes,
            icon: XCircle,
            color: "from-orange-500 to-orange-600",
            borderColor: "border-orange-500/30",
        },
        {
            label: "Total de Tickets",
            value: stats.total,
            icon: FileText,
            color: "from-slate-600 to-slate-700",
            borderColor: "border-slate-600/30",
        },
    ];

    return (
        <div className="grid grid-cols-5 gap-4">
            {metricsData.map((metric) => {
                const Icon = metric.icon;
                return (
                    <div
                        key={metric.label}
                        className={`bg-gradient-to-br ${metric.color} rounded-xl p-5 shadow-xl border ${metric.borderColor} hover:scale-105 transition-transform duration-300`}
                    >
                        <div className="flex items-center justify-between mb-2">
                            <Icon className="w-7 h-7 text-white/90" />
                        </div>

                        <div className="text-white">
                            <div className="text-3xl tabular-nums mb-1">
                                {metric.value?.toLocaleString('pt-BR') || '0'}
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

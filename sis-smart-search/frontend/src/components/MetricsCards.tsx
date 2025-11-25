import { Mail, Clock, CalendarClock, XCircle, CheckCircle } from "lucide-react";

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

    const statusArr: Array<[string, number]> = (stats as any)?.status || []
    const normalize = (s: string) => (s || '').toLowerCase()
    const sumSynonyms = (synonyms: string[]) => statusArr.reduce((acc, [name, count]) => acc + (synonyms.includes(normalize(name)) ? count : 0), 0)

    const fechados = sumSynonyms(['fechado']) || (stats as any).fechados || 0
    const solucionados = sumSynonyms(['solucionado']) || 0
    const emAndamento = sumSynonyms(['atribuido','em andamento (atribuído)','em andamento (atribuido)']) || (stats as any).em_andamento || 0
    const planejado = sumSynonyms(['planejado','em andamento (planejado)']) || (stats as any).planejado || 0
    const pendentes = sumSynonyms(['pendente']) || (stats as any).pendentes || 0
    const resolvidosTotal = fechados + solucionados

    const metricsData = [
        {
            label: "Novos",
            value: (stats as any)?.novos ?? sumSynonyms(['novo']),
            icon: Mail,
            color: "from-green-500 to-green-600",
            borderColor: "border-green-500/30",
        },
        {
            label: "Em Andamento",
            value: (stats as any)?.em_atendimento ?? emAndamento,
            icon: Clock,
            color: "from-blue-500 to-blue-600",
            borderColor: "border-blue-500/30",
        },
        {
            label: "Planejado",
            value: (stats as any)?.planejados ?? planejado,
            icon: CalendarClock,
            color: "from-cyan-500 to-cyan-600",
            borderColor: "border-cyan-500/30",
        },
        {
            label: "Pendentes",
            value: (stats as any)?.pendentes ?? pendentes,
            icon: XCircle,
            color: "from-orange-500 to-orange-600",
            borderColor: "border-orange-500/30",
        },
        {
            label: "Resolvidos",
            value: (stats as any)?.resolvidos ?? resolvidosTotal,
            icon: CheckCircle,
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

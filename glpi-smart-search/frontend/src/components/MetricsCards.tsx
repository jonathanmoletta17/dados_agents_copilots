import { Mail, Clock, CheckCircle2, Lock, AlertTriangle, Activity, ArrowRight, Check } from "lucide-react";

interface MetricsCardsProps {
    stats: any;
}

export function MetricsCards({ stats }: MetricsCardsProps) {
    const statusData = stats?.status || [];

    // Map status names to internal IDs and config
    const statusConfig: Record<string, { id: string; label: string; icon: any; color: string; borderColor: string }> = {
        'novo': {
            id: 'new',
            label: 'Novos',
            icon: Mail,
            color: 'from-green-500 to-green-600',
            borderColor: 'border-green-500/30'
        },
        'processando (atribuído)': {
            id: 'progress',
            label: 'Em andamento',
            icon: ArrowRight,
            color: 'from-slate-600 to-slate-700',
            borderColor: 'border-slate-600/30'
        },
        'processando (planejado)': {
            id: 'planned',
            label: 'Planejado',
            icon: Clock,
            color: 'from-slate-600 to-slate-700',
            borderColor: 'border-slate-600/30'
        },
        'pendente': {
            id: 'pending',
            label: 'Pendentes',
            icon: AlertTriangle,
            color: 'from-yellow-500 to-yellow-600',
            borderColor: 'border-yellow-500/30'
        },
        'solucionado': {
            id: 'resolved',
            label: 'Resolvidos',
            icon: Check,
            color: 'from-blue-500 to-blue-600',
            borderColor: 'border-blue-500/30'
        },
        'fechado': {
            id: 'closed',
            label: 'Fechados',
            icon: Lock,
            color: 'from-slate-600 to-slate-700',
            borderColor: 'border-slate-600/30'
        }
    };

    // Aggregate data
    const aggregated = statusData.reduce((acc: any[], [name, count]: [string, number]) => {
        const normalized = name.toLowerCase();
        const config = statusConfig[normalized];

        if (config) {
            const existing = acc.find(x => x.id === config.id);
            if (existing) {
                existing.value += count;
            } else {
                acc.push({ ...config, value: count });
            }
        }
        return acc;
    }, []);

    // Ensure we have at least the main 4 metrics if data is missing, or just show what we have
    // For consistency with design, we might want to enforce specific order or items
    // But for now, let's render what we have, sorted by importance/design order if possible

    const order = ['new', 'pending', 'resolved', 'closed'];
    aggregated.sort((a: any, b: any) => order.indexOf(a.id) - order.indexOf(b.id));

    return (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {aggregated.map((metric: any) => {
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

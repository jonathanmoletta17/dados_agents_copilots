import { CheckCircle, Clock, XCircle, Users } from "lucide-react";

const statusData = [
  {
    id: "available",
    label: "Disponíveis",
    value: 4,
    icon: CheckCircle,
    color: "from-green-500 to-green-600",
    borderColor: "border-green-500/30",
  },
  {
    id: "busy",
    label: "Ocupados",
    value: 1,
    icon: Clock,
    color: "from-orange-500 to-orange-600",
    borderColor: "border-orange-500/30",
  },
  {
    id: "offline",
    label: "Offline",
    value: 0,
    icon: XCircle,
    color: "from-slate-600 to-slate-700",
    borderColor: "border-slate-600/30",
  },
  {
    id: "total",
    label: "Total de Carregadores",
    value: 5,
    icon: Users,
    color: "from-blue-600 to-blue-700",
    borderColor: "border-blue-600/30",
  },
];

export function StatusOverview() {
  return (
    <div className="grid grid-cols-4 gap-6">
      {statusData.map((status) => {
        const Icon = status.icon;
        return (
          <div
            key={status.id}
            className={`bg-gradient-to-br ${status.color} rounded-xl p-6 shadow-xl border ${status.borderColor} hover:scale-105 transition-transform duration-300`}
          >
            <div className="flex items-center justify-between mb-3">
              <Icon className="w-8 h-8 text-white/90" />
              <div className="bg-white/20 backdrop-blur-sm px-3 py-1 rounded-full">
                <span className="text-xs text-white/90">Agora</span>
              </div>
            </div>
            
            <div className="text-white">
              <div className="text-4xl tabular-nums mb-1">
                {status.value}
              </div>
              <div className="text-sm text-white/90">
                {status.label}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}

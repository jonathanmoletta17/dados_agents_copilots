import { Ticket, Clock, User, Activity } from "lucide-react";
import { NewTicketItem } from "../types/api";

interface RecentTicketsCompactProps {
  tickets?: NewTicketItem[];
}

const recentActivity = [
  { action: "Ticket resolvido", tech: "Carlos A.", time: "5 min" },
  { action: "Novo atendimento", tech: "Wellington G.", time: "12 min" },
  { action: "SLA atingido", tech: "Silas V.", time: "18 min" },
];

export function RecentTicketsCompact({ tickets }: RecentTicketsCompactProps) {
  return (
    <div className="h-full bg-slate-800/50 backdrop-blur-sm rounded-xl border border-slate-700/50 p-4 shadow-xl flex flex-col gap-4">
      {/* Recent Tickets */}
      <div className="flex-1 flex flex-col">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-white flex items-center gap-2">
            <Ticket className="w-5 h-5 text-blue-400" />
            Tickets Novos
          </h2>
          <div className="bg-blue-500/20 text-blue-400 px-2 py-1 rounded-full text-xs border border-blue-400/30">
            {tickets?.length ?? 0} tickets
          </div>
        </div>

        <div className="space-y-3 flex-1 overflow-y-auto pr-1">
          {tickets?.map((ticket) => (
            <div
              key={ticket.id}
              className="bg-slate-900/50 rounded-lg p-3 border border-slate-700/30 hover:border-blue-500/50 transition-all group"
            >
              <div className="flex items-start justify-between mb-2">
                <div className={`bg-gradient-to-r from-blue-500 to-blue-600 px-2 py-1 rounded text-xs text-white`}>
                  #{ticket.id}
                </div>
                <div className={`text-xs px-2 py-0.5 rounded-full ${ticket.prioridade === "Alta"
                    ? "bg-red-500/20 text-red-400 border border-red-400/30"
                    : "bg-yellow-500/20 text-yellow-400 border border-yellow-400/30"
                  }`}>
                  {ticket.prioridade || 'Normal'}
                </div>
              </div>

              <p className="text-xs text-slate-300 leading-relaxed line-clamp-3 mb-2">
                {ticket.titulo}
              </p>

              <div className="flex items-center justify-between text-xs text-slate-500">
                <div className="flex items-center gap-1">
                  <User className="w-3 h-3" />
                  <span className="truncate max-w-[120px]">{ticket.solicitante}</span>
                </div>
                <div className="flex items-center gap-1">
                  <Clock className="w-3 h-3" />
                  <span>{ticket.data}</span>
                </div>
              </div>
            </div>
          ))}
          {!tickets && (
            <div className="space-y-3 animate-pulse">
              {[1, 2, 3].map(i => (
                <div key={i} className="h-24 bg-slate-800 rounded-lg" />
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-slate-900/50 rounded-lg p-3 border border-slate-700/30">
        <div className="flex items-center gap-2 mb-3">
          <Activity className="w-4 h-4 text-green-400" />
          <h3 className="text-sm text-white">Atividade Recente</h3>
        </div>

        <div className="space-y-2">
          {recentActivity.map((activity, index) => (
            <div key={index} className="flex items-center justify-between text-xs">
              <div className="flex items-center gap-2">
                <div className="w-1.5 h-1.5 rounded-full bg-green-400" />
                <span className="text-slate-400">{activity.action}</span>
              </div>
              <span className="text-slate-500">{activity.time}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Live Status Indicator */}
      <div className="bg-gradient-to-r from-green-500/10 to-emerald-500/10 rounded-lg p-3 border border-green-500/30">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="relative">
              <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
              <div className="absolute inset-0 w-2 h-2 rounded-full bg-green-400 animate-ping" />
            </div>
            <span className="text-xs text-green-400">Sistema Online</span>
          </div>
          <span className="text-xs text-slate-400">9 técnicos ativos</span>
        </div>
      </div>
    </div>
  );
}

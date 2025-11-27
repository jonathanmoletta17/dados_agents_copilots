import { Ticket, Clock, User, Activity, Filter } from "lucide-react";
import { NewTicketItem } from "../types/api";
import { useMemo, useState } from "react";

interface RecentTicketsCompactProps {
  tickets?: NewTicketItem[];
}

const recentActivity = [
  { action: "Ticket resolvido", tech: "Carlos A.", time: "5 min" },
  { action: "Novo atendimento", tech: "Wellington G.", time: "12 min" },
  { action: "SLA atingido", tech: "Silas V.", time: "18 min" },
];

function TicketCard({ ticket }: { ticket: NewTicketItem }) {
    const [expanded, setExpanded] = useState(false);
    
    const hasDescription = !!ticket.descricao_full;
    
    return (
        <div
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

            <p className="text-xs text-slate-300 font-medium mb-1">
                {ticket.titulo}
            </p>
            
            {hasDescription && (
                <div className="mb-2">
                    <p className={`text-xs text-slate-400 leading-relaxed ${expanded ? '' : 'line-clamp-3'}`}>
                        {expanded ? ticket.descricao_full : ticket.descricao_preview}
                    </p>
                     <button 
                        onClick={(e) => { e.stopPropagation(); setExpanded(!expanded) }} 
                        className="mt-1 text-blue-400 hover:text-blue-300 text-[10px] font-medium uppercase tracking-wider"
                    >
                        {expanded ? 'ver menos' : 'ver mais'}
                    </button>
                </div>
            )}

            <div className="flex items-center justify-between text-xs text-slate-500 mt-2">
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
    );
}

export function RecentTicketsCompact({ tickets }: RecentTicketsCompactProps) {
  const [priority, setPriority] = useState<string>("");
  const filtered = useMemo(() => {
    if (!tickets) return tickets;
    if (!priority) return tickets;
    return tickets.filter((t) => (t.prioridade || "").toLowerCase() === priority.toLowerCase());
  }, [tickets, priority]);

  return (
    <div className="h-full bg-slate-800/50 backdrop-blur-sm rounded-xl border border-slate-700/40 p-4 shadow-xl flex flex-col gap-4">
      {/* Recent Tickets */}
      <div className="flex-1 flex flex-col">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-white flex items-center gap-2">
            <Ticket className="w-5 h-5 text-blue-400" />
            Tickets Novos
          </h2>
          <div className="flex items-center gap-2">
            <div className="hidden xl:flex items-center gap-1 text-xs text-slate-300 bg-slate-700/30 px-2 py-1 rounded">
              <Filter className="w-3 h-3" />
              <select className="bg-transparent outline-none" value={priority} onChange={(e) => setPriority(e.target.value)}>
                <option value="">Todas</option>
                <option value="baixa">Baixa</option>
                <option value="media">Média</option>
                <option value="alta">Alta</option>
                <option value="critica">Crítica</option>
              </select>
            </div>
            <div className="bg-blue-500/20 text-blue-400 px-2 py-1 rounded-full text-xs border border-blue-400/30">
              {(filtered?.length ?? 0)} tickets
            </div>
          </div>
        </div>

        <div className="space-y-3 flex-1 overflow-y-auto pr-1">
          {filtered?.map((ticket) => (
            <TicketCard key={ticket.id} ticket={ticket} />
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
          {recentActivity.map((item, i) => (
            <div key={i} className="flex items-center justify-between text-xs">
              <span className="text-slate-300">{item.action}</span>
              <div className="flex items-center gap-2">
                <span className="text-slate-500">{item.tech}</span>
                <span className="text-slate-600">{item.time}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
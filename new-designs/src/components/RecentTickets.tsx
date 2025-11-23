import { Ticket, Clock, User } from "lucide-react";

const tickets = [
  {
    id: "#11390",
    title: "INCIDENTE - Defeito Civil/ Tipo de Recuperação - Casa Mãe SFH ( L andiei)",
    author: "Andrei Ribeiro Taborda",
    date: "19/11/2025 15:23",
    status: "Novo",
    statusColor: "bg-blue-100 text-blue-700 border-blue-200",
  },
  {
    id: "#11389",
    title: "Acesso a Sistemas - Geral - OUTRO",
    author: "Moisés de Melo",
    date: "19/11/2025 16:05",
    status: "Novo",
    statusColor: "bg-blue-100 text-blue-700 border-blue-200",
  },
];

export function RecentTickets() {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl text-slate-700 flex items-center gap-2">
          <Ticket className="w-5 h-5 text-blue-600" />
          Tickets Novos
        </h2>
        <div className="bg-blue-100 text-blue-700 px-3 py-1 rounded-full text-sm">
          2 tickets
        </div>
      </div>

      <div className="space-y-4">
        {tickets.map((ticket) => (
          <div
            key={ticket.id}
            className="bg-white rounded-xl shadow-sm border border-slate-200 p-5 hover:shadow-md transition-all duration-200 group"
          >
            <div className="flex items-start justify-between mb-3">
              <div className="bg-blue-50 text-blue-700 px-3 py-1 rounded-lg text-sm border border-blue-100">
                {ticket.id}
              </div>
              <div className={`px-3 py-1 rounded-full text-xs border ${ticket.statusColor}`}>
                {ticket.status}
              </div>
            </div>

            <h3 className="text-sm text-slate-700 mb-4 leading-relaxed line-clamp-3 group-hover:text-blue-600 transition-colors">
              {ticket.title}
            </h3>

            <div className="space-y-2 text-xs text-slate-500">
              <div className="flex items-center gap-2">
                <User className="w-3.5 h-3.5" />
                <span>{ticket.author}</span>
              </div>
              <div className="flex items-center gap-2">
                <Clock className="w-3.5 h-3.5" />
                <span>{ticket.date}</span>
              </div>
            </div>

            <button className="mt-4 w-full bg-gradient-to-r from-blue-500 to-blue-600 text-white py-2 rounded-lg text-sm hover:from-blue-600 hover:to-blue-700 transition-all duration-200 shadow-sm hover:shadow-md">
              Ver Detalhes
            </button>
          </div>
        ))}

        {/* View all button */}
        <button className="w-full bg-slate-100 text-slate-600 py-3 rounded-xl text-sm hover:bg-slate-200 transition-colors border border-slate-200">
          Ver Todos os Tickets
        </button>
      </div>

      {/* Quick Stats */}
      <div className="bg-gradient-to-br from-blue-600 to-blue-700 rounded-xl p-5 text-white shadow-lg">
        <h3 className="text-sm opacity-90 mb-3">Estatísticas Rápidas</h3>
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-sm opacity-90">Taxa de Resolução</span>
            <span className="text-xl">93.8%</span>
          </div>
          <div className="h-2 bg-white/20 rounded-full overflow-hidden">
            <div className="h-full bg-white rounded-full" style={{ width: "93.8%" }} />
          </div>
          
          <div className="pt-3 border-t border-white/20 grid grid-cols-2 gap-3">
            <div>
              <div className="text-xs opacity-75">Tempo Médio</div>
              <div className="text-lg">4.2h</div>
            </div>
            <div>
              <div className="text-xs opacity-75">SLA Cumprido</div>
              <div className="text-lg">96%</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

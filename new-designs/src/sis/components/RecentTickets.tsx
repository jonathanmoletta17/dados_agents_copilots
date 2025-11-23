import { Ticket, Clock, User, Activity } from "lucide-react";

const tickets = [
  {
    id: "#4812/1",
    title: "TESTE // NAO MEXER",
    author: "Jonathan Nascimento Moletta",
    date: "06/10/2025",
    time: "01:57",
    status: "Novo",
    statusColor: "from-blue-500 to-blue-600",
  },
];

const recentActivity = [
  { action: "Manutenção concluída", tech: "Vera M.", time: "8 min", type: "success" },
  { action: "Em atendimento", tech: "Amanda N.", time: "15 min", type: "progress" },
  { action: "Novo chamado", tech: "Rodrigo P.", time: "23 min", type: "new" },
  { action: "Planejado", tech: "Thiago O.", time: "31 min", type: "planned" },
];

export function RecentTickets() {
  return (
    <div className="flex-1 bg-slate-800/50 backdrop-blur-sm rounded-xl border border-slate-700/50 p-4 shadow-xl flex flex-col gap-4 overflow-hidden">
      {/* Recent Tickets */}
      <div className="flex-1 flex flex-col min-h-0">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-white flex items-center gap-2">
            <Ticket className="w-5 h-5 text-blue-400" />
            Tickets Novos
          </h2>
          <div className="bg-blue-500/20 text-blue-400 px-2 py-1 rounded-full text-xs border border-blue-400/30">
            1 ticket
          </div>
        </div>

        <div className="space-y-3 flex-1 overflow-y-auto pr-1">
          {tickets.map((ticket) => (
            <div
              key={ticket.id}
              className="bg-slate-900/50 rounded-lg p-3 border border-slate-700/30 hover:border-blue-500/50 transition-all group"
            >
              <div className="flex items-start justify-between mb-2">
                <div className={`bg-gradient-to-r ${ticket.statusColor} px-2 py-1 rounded text-xs text-white`}>
                  {ticket.id}
                </div>
                <div className="bg-blue-500/20 text-blue-400 border border-blue-400/30 text-xs px-2 py-0.5 rounded-full">
                  {ticket.status}
                </div>
              </div>

              <p className="text-sm text-slate-300 leading-relaxed mb-3">
                {ticket.title}
              </p>

              <div className="space-y-1.5 text-xs text-slate-500">
                <div className="flex items-center gap-2">
                  <User className="w-3 h-3" />
                  <span className="truncate">{ticket.author}</span>
                </div>
                <div className="flex items-center gap-2">
                  <Clock className="w-3 h-3" />
                  <span>{ticket.date} às {ticket.time}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-slate-900/50 rounded-lg p-3 border border-slate-700/30 shrink-0">
        <div className="flex items-center gap-2 mb-3">
          <Activity className="w-4 h-4 text-green-400" />
          <h3 className="text-sm text-white">Atividade Recente</h3>
        </div>
        
        <div className="space-y-2">
          {recentActivity.map((activity, index) => {
            const getActivityColor = (type: string) => {
              switch(type) {
                case "success": return "bg-green-400";
                case "progress": return "bg-cyan-400";
                case "new": return "bg-blue-400";
                case "planned": return "bg-orange-400";
                default: return "bg-slate-400";
              }
            };

            return (
              <div key={index} className="flex items-center justify-between text-xs">
                <div className="flex items-center gap-2 flex-1 min-w-0">
                  <div className={`w-1.5 h-1.5 rounded-full ${getActivityColor(activity.type)}`} />
                  <span className="text-slate-400 truncate">{activity.action}</span>
                  <span className="text-slate-600">•</span>
                  <span className="text-slate-500">{activity.tech}</span>
                </div>
                <span className="text-slate-500 ml-2 shrink-0">{activity.time}</span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

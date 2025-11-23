import { Target, Clock, Building2, Tag, User, Users, Calendar } from "lucide-react";
import { useState } from "react";

const tickets = [
  {
    id: "#10203",
    status: "Em andamento (atribuído)",
    statusColor: "bg-orange-500/20 text-orange-400 border-orange-400/30",
    title: "TESTE // NÃO MEXER",
    entity: "CENTRAL DE ATENDI...",
    category: "NDD",
    requester: "Jonathan Nasciment...",
    technician: "User 1291",
    group: "N2",
    openDate: "22/10/2025, 16:52",
    updateDate: "20/11/2025, 10:37",
  },
  {
    id: "#11501",
    status: "Em andamento (atribuído)",
    statusColor: "bg-orange-500/20 text-orange-400 border-orange-400/30",
    title: "testrre",
    entity: "CENTRAL DE ATENDI...",
    category: "NDD",
    requester: "Jonathan Nasciment...",
    technician: "Jonathan Nasciment...",
    group: "N3",
    openDate: "19/11/2025, 23:27",
    updateDate: "19/11/2025, 23:29",
  },
  {
    id: "#11490",
    status: "Fechado",
    statusColor: "bg-slate-500/20 text-slate-400 border-slate-400/30",
    title: "Instalação de Sistema - Windows",
    entity: "CENTRAL DE ATENDI...",
    category: "Instalação",
    requester: "Maria Silva",
    technician: "Carlos Alberto",
    group: "N1",
    openDate: "18/11/2025, 14:20",
    updateDate: "19/11/2025, 09:15",
  },
];

export function ResultsList() {
  const [sortBy, setSortBy] = useState<"relevance" | "recent">("relevance");

  return (
    <div className="bg-slate-800/30 backdrop-blur-sm rounded-xl border border-slate-700/50 shadow-xl">
      <div className="p-6 border-b border-slate-700/50">
        <div className="flex items-center justify-between">
          <h2 className="text-xl text-white">
            Resultados <span className="text-blue-400">(11080)</span>
          </h2>
          
          <div className="flex gap-2">
            <button
              onClick={() => setSortBy("relevance")}
              className={`px-4 py-2 rounded-lg transition-all ${
                sortBy === "relevance"
                  ? "bg-blue-600 text-white shadow-lg"
                  : "bg-slate-700/50 text-slate-400 hover:bg-slate-700"
              }`}
            >
              <div className="flex items-center gap-2">
                <Target className="w-4 h-4" />
                <span className="text-sm">Relevância</span>
              </div>
            </button>
            
            <button
              onClick={() => setSortBy("recent")}
              className={`px-4 py-2 rounded-lg transition-all ${
                sortBy === "recent"
                  ? "bg-blue-600 text-white shadow-lg"
                  : "bg-slate-700/50 text-slate-400 hover:bg-slate-700"
              }`}
            >
              <div className="flex items-center gap-2">
                <Clock className="w-4 h-4" />
                <span className="text-sm">Recentes</span>
              </div>
            </button>
          </div>
        </div>
      </div>

      <div className="divide-y divide-slate-700/50">
        {tickets.map((ticket) => (
          <div
            key={ticket.id}
            className="p-6 hover:bg-slate-700/20 transition-colors group"
          >
            <div className="flex items-start gap-4">
              <div className="flex-1 space-y-4">
                {/* Header */}
                <div className="flex items-center gap-3">
                  <div className="bg-blue-500/20 text-blue-400 px-3 py-1 rounded-lg border border-blue-400/30 text-sm">
                    {ticket.id}
                  </div>
                  <div className={`px-3 py-1 rounded-lg border text-sm ${ticket.statusColor}`}>
                    {ticket.status}
                  </div>
                </div>

                {/* Title */}
                <div className="text-lg text-slate-200 group-hover:text-white transition-colors">
                  <span className="text-slate-500 text-sm mr-2">TÍTULO:</span>
                  {ticket.title}
                </div>

                {/* Details Grid */}
                <div className="grid grid-cols-5 gap-4">
                  <div className="space-y-1">
                    <div className="text-xs text-slate-500 uppercase flex items-center gap-1">
                      <Building2 className="w-3 h-3" />
                      Entidade
                    </div>
                    <div className="text-sm text-slate-300">{ticket.entity}</div>
                  </div>

                  <div className="space-y-1">
                    <div className="text-xs text-slate-500 uppercase flex items-center gap-1">
                      <Tag className="w-3 h-3" />
                      Categoria
                    </div>
                    <div className="text-sm text-slate-300">{ticket.category}</div>
                  </div>

                  <div className="space-y-1">
                    <div className="text-xs text-slate-500 uppercase flex items-center gap-1">
                      <User className="w-3 h-3" />
                      Requerente
                    </div>
                    <div className="text-sm text-slate-300">{ticket.requester}</div>
                  </div>

                  <div className="space-y-1">
                    <div className="text-xs text-slate-500 uppercase flex items-center gap-1">
                      <User className="w-3 h-3" />
                      Técnico
                    </div>
                    <div className="text-sm text-slate-300">{ticket.technician}</div>
                  </div>

                  <div className="space-y-1">
                    <div className="text-xs text-slate-500 uppercase flex items-center gap-1">
                      <Users className="w-3 h-3" />
                      Grupo
                    </div>
                    <div className="text-sm text-slate-300">{ticket.group}</div>
                  </div>
                </div>
              </div>

              {/* Dates */}
              <div className="text-right space-y-3 shrink-0">
                <div>
                  <div className="text-xs text-blue-400 uppercase mb-1">Data Abertura</div>
                  <div className="text-sm text-slate-300">{ticket.openDate}</div>
                </div>
                <div>
                  <div className="text-xs text-green-400 uppercase mb-1">Última Modificação</div>
                  <div className="text-sm text-slate-300">{ticket.updateDate}</div>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Pagination */}
      <div className="p-6 border-t border-slate-700/50 flex items-center justify-between">
        <div className="text-sm text-slate-400">
          Mostrando 1-3 de 11,080 resultados
        </div>
        <div className="flex gap-2">
          <button className="px-4 py-2 bg-slate-700/50 text-slate-400 rounded-lg hover:bg-slate-700 transition-colors">
            Anterior
          </button>
          <button className="px-4 py-2 bg-blue-600 text-white rounded-lg shadow-lg">
            1
          </button>
          <button className="px-4 py-2 bg-slate-700/50 text-slate-400 rounded-lg hover:bg-slate-700 transition-colors">
            2
          </button>
          <button className="px-4 py-2 bg-slate-700/50 text-slate-400 rounded-lg hover:bg-slate-700 transition-colors">
            3
          </button>
          <button className="px-4 py-2 bg-slate-700/50 text-slate-400 rounded-lg hover:bg-slate-700 transition-colors">
            Próximo
          </button>
        </div>
      </div>
    </div>
  );
}

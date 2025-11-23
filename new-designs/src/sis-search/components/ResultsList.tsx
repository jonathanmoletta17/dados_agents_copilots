import { Target, Clock, Building2, Tag, User, Users, Calendar } from "lucide-react";
import { useState } from "react";

const tickets = [
  {
    id: "#4890",
    status: "Fechado",
    statusColor: "bg-slate-500/20 text-slate-400 border-slate-400/30",
    title: "Marcenaria - skate de rodinhas - mesas",
    entity: "Departamento de Co...",
    category: "Conserto de Mobiliário",
    requester: "Lorena Fonseca Vieira",
    technician: "Anderson Rocha Car...",
    group: "GG-CONSERVACAO, ...",
    openDate: "13/11/2025, 17:31",
    closeDate: "20/11/2025, 12:40",
  },
  {
    id: "#4922",
    status: "Fechado",
    statusColor: "bg-slate-500/20 text-slate-400 border-slate-400/30",
    title: "Elétrica - Remoção provisória de arandelas",
    entity: "Departamento de Co...",
    category: "Remoção",
    requester: "Marcio Brum de Mello",
    technician: "Amanda Pinheiro No...",
    group: "GG-CONSERVACAO, ...",
    openDate: "14/11/2025, 17:40",
    closeDate: "20/11/2025, 12:40",
  },
  {
    id: "#4931",
    status: "Fechado",
    statusColor: "bg-slate-500/20 text-slate-400 border-slate-400/30",
    title: "Pintura - Sala de reuniões 2º andar",
    entity: "Departamento de Co...",
    category: "Pintura",
    requester: "Ana Costa Silva",
    technician: "Rodrigo Ludmann Pias",
    group: "GG-CONSERVACAO, ...",
    openDate: "15/11/2025, 09:15",
    closeDate: "19/11/2025, 16:30",
  },
];

export function ResultsList() {
  const [sortBy, setSortBy] = useState<"relevance" | "recent">("relevance");

  return (
    <div className="bg-slate-800/30 backdrop-blur-sm rounded-xl border border-slate-700/50 shadow-xl">
      <div className="p-6 border-b border-slate-700/50">
        <div className="flex items-center justify-between">
          <h2 className="text-xl text-white">
            Resultados <span className="text-blue-400">(4890)</span>
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
                  <div className="text-xs text-slate-400 uppercase mb-1">Data Fechamento</div>
                  <div className="text-sm text-slate-300">{ticket.closeDate}</div>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Pagination */}
      <div className="p-6 border-t border-slate-700/50 flex items-center justify-between">
        <div className="text-sm text-slate-400">
          Mostrando 1-3 de 4,890 resultados
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

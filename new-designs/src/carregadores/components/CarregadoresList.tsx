import { User, MapPin, Clock, Ticket } from "lucide-react";

const carregadores = [
  {
    id: 1,
    nome: "Carregador 1",
    status: "Disponível",
    statusColor: "bg-green-500",
    statusBg: "bg-green-500/20 text-green-400 border-green-400/30",
    localizacao: "Casa Civil 1005",
    tempo: "aguardando para iniciar o expediente",
    ref: "ref",
    ticket: "#4167",
  },
  {
    id: 2,
    nome: "Carregador 2",
    status: "Disponível",
    statusColor: "bg-green-500",
    statusBg: "bg-green-500/20 text-green-400 border-green-400/30",
    localizacao: "Casa Civil 1005",
    tempo: "aguardando para iniciar o expediente",
    ref: "ref",
    ticket: "#4170",
  },
  {
    id: 3,
    nome: "Carregador 3",
    status: "Ocupado",
    statusColor: "bg-orange-500",
    statusBg: "bg-orange-500/20 text-orange-400 border-orange-400/30",
    localizacao: "Casa Civil 1005",
    tempo: "aguardando para iniciar o expediente",
    ref: "",
    ticket: "#4228",
  },
  {
    id: 4,
    nome: "carregador 4",
    status: "Disponível",
    statusColor: "bg-green-500",
    statusBg: "bg-green-500/20 text-green-400 border-green-400/30",
    localizacao: "Casa Civil 1005",
    tempo: "aguardando para iniciar o expediente",
    ref: "ref",
    ticket: "#4021",
  },
  {
    id: 5,
    nome: "carregador 5",
    status: "Disponível",
    statusColor: "bg-green-500",
    statusBg: "bg-green-500/20 text-green-400 border-green-400/30",
    localizacao: "Casa Civil 1005",
    tempo: "aguardando para iniciar o expediente",
    ref: "ref",
    ticket: "#4170",
  },
];

export function CarregadoresList() {
  return (
    <div className="bg-slate-800/30 backdrop-blur-sm rounded-xl border border-slate-700/50 shadow-xl">
      <div className="p-6 border-b border-slate-700/50">
        <div className="flex items-center gap-2">
          <User className="w-5 h-5 text-blue-400" />
          <h2 className="text-xl text-white">Lista de Carregadores</h2>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-slate-700/50 bg-slate-900/50">
              <th className="text-left p-4 text-sm text-slate-400 uppercase tracking-wider">Nome</th>
              <th className="text-left p-4 text-sm text-slate-400 uppercase tracking-wider">Status</th>
              <th className="text-left p-4 text-sm text-slate-400 uppercase tracking-wider">Localização</th>
              <th className="text-left p-4 text-sm text-slate-400 uppercase tracking-wider">Tempo</th>
              <th className="text-left p-4 text-sm text-slate-400 uppercase tracking-wider">Ticket</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-700/50">
            {carregadores.map((carregador) => (
              <tr key={carregador.id} className="hover:bg-slate-700/20 transition-colors group">
                <td className="p-4">
                  <div className="flex items-center gap-3">
                    <div className={`w-10 h-10 rounded-lg bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center text-white shadow-md relative`}>
                      <User className="w-5 h-5" />
                      <div className={`absolute -bottom-1 -right-1 w-3 h-3 rounded-full ${carregador.statusColor} border-2 border-slate-800`} />
                    </div>
                    <span className="text-slate-200">{carregador.nome}</span>
                  </div>
                </td>
                <td className="p-4">
                  <div className={`inline-flex items-center gap-2 px-3 py-1 rounded-lg border text-sm ${carregador.statusBg}`}>
                    <div className={`w-2 h-2 rounded-full ${carregador.statusColor} animate-pulse`} />
                    {carregador.status}
                  </div>
                </td>
                <td className="p-4">
                  <div className="flex items-center gap-2 text-slate-300">
                    <MapPin className="w-4 h-4 text-slate-500" />
                    {carregador.localizacao}
                  </div>
                </td>
                <td className="p-4">
                  <div className="flex items-center gap-2 text-slate-300 text-sm">
                    <Clock className="w-4 h-4 text-slate-500" />
                    <span>{carregador.tempo}</span>
                    {carregador.ref && <span className="text-slate-500 ml-1">{carregador.ref}</span>}
                  </div>
                </td>
                <td className="p-4">
                  <div className="bg-blue-500/20 text-blue-400 px-3 py-1 rounded-lg border border-blue-400/30 text-sm inline-flex items-center gap-2">
                    <Ticket className="w-3 h-3" />
                    {carregador.ticket}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

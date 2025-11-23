import { Award, TrendingUp, Medal, Trophy } from "lucide-react";

const ranking = [
  { nome: "Carregador 3", tickets: 4, position: 1 },
  { nome: "Carregador 1", tickets: 2, position: 2 },
  { nome: "Carregador 2", tickets: 2, position: 3 },
  { nome: "carregador 4", tickets: 2, position: 4 },
  { nome: "carregador 5", tickets: 1, position: 5 },
];

export function CarregadoresRanking() {
  const getRankIcon = (position: number) => {
    if (position === 1) return <Trophy className="w-5 h-5 text-yellow-500" />;
    if (position === 2) return <Medal className="w-5 h-5 text-slate-400" />;
    if (position === 3) return <Medal className="w-5 h-5 text-amber-700" />;
    return null;
  };

  const getRankColor = (position: number) => {
    if (position === 1) return "from-yellow-500 to-yellow-600";
    if (position === 2) return "from-slate-400 to-slate-500";
    if (position === 3) return "from-amber-600 to-amber-700";
    return "from-blue-500 to-blue-600";
  };

  return (
    <div className="bg-slate-800/30 backdrop-blur-sm rounded-xl border border-slate-700/50 shadow-xl h-full">
      <div className="p-6 border-b border-slate-700/50">
        <div className="flex items-center gap-2 mb-1">
          <Award className="w-5 h-5 text-yellow-500" />
          <h2 className="text-xl text-white">Ranking de Carregadores</h2>
        </div>
        <p className="text-sm text-slate-400">(últimos 30 dias)</p>
      </div>

      <div className="p-6">
        {/* Top 3 Featured */}
        <div className="mb-6">
          {ranking.slice(0, 1).map((item) => (
            <div
              key={item.position}
              className={`bg-gradient-to-br ${getRankColor(item.position)} rounded-xl p-4 shadow-lg border border-white/20 mb-4`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="relative">
                    <div className="w-12 h-12 rounded-full bg-white/20 backdrop-blur-sm border-2 border-white/40 flex items-center justify-center text-white shadow-lg">
                      <span className="text-lg">#{item.position}</span>
                    </div>
                    <div className="absolute -top-1 -right-1 bg-white rounded-full p-1 shadow-md">
                      {getRankIcon(item.position)}
                    </div>
                  </div>
                  <div>
                    <div className="text-white">{item.nome}</div>
                    <div className="text-xs text-white/80">Líder do ranking</div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-3xl text-white tabular-nums">{item.tickets}</div>
                  <div className="text-xs text-white/80">tickets</div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Rest of ranking */}
        <div className="space-y-3">
          {ranking.slice(1).map((item) => (
            <div
              key={item.position}
              className="flex items-center justify-between p-3 bg-slate-700/30 rounded-lg hover:bg-slate-700/50 transition-colors border border-slate-600/30"
            >
              <div className="flex items-center gap-3">
                <div className={`w-10 h-10 rounded-lg bg-gradient-to-br ${getRankColor(item.position)} flex items-center justify-center text-white text-sm shadow-md relative`}>
                  {item.position}
                  {getRankIcon(item.position) && (
                    <div className="absolute -top-1 -right-1">
                      {getRankIcon(item.position)}
                    </div>
                  )}
                </div>
                <div className="text-slate-200">{item.nome}</div>
              </div>
              <div className="text-right">
                <div className="text-2xl text-blue-400 tabular-nums">{item.tickets}</div>
                <div className="text-xs text-slate-500">tickets</div>
              </div>
            </div>
          ))}
        </div>

        {/* Summary */}
        <div className="mt-6 pt-6 border-t border-slate-700/50">
          <div className="bg-slate-900/50 rounded-lg p-4 border border-slate-700/30">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-slate-400">Total Atribuído</span>
              <span className="text-2xl text-white tabular-nums">11</span>
            </div>
            <div className="flex items-center gap-2 text-xs text-slate-500">
              <TrendingUp className="w-3 h-3" />
              <span>Período: últimos 30 dias</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

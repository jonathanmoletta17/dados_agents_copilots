import { Trophy, Medal, Award } from "lucide-react";

const technicians = [
  { rank: 1, name: "Carlos Alberto Pereira", tickets: 70, avatar: "CA" },
  { rank: 2, name: "Silas Gomes Valim", tickets: 70, avatar: "SV" },
  { rank: 3, name: "Wellington Guimarães", tickets: 48, avatar: "WG" },
  { rank: 4, name: "Alessandro Carvalho Vieira", tickets: 42, avatar: "AV" },
  { rank: 5, name: "Miguelangelo Ferreira", tickets: 37, avatar: "MF" },
  { rank: 6, name: "Anderson da Silva Morim", tickets: 37, avatar: "AS" },
  { rank: 7, name: "Thales Vinícius Pira Leite", tickets: 35, avatar: "TL" },
  { rank: 8, name: "Edson José das Santos", tickets: 24, avatar: "ES" },
  { rank: 9, name: "Gabriel Andrade", tickets: 17, avatar: "GC" },
];

export function TechnicianRankingCompact() {
  return (
    <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl border border-slate-700/50 p-4 shadow-xl">
      <h2 className="text-white mb-3 flex items-center gap-2">
        <div className="w-1 h-6 bg-gradient-to-b from-yellow-500 to-orange-600 rounded-full" />
        Ranking de Técnicos
      </h2>

      <div className="grid grid-cols-12 gap-4">
        {/* Top 3 - Featured */}
        <div className="col-span-5 grid grid-cols-3 gap-3">
          {technicians.slice(0, 3).map((tech) => {
            const getRankColor = (rank: number) => {
              if (rank === 1) return "from-yellow-500 to-yellow-600";
              if (rank === 2) return "from-slate-400 to-slate-500";
              if (rank === 3) return "from-amber-600 to-amber-700";
              return "from-blue-500 to-blue-600";
            };

            const getRankIcon = (rank: number) => {
              if (rank === 1) return <Trophy className="w-5 h-5" />;
              if (rank === 2) return <Medal className="w-5 h-5" />;
              if (rank === 3) return <Medal className="w-5 h-5" />;
              return null;
            };

            return (
              <div
                key={tech.rank}
                className={`bg-gradient-to-br ${getRankColor(tech.rank)} rounded-lg p-3 shadow-lg border border-white/20 hover:scale-105 transition-transform relative overflow-hidden`}
              >
                <div className="absolute top-2 right-2 text-white/80">
                  {getRankIcon(tech.rank)}
                </div>
                
                <div className="flex flex-col items-center gap-2 relative z-10">
                  <div className="w-12 h-12 rounded-full bg-white/20 backdrop-blur-sm border border-white/40 flex items-center justify-center text-white shadow-lg">
                    <span className="text-sm">{tech.avatar}</span>
                  </div>
                  
                  <div className="text-center">
                    <div className="text-xs text-white/80 mb-0.5">#{tech.rank}</div>
                    <div className="text-xs text-white line-clamp-2 leading-tight">
                      {tech.name}
                    </div>
                    <div className="text-2xl text-white mt-1 tabular-nums">
                      {tech.tickets}
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Rest of ranking - Compact list */}
        <div className="col-span-7 bg-slate-900/50 rounded-lg border border-slate-700/30 p-3">
          <div className="grid grid-cols-3 gap-2">
            {technicians.slice(3).map((tech) => (
              <div
                key={tech.rank}
                className="flex items-center gap-2 bg-slate-800/50 rounded-lg p-2 border border-slate-700/30 hover:bg-slate-700/50 transition-colors"
              >
                <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center text-white text-xs shadow-md shrink-0">
                  {tech.rank}
                </div>
                
                <div className="flex-1 min-w-0">
                  <div className="text-xs text-slate-300 truncate">{tech.name}</div>
                  <div className="text-sm text-blue-400 tabular-nums">{tech.tickets} tickets</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

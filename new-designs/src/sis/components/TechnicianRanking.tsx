import { Trophy, Medal, Award } from "lucide-react";

const technicians = [
  { 
    rank: 1, 
    name: "Vera M.", 
    fullName: "Vera Lucia dos Santos Machado",
    tickets: 220, 
    avatar: "VM" 
  },
  { 
    rank: 2, 
    name: "Amanda N.", 
    fullName: "Amanda Pinheiro Nobre",
    tickets: 94, 
    avatar: "AN" 
  },
  { 
    rank: 3, 
    name: "Rodrigo P.", 
    fullName: "Rodrigo Ludmann Pias",
    tickets: 78, 
    avatar: "RP" 
  },
  { 
    rank: 4, 
    name: "Thiago O.", 
    fullName: "Thiago Lima de Oliveira",
    tickets: 69, 
    avatar: "TO" 
  },
  { 
    rank: 5, 
    name: "Anderson S.", 
    fullName: "Anderson Silva",
    tickets: 45, 
    avatar: "AS" 
  },
];

export function TechnicianRanking() {
  return (
    <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl border border-slate-700/50 p-4 shadow-xl">
      <h2 className="text-white mb-3 flex items-center gap-2">
        <div className="w-1 h-6 bg-gradient-to-b from-yellow-500 to-orange-600 rounded-full" />
        Ranking de Técnicos
      </h2>

      <div className="grid grid-cols-12 gap-4">
        {/* Top 3 - Featured */}
        <div className="col-span-7 grid grid-cols-3 gap-3">
          {technicians.slice(0, 3).map((tech) => {
            const getRankColor = (rank: number) => {
              if (rank === 1) return "from-blue-500 to-blue-600";
              if (rank === 2) return "from-slate-600 to-slate-700";
              if (rank === 3) return "from-orange-600 to-orange-700";
              return "from-blue-500 to-blue-600";
            };

            const getRankIcon = (rank: number) => {
              if (rank === 1) return <Trophy className="w-6 h-6" />;
              if (rank === 2) return <Medal className="w-6 h-6" />;
              if (rank === 3) return <Medal className="w-6 h-6" />;
              return null;
            };

            const getRankBadgeColor = (rank: number) => {
              if (rank === 1) return "bg-yellow-500";
              if (rank === 2) return "bg-slate-400";
              if (rank === 3) return "bg-orange-600";
              return "bg-blue-500";
            };

            return (
              <div
                key={tech.rank}
                className={`bg-gradient-to-br ${getRankColor(tech.rank)} rounded-xl p-4 shadow-lg border border-white/20 hover:scale-105 transition-transform relative overflow-hidden`}
              >
                <div className={`absolute -top-2 -right-2 ${getRankBadgeColor(tech.rank)} text-white rounded-full p-2 shadow-lg`}>
                  {getRankIcon(tech.rank)}
                </div>
                
                <div className="flex flex-col items-center gap-3 relative z-10">
                  <div className="w-16 h-16 rounded-full bg-white/20 backdrop-blur-sm border-2 border-white/40 flex items-center justify-center text-white shadow-lg">
                    <span className="text-lg">{tech.avatar}</span>
                  </div>
                  
                  <div className="text-center w-full">
                    <div className="text-xs text-white/80 mb-1">#{tech.rank}</div>
                    <div className="text-sm text-white mb-0.5">
                      {tech.name}
                    </div>
                    <div className="text-xs text-white/70 line-clamp-2 leading-tight px-2">
                      {tech.fullName}
                    </div>
                    <div className="text-3xl text-white mt-2 tabular-nums">
                      {tech.tickets}
                    </div>
                    <div className="text-xs text-white/80">tickets</div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Rest of ranking - Compact list */}
        <div className="col-span-5 bg-slate-900/50 rounded-lg border border-slate-700/30 p-3">
          <div className="space-y-2">
            {technicians.slice(3).map((tech) => (
              <div
                key={tech.rank}
                className="flex items-center gap-3 bg-slate-800/50 rounded-lg p-3 border border-slate-700/30 hover:bg-slate-700/50 transition-colors"
              >
                <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center text-white text-sm shadow-md shrink-0">
                  {tech.rank}
                </div>
                
                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-slate-600 to-slate-700 flex items-center justify-center text-white text-sm shadow-md shrink-0">
                  {tech.avatar}
                </div>
                
                <div className="flex-1 min-w-0">
                  <div className="text-sm text-slate-300">{tech.name}</div>
                  <div className="text-xs text-slate-500 truncate">{tech.fullName}</div>
                </div>

                <div className="text-right shrink-0">
                  <div className="text-xl text-blue-400 tabular-nums">{tech.tickets}</div>
                  <div className="text-xs text-slate-500">tickets</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

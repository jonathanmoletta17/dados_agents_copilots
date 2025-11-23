import { Award, Medal, Trophy, TrendingUp } from "lucide-react";

const technicians = [
  { rank: 1, name: "Carlos Alberto Pereira", tickets: 70, avatar: "CA" },
  { rank: 2, name: "Silas Gomes Valim", tickets: 70, avatar: "SV" },
  { rank: 3, name: "Wellington Guimarães", tickets: 48, avatar: "WG" },
  { rank: 4, name: "Alessandro Carvalho Vieira", tickets: 42, avatar: "AV" },
  { rank: 5, name: "Miguelangelo Ferreira", tickets: 37, avatar: "MF" },
  { rank: 6, name: "Anderson da Silva Morim de Oliveira", tickets: 37, avatar: "AS" },
  { rank: 7, name: "Thales Vinícius Pira Leite", tickets: 35, avatar: "TL" },
  { rank: 8, name: "Edson José das Santos Silva", tickets: 24, avatar: "ES" },
  { rank: 9, name: "Gabriel Andrade de Camargos", tickets: 17, avatar: "GC" },
];

export function TechnicianRanking() {
  const getRankIcon = (rank: number) => {
    if (rank === 1) return <Trophy className="w-5 h-5 text-yellow-500" />;
    if (rank === 2) return <Medal className="w-5 h-5 text-slate-400" />;
    if (rank === 3) return <Medal className="w-5 h-5 text-amber-700" />;
    return null;
  };

  const getRankStyle = (rank: number) => {
    if (rank === 1) return "from-yellow-500 to-yellow-600";
    if (rank === 2) return "from-slate-400 to-slate-500";
    if (rank === 3) return "from-amber-600 to-amber-700";
    return "from-blue-500 to-blue-600";
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl text-slate-700 flex items-center gap-2">
          <Award className="w-5 h-5 text-blue-600" />
          Ranking de Técnicos
        </h2>
        <div className="text-sm text-slate-500 flex items-center gap-1">
          <TrendingUp className="w-4 h-4" />
          Por volume de tickets
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
        {/* Top 3 - Featured */}
        <div className="grid grid-cols-3 gap-4 p-6 bg-gradient-to-br from-slate-50 to-white border-b border-slate-200">
          {technicians.slice(0, 3).map((tech) => (
            <div
              key={tech.rank}
              className="flex flex-col items-center gap-3 p-4 bg-white rounded-lg shadow-sm border border-slate-200 hover:shadow-md transition-shadow"
            >
              <div className="relative">
                <div className={`w-16 h-16 rounded-full bg-gradient-to-br ${getRankStyle(tech.rank)} flex items-center justify-center text-white shadow-lg`}>
                  <span className="text-xl">{tech.avatar}</span>
                </div>
                <div className="absolute -top-1 -right-1 bg-white rounded-full p-1 shadow-md">
                  {getRankIcon(tech.rank)}
                </div>
              </div>
              
              <div className="text-center">
                <div className="text-xs text-slate-500 mb-1">#{tech.rank}</div>
                <div className="text-sm text-slate-700 line-clamp-2">
                  {tech.name}
                </div>
                <div className="text-xl text-blue-600 mt-2">
                  {tech.tickets}
                </div>
                <div className="text-xs text-slate-500">tickets</div>
              </div>
            </div>
          ))}
        </div>

        {/* Rest of ranking */}
        <div className="divide-y divide-slate-100">
          {technicians.slice(3).map((tech) => (
            <div
              key={tech.rank}
              className="flex items-center gap-4 p-4 hover:bg-slate-50 transition-colors"
            >
              <div className={`w-8 h-8 rounded-lg bg-gradient-to-br ${getRankStyle(tech.rank)} flex items-center justify-center text-white text-sm shadow-sm`}>
                {tech.rank}
              </div>
              
              <div className={`w-12 h-12 rounded-full bg-gradient-to-br ${getRankStyle(tech.rank)} flex items-center justify-center text-white shadow-sm`}>
                <span>{tech.avatar}</span>
              </div>

              <div className="flex-1">
                <div className="text-sm text-slate-700">{tech.name}</div>
                <div className="text-xs text-slate-500 mt-0.5">Técnico</div>
              </div>

              <div className="text-right">
                <div className="text-2xl text-blue-600">{tech.tickets}</div>
                <div className="text-xs text-slate-500">tickets</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

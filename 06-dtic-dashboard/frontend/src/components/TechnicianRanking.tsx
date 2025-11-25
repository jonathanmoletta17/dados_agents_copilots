import { useState } from "react";
import { Award, Medal, Trophy, TrendingUp, ChevronLeft, ChevronRight } from "lucide-react";
import { TechnicianRankingItem } from "../types/api";

interface TechnicianRankingProps {
  ranking?: TechnicianRankingItem[];
}

export function TechnicianRanking({ ranking }: TechnicianRankingProps) {
  const [currentPage, setCurrentPage] = useState(0);
  const itemsPerPage = 6; // 3 columns * 2 rows

  const technicians = ranking?.map((tech, index) => ({
    rank: index + 1,
    name: tech.tecnico,
    tickets: tech.tickets,
    avatar: tech.tecnico.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase(),
  })) || [];

  const top3 = technicians.slice(0, 3);
  const restTechnicians = technicians.slice(3);
  const totalPages = Math.ceil(restTechnicians.length / itemsPerPage);

  const currentRestPage = restTechnicians.slice(
    currentPage * itemsPerPage,
    (currentPage + 1) * itemsPerPage
  );

  const nextPage = () => {
    setCurrentPage((prev) => (prev + 1) % totalPages);
  };

  const prevPage = () => {
    setCurrentPage((prev) => (prev - 1 + totalPages) % totalPages);
  };

  const getRankIcon = (rank: number) => {
    if (rank === 1) return <Trophy className="w-4 h-4 text-yellow-500" />;
    if (rank === 2) return <Medal className="w-4 h-4 text-slate-400" />;
    if (rank === 3) return <Medal className="w-4 h-4 text-amber-700" />;
    return null;
  };

  const getRankStyle = (rank: number) => {
    if (rank === 1) return "from-yellow-500 to-yellow-600";
    if (rank === 2) return "from-slate-400 to-slate-500";
    if (rank === 3) return "from-amber-600 to-amber-700";
    return "from-blue-500 to-blue-600";
  };

  if (!ranking) {
    return (
      <div className="space-y-4 animate-pulse">
        <div className="h-8 w-48 bg-slate-800/50 rounded" />
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 h-48" />
      </div>
    );
  }

  return (
    <div className="space-y-2 h-auto flex flex-col">
      <div className="flex items-center justify-between shrink-0">
        <h2 className="text-lg text-white flex items-center gap-2 font-semibold">
          <Award className="w-5 h-5 text-blue-400" />
          Ranking de Técnicos
        </h2>
        <div className="text-xs text-slate-400 flex items-center gap-1">
          <TrendingUp className="w-3 h-3" />
          Por volume de tickets
        </div>
      </div>

      <div className="grid grid-cols-12 gap-4 flex-1 min-h-0">
        {/* Top 3 - Featured */}
        <div className="col-span-5 grid grid-cols-2 md:grid-cols-3 auto-rows-[minmax(90px,auto)] gap-1.5 h-full content-start">
          {top3.map((tech) => (
            <div
              key={tech.rank}
              className="flex flex-col items-center justify-center gap-1.5 p-2 bg-white rounded-xl shadow-sm border border-slate-200 hover:shadow-md transition-all relative overflow-hidden group h-auto min-h-[90px]"
            >
              <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-slate-200 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />

              <div className="relative mt-0">
                <div className={`w-8 h-8 rounded-full bg-gradient-to-br ${getRankStyle(tech.rank)} flex items-center justify-center text-white shadow-md group-hover:scale-110 transition-transform duration-300`}>
                  <span className="text-sm font-bold">{tech.avatar}</span>
                </div>
                <div className="absolute -top-1 -right-1 bg-white rounded-full p-0.5 shadow-sm border border-slate-100">
                  {getRankIcon(tech.rank)}
                </div>
              </div>

              <div className="text-center w-full flex-1 flex flex-col justify-center">
                <div className="text-[9px] text-slate-400 font-medium mb-0.5">#{tech.rank}</div>
                <div className="text-xs font-medium text-slate-700 line-clamp-2 px-1 leading-tight" title={tech.name}>
                  {tech.name}
                </div>
                <div className="text-base font-bold text-blue-600 mt-0.5 leading-none">
                  {tech.tickets}
                </div>
                <div className="text-[8px] text-slate-400 uppercase tracking-wider mt-0.5">tickets</div>
              </div>
            </div>
          ))}
        </div>

        {/* Rest of ranking - Carousel Grid */}
        <div className="col-span-7 flex flex-col h-full">
          <div className="flex-1 min-h-0 grid grid-cols-2 md:grid-cols-3 auto-rows-[minmax(90px,auto)] gap-1.5">
            {currentRestPage.map((tech) => (
              <div
                key={tech.rank}
                className="flex items-center gap-1.5 p-2 bg-white rounded-xl border border-slate-200 hover:border-blue-200 hover:shadow-sm transition-all group h-auto min-h-[90px]"
              >
                <div className={`w-7 h-7 rounded-lg bg-gradient-to-br ${getRankStyle(tech.rank)} flex items-center justify-center text-white font-bold text-xs shadow-sm group-hover:scale-105 transition-transform shrink-0`}>
                  {tech.rank}
                </div>

                <div className="flex-1 min-w-0 flex flex-col justify-center">
                  <div className="text-xs font-medium text-slate-700 truncate leading-tight" title={tech.name}>{tech.name}</div>
                  <div className="flex items-baseline gap-1">
                    <span className="text-sm font-bold text-blue-600 leading-none">{tech.tickets}</span>
                    <span className="text-[8px] text-slate-400 uppercase">tickets</span>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {totalPages > 1 && (
            <div className="flex justify-center gap-2 mt-0 shrink-0">
              <button
                onClick={prevPage}
                className="p-1 rounded-full bg-slate-800 text-slate-400 hover:bg-slate-700 hover:text-white transition-colors"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              <div className="flex gap-1.5 items-center">
                {Array.from({ length: totalPages }).map((_, i) => (
                  <div
                    key={i}
                    className={`w-2 h-2 rounded-full transition-colors ${i === currentPage ? "bg-blue-500" : "bg-slate-700"
                      }`}
                  />
                ))}
              </div>
              <button
                onClick={nextPage}
                className="p-1 rounded-full bg-slate-800 text-slate-400 hover:bg-slate-700 hover:text-white transition-colors"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          )}
        </div>
      </div>
    </div >
  );
}

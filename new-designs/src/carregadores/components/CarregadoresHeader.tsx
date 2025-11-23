import { PackageOpen, Calendar, RefreshCw, LayoutDashboard, ArrowRightLeft } from "lucide-react";
import { useState, useEffect } from "react";

interface CarregadoresHeaderProps {
  onNavigate: (view: string) => void;
}

export function CarregadoresHeader({ onNavigate }: CarregadoresHeaderProps) {
  const [startDate, setStartDate] = useState("22/10/2025");
  const [endDate, setEndDate] = useState("21/11/2025");
  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  return (
    <header className="bg-gradient-to-r from-slate-800 via-slate-900 to-slate-800 text-white shadow-2xl border-b border-slate-700/50">
      <div className="max-w-[1600px] mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          {/* Title Section */}
          <div className="flex items-center gap-4">
            <div className="bg-white/10 backdrop-blur-sm p-2 rounded-lg border border-white/20">
              <PackageOpen className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-2xl tracking-tight">CARREGADORES</h1>
              <p className="text-slate-300 text-sm mt-0.5">Em tempo real</p>
            </div>
          </div>

          {/* Center - Date Filters */}
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 text-sm text-slate-300">
              <Calendar className="w-4 h-4" />
              <span>Início:</span>
            </div>
            <input
              type="text"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              className="bg-slate-700/50 border border-slate-600/50 rounded-lg px-3 py-2 text-sm w-32 focus:outline-none focus:ring-2 focus:ring-blue-500/50 text-white"
              placeholder="DD/MM/AAAA"
            />
            
            <div className="flex items-center gap-2 text-sm text-slate-300">
              <span>Fim:</span>
            </div>
            <input
              type="text"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              className="bg-slate-700/50 border border-slate-600/50 rounded-lg px-3 py-2 text-sm w-32 focus:outline-none focus:ring-2 focus:ring-blue-500/50 text-white"
              placeholder="DD/MM/AAAA"
            />

            <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm transition-all shadow-lg hover:shadow-xl">
              Aplicar
            </button>
          </div>

          {/* Right - Time and Navigation */}
          <div className="flex items-center gap-4">
            <div className="bg-slate-700/50 backdrop-blur-sm rounded-lg px-4 py-2 border border-slate-600/30">
              <div className="text-2xl tabular-nums tracking-tight">
                {currentTime.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
              </div>
            </div>

            <button 
              onClick={() => onNavigate("dtic-dashboard")}
              className="bg-white/10 hover:bg-white/20 transition-all rounded-lg px-4 py-2.5 backdrop-blur-sm border border-white/20 hover:scale-105 flex items-center gap-2"
            >
              <LayoutDashboard className="w-5 h-5" />
              <span className="text-sm">Dashboards</span>
            </button>
            
            <button className="bg-white/10 hover:bg-white/20 transition-all rounded-lg p-2.5 backdrop-blur-sm border border-white/20 hover:scale-105">
              <RefreshCw className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}

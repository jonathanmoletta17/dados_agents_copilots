import { Wrench, Calendar, RefreshCw, ArrowRightLeft, Search } from "lucide-react";
import { useState, useEffect } from "react";

interface DashboardHeaderProps {
  onSwitchToDashboard: () => void;
  onSwitchToSearch: () => void;
}

export function DashboardHeader({ onSwitchToDashboard, onSwitchToSearch }: DashboardHeaderProps) {
  const [startDate] = useState("07/09/2025");
  const [endDate] = useState("07/10/2025");
  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  return (
    <header className="bg-gradient-to-r from-blue-600 via-blue-700 to-blue-800 text-white shadow-2xl border-b border-blue-500/30">
      <div className="px-6 py-3 flex items-center justify-between">
        {/* Title Section */}
        <div className="flex items-center gap-4">
          <div className="bg-white/10 backdrop-blur-sm p-2 rounded-lg border border-white/20">
            <Wrench className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl tracking-tight">Divisão de Manutenção</h1>
            <p className="text-blue-100 text-xs mt-0.5">Dashboard de Métricas - SIS</p>
          </div>
        </div>

        {/* Center - Date Range */}
        <div className="flex items-center gap-2 bg-white/10 backdrop-blur-sm rounded-lg px-4 py-2 border border-white/20">
          <Calendar className="w-4 h-4 text-blue-100" />
          <span className="text-sm">Período:</span>
          <span className="text-sm">{startDate}</span>
          <span className="text-blue-300">→</span>
          <span className="text-sm">{endDate}</span>
        </div>

        {/* Right - Time, Buttons */}
        <div className="flex items-center gap-4">
          <div className="text-right">
            <div className="text-2xl tabular-nums tracking-tight">
              {currentTime.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
            </div>
            <div className="text-xs text-blue-100">
              {currentTime.toLocaleDateString('pt-BR', { weekday: 'long', day: '2-digit', month: 'long' })}
            </div>
          </div>
          
          <button 
            onClick={onSwitchToSearch}
            className="bg-white/10 hover:bg-white/20 transition-all rounded-lg px-4 py-2.5 backdrop-blur-sm border border-white/20 hover:scale-105 flex items-center gap-2"
          >
            <Search className="w-5 h-5" />
            <span className="text-sm">Buscar</span>
          </button>
          
          <button 
            onClick={onSwitchToDashboard}
            className="bg-white/10 hover:bg-white/20 transition-all rounded-lg px-4 py-2.5 backdrop-blur-sm border border-white/20 hover:scale-105 flex items-center gap-2"
          >
            <ArrowRightLeft className="w-5 h-5" />
            <span className="text-sm">DTIC</span>
          </button>
          
          <button className="bg-white/10 hover:bg-white/20 transition-all rounded-lg p-2.5 backdrop-blur-sm border border-white/20 hover:scale-105">
            <RefreshCw className="w-5 h-5" />
          </button>
        </div>
      </div>
    </header>
  );
}

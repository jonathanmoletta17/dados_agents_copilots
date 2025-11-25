import { Calendar, RefreshCw, Activity } from "lucide-react";
import { useState, useEffect } from "react";

interface DashboardHeaderProps {
  startDate: string;
  endDate: string;
  onDateChange: (start: string, end: string) => void;
  onRefresh?: () => void;
}

export function DashboardHeader({ startDate, endDate, onDateChange, onRefresh }: DashboardHeaderProps) {
  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  const handleDateChange = (e: React.ChangeEvent<HTMLInputElement>, type: 'start' | 'end') => {
    if (type === 'start') {
      onDateChange(e.target.value, endDate);
    } else {
      onDateChange(startDate, e.target.value);
    }
  };

  return (
    <header className="bg-gradient-to-r from-blue-600 via-blue-700 to-blue-800 text-white shadow-2xl border-b border-blue-500/30">
      <div className="px-6 py-3 flex items-center justify-between">
        {/* Title Section */}
        <div className="flex items-center gap-4">
          <div className="bg-white/10 backdrop-blur-sm p-2 rounded-lg border border-white/20">
            <Activity className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl tracking-tight">DTIC - Dashboard de Métricas</h1>
            <p className="text-blue-100 text-xs mt-0.5">Departamento de Tecnologia da Informação - Monitoramento em Tempo Real</p>
          </div>
        </div>

        {/* Center - Date Range */}
        <div className="flex items-center gap-2 bg-white/10 backdrop-blur-sm rounded-lg px-4 py-2 border border-white/20">
          <Calendar className="w-4 h-4 text-blue-100" />
          <span className="text-sm">Período:</span>
          <input
            type="date"
            value={startDate}
            onChange={(e) => handleDateChange(e, 'start')}
            className="bg-transparent border-none text-white text-sm focus:ring-0 p-0 w-[130px] [&::-webkit-calendar-picker-indicator]:invert"
          />
          <span className="text-blue-300">→</span>
          <input
            type="date"
            value={endDate}
            onChange={(e) => handleDateChange(e, 'end')}
            className="bg-transparent border-none text-white text-sm focus:ring-0 p-0 w-[130px] [&::-webkit-calendar-picker-indicator]:invert"
          />
        </div>

        {/* Right - Time and Refresh */}
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
            onClick={onRefresh || (() => window.location.reload())}
            className="bg-white/10 hover:bg-white/20 transition-all rounded-lg p-2.5 backdrop-blur-sm border border-white/20 hover:scale-105"
            title="Recarregar página"
          >
            <RefreshCw className="w-5 h-5" />
          </button>
        </div>
      </div>
    </header>
  );
}

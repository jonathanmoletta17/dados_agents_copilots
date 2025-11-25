import { useState } from 'react';
import { DashboardHeader } from "./components/DashboardHeader";
import { MetricsCards } from "./components/MetricsCards";
import { LevelCharts } from "./components/LevelCharts";
import { TechnicianRanking } from "./components/TechnicianRanking";
import { RecentTicketsCompact } from "./components/RecentTicketsCompact";
import { QuickStats } from "./components/QuickStats";
import { useGLPIData } from "./hooks/useGLPIData";

export default function App() {
  // Estado para o filtro de data
  const [dateRange, setDateRange] = useState(() => {
    const today = new Date();
    const thirtyDaysAgo = new Date();
    thirtyDaysAgo.setDate(today.getDate() - 30);
    return {
      inicio: thirtyDaysAgo.toISOString().split('T')[0], // YYYY-MM-DD
      fim: today.toISOString().split('T')[0],
    };
  });

  // Hook de dados
  const { generalStats, levelStats, technicianRanking, newTickets, isLoading, refresh } = useGLPIData(dateRange);

  const handleDateChange = (inicio: string, fim: string) => {
    setDateRange({ inicio, fim });
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans selection:bg-blue-500/30">
      <div className="flex flex-col h-screen overflow-hidden">
        <DashboardHeader
          startDate={dateRange.inicio}
          endDate={dateRange.fim}
          onDateChange={handleDateChange}
          onRefresh={refresh}
        />

        <main className="flex-1 overflow-hidden p-6">
          <div className="grid grid-cols-12 gap-4 h-full">
            {/* Left Column - Main Metrics */}
            <div className="col-span-9 flex flex-col min-h-0 flex-1 gap-4">
              {/* Top Cards */}
              <div className="flex-none">
                <MetricsCards stats={generalStats} isLoading={isLoading} />
              </div>

              {/* Charts Section */}
              {/* Charts Section */}
              <div className="flex-1 min-h-0">
                <LevelCharts levelStats={levelStats} />
              </div>

              {/* Bottom Section - Ranking */}
              <div className="mt-auto shrink-0">
                <TechnicianRanking ranking={technicianRanking} />
              </div>
            </div>

            {/* Right Column - Sidebar */}
            <div className="col-span-3 h-full overflow-hidden">
              <RecentTicketsCompact tickets={newTickets} />
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}

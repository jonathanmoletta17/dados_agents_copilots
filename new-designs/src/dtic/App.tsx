import { DashboardHeader } from "./components/DashboardHeader";
import { MetricsCardsCompact } from "./components/MetricsCardsCompact";
import { LevelCharts } from "./components/LevelCharts";
import { TechnicianRankingCompact } from "./components/TechnicianRankingCompact";
import { RecentTicketsCompact } from "./components/RecentTicketsCompact";
import { QuickStats } from "./components/QuickStats";

interface DashboardDTICProps {
  onSwitchToDashboard: () => void;
  onSwitchToSearch: () => void;
}

export default function DashboardDTIC({ onSwitchToDashboard, onSwitchToSearch }: DashboardDTICProps) {
  return (
    <div className="h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 overflow-hidden flex flex-col">
      <DashboardHeader 
        onSwitchToDashboard={onSwitchToDashboard}
        onSwitchToSearch={onSwitchToSearch}
      />
      
      <div className="flex-1 flex gap-4 p-4 overflow-hidden">
        {/* Main Content */}
        <div className="flex-1 flex flex-col gap-4 overflow-hidden">
          {/* Top Row - Metrics */}
          <MetricsCardsCompact />
          
          {/* Middle Row - Levels and Quick Stats */}
          <div className="flex gap-4 flex-1">
            <div className="flex-1">
              <LevelCharts />
            </div>
            <div className="w-80">
              <QuickStats />
            </div>
          </div>
          
          {/* Bottom Row - Technician Ranking */}
          <TechnicianRankingCompact />
        </div>
        
        {/* Sidebar - Recent Tickets */}
        <div className="w-80">
          <RecentTicketsCompact />
        </div>
      </div>
    </div>
  );
}

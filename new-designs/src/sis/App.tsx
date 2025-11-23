import { DashboardHeader } from "./components/DashboardHeader";
import { MetricsCardsCompact } from "./components/MetricsCardsCompact";
import { EntityDistribution } from "./components/EntityDistribution";
import { CategoryDistribution } from "./components/CategoryDistribution";
import { TechnicianRanking } from "./components/TechnicianRanking";
import { RecentTickets } from "./components/RecentTickets";
import { QuickStats } from "./components/QuickStats";

interface DashboardSISProps {
  onSwitchToDashboard: () => void;
  onSwitchToSearch: () => void;
}

export default function DashboardSIS({ onSwitchToDashboard, onSwitchToSearch }: DashboardSISProps) {
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
          
          {/* Middle Row - Distribution Charts */}
          <div className="flex gap-4 flex-1 overflow-hidden">
            <div className="flex-1">
              <EntityDistribution />
            </div>
            <div className="flex-1">
              <CategoryDistribution />
            </div>
          </div>
          
          {/* Bottom Row - Technician Ranking */}
          <TechnicianRanking />
        </div>
        
        {/* Sidebar */}
        <div className="w-80 flex flex-col gap-4">
          <RecentTickets />
          <QuickStats />
        </div>
      </div>
    </div>
  );
}

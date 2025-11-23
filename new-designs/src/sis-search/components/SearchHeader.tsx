import { LayoutDashboard, Search, ArrowRightLeft } from "lucide-react";

interface SearchHeaderProps {
  onSwitchToDashboard: () => void;
  onSwitchToSearch: () => void;
}

export function SearchHeader({ onSwitchToDashboard, onSwitchToSearch }: SearchHeaderProps) {
  return (
    <header className="bg-gradient-to-r from-blue-600 via-blue-700 to-blue-800 text-white shadow-2xl border-b border-blue-500/30">
      <div className="max-w-[1600px] mx-auto px-6 py-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl tracking-tight mb-1">GLPI SIS Smart Search</h1>
            <p className="text-blue-100">Busca de Tickets - Manutenção e Conservação</p>
          </div>
          
          <div className="flex items-center gap-3">
            <button 
              onClick={onSwitchToDashboard}
              className="bg-white/10 hover:bg-white/20 transition-all rounded-lg px-4 py-2.5 backdrop-blur-sm border border-white/20 hover:scale-105 flex items-center gap-2"
            >
              <LayoutDashboard className="w-5 h-5" />
              <span className="text-sm">Dashboard</span>
            </button>
            
            <button 
              onClick={onSwitchToSearch}
              className="bg-white/10 hover:bg-white/20 transition-all rounded-lg px-4 py-2.5 backdrop-blur-sm border border-white/20 hover:scale-105 flex items-center gap-2"
            >
              <ArrowRightLeft className="w-5 h-5" />
              <span className="text-sm">DTIC</span>
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}

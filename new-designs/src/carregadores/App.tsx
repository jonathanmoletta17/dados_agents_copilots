import { CarregadoresHeader } from "./components/CarregadoresHeader";
import { CarregadoresList } from "./components/CarregadoresList";
import { CarregadoresRanking } from "./components/CarregadoresRanking";
import { StatusOverview } from "./components/StatusOverview";

interface CarregadoresProps {
  onNavigate: (view: string) => void;
}

export default function Carregadores({ onNavigate }: CarregadoresProps) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      <CarregadoresHeader onNavigate={onNavigate} />
      
      <div className="max-w-[1600px] mx-auto p-6 space-y-6">
        <StatusOverview />
        
        <div className="grid grid-cols-3 gap-6">
          <div className="col-span-2">
            <CarregadoresList />
          </div>
          <div>
            <CarregadoresRanking />
          </div>
        </div>
      </div>
    </div>
  );
}

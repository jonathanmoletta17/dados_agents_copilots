import { SearchHeader } from "./components/SearchHeader";
import { SearchBar } from "./components/SearchBar";
import { MetricsCards } from "./components/MetricsCards";
import { ResultsList } from "./components/ResultsList";

interface SearchSISProps {
  onSwitchToDashboard: () => void;
  onSwitchToSearch: () => void;
}

export default function SearchSIS({ onSwitchToDashboard, onSwitchToSearch }: SearchSISProps) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      <SearchHeader 
        onSwitchToDashboard={onSwitchToDashboard}
        onSwitchToSearch={onSwitchToSearch}
      />
      
      <div className="max-w-[1600px] mx-auto p-6 space-y-6">
        <SearchBar />
        <MetricsCards />
        <ResultsList />
      </div>
    </div>
  );
}

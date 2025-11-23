import { Search, LayoutDashboard } from "lucide-react";

interface SearchHeaderProps {
    onNavigate?: (view: string) => void;
}

export default function SearchHeader({ onNavigate }: SearchHeaderProps) {
    return (
        <header className="bg-gradient-to-r from-slate-800 via-slate-900 to-slate-800 text-white shadow-2xl border-b border-slate-700/50">
            <div className="max-w-[1600px] mx-auto px-6 py-4">
                <div className="flex items-center justify-between">
                    {/* Title Section */}
                    <div className="flex items-center gap-4">
                        <div className="bg-white/10 backdrop-blur-sm p-2 rounded-lg border border-white/20">
                            <Search className="w-6 h-6" />
                        </div>
                        <div>
                            <h1 className="text-2xl tracking-tight">GLPI SIS SMART SEARCH</h1>
                            <p className="text-slate-300 text-sm mt-0.5">Busca de Tickets - Manutenção e Conservação</p>
                        </div>
                    </div>

                    {/* Navigation Buttons */}
                    <div className="flex items-center gap-3">
                        <button
                            onClick={() => onNavigate?.("sis-dashboard")}
                            className="bg-white/10 hover:bg-white/20 transition-all rounded-lg px-4 py-2.5 backdrop-blur-sm border border-white/20 hover:scale-105 flex items-center gap-2"
                        >
                            <LayoutDashboard className="w-5 h-5" />
                            <span className="text-sm">Dashboard SIS</span>
                        </button>

                        <button
                            onClick={() => onNavigate?.("dtic-search")}
                            className="bg-white/10 hover:bg-white/20 transition-all rounded-lg px-4 py-2.5 backdrop-blur-sm border border-white/20 hover:scale-105 flex items-center gap-2"
                        >
                            <Search className="w-5 h-5" />
                            <span className="text-sm">Busca DTIC</span>
                        </button>
                    </div>
                </div>
            </div>
        </header>
    );
}

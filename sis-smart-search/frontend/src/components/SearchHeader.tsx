import { Search } from "lucide-react";

interface SearchHeaderProps {
    onNavigate?: (view: string) => void;
}

export default function SearchHeader({ onNavigate }: SearchHeaderProps) {
    return (
        <header className="bg-gradient-to-r from-blue-600 via-blue-700 to-blue-800 text-white shadow-2xl border-b border-blue-500/30">
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

                    
                </div>
            </div>
        </header>
    );
}

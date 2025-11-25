interface SearchHeaderProps {
    onSwitchToDashboard?: () => void;
    onSwitchToSearch?: () => void;
}

export function SearchHeader({}: SearchHeaderProps) {
    return (
        <header className="bg-gradient-to-r from-blue-600 via-blue-700 to-blue-800 text-white shadow-2xl border-b border-blue-500/30">
            <div className="max-w-[1600px] mx-auto px-6 py-6">
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-3xl tracking-tight mb-1">GLPI Smart Search</h1>
                        <p className="text-blue-100">Sistema Inteligente de Busca de Tickets - DTIC</p>
                    </div>
                </div>
            </div>
        </header>
    );
}

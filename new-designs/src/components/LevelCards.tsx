import { BarChart3 } from "lucide-react";

const levels = [
  {
    level: "N1",
    total: 60,
    data: [
      { status: "Novos", value: 1, color: "bg-blue-500" },
      { status: "Em Progr.", value: 2, color: "bg-orange-500" },
      { status: "Pendentes", value: 1, color: "bg-yellow-500" },
      { status: "Resolvidos", value: 56, color: "bg-green-500" },
    ],
  },
  {
    level: "N2",
    total: 140,
    data: [
      { status: "Novos", value: 1, color: "bg-blue-500" },
      { status: "Em Progr.", value: 11, color: "bg-orange-500" },
      { status: "Pendentes", value: 2, color: "bg-yellow-500" },
      { status: "Resolvidos", value: 126, color: "bg-green-500" },
    ],
  },
  {
    level: "N3",
    total: 239,
    data: [
      { status: "Novos", value: 1, color: "bg-blue-500" },
      { status: "Em Progr.", value: 9, color: "bg-orange-500" },
      { status: "Pendentes", value: 0, color: "bg-yellow-500" },
      { status: "Resolvidos", value: 229, color: "bg-green-500" },
    ],
  },
  {
    level: "N4",
    total: 0,
    data: [
      { status: "Novos", value: 0, color: "bg-blue-500" },
      { status: "Em Progr.", value: 0, color: "bg-orange-500" },
      { status: "Pendentes", value: 0, color: "bg-yellow-500" },
      { status: "Resolvidos", value: 0, color: "bg-green-500" },
    ],
  },
];

export function LevelCards() {
  return (
    <div className="space-y-4">
      <h2 className="text-xl text-slate-700 flex items-center gap-2">
        <BarChart3 className="w-5 h-5 text-blue-600" />
        Distribuição por Níveis de Suporte
      </h2>
      
      <div className="grid grid-cols-2 gap-6">
        {levels.map((level) => (
          <div
            key={level.level}
            className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 hover:shadow-md transition-shadow duration-200"
          >
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="bg-gradient-to-br from-blue-500 to-blue-600 text-white px-4 py-2 rounded-lg shadow-sm">
                  <span className="text-lg">Nível {level.level}</span>
                </div>
                <div className="text-3xl text-slate-700">
                  {level.total}
                </div>
              </div>
              <div className="text-sm text-slate-500">tickets</div>
            </div>

            {/* Status breakdown */}
            <div className="space-y-3">
              {level.data.map((item, index) => (
                <div key={index} className="flex items-center justify-between group">
                  <div className="flex items-center gap-2 flex-1">
                    <div className={`w-2 h-2 rounded-full ${item.color}`} />
                    <span className="text-sm text-slate-600">{item.status}</span>
                  </div>
                  <div className="flex items-center gap-3 flex-1">
                    <div className="flex-1 h-2 bg-slate-100 rounded-full overflow-hidden">
                      <div
                        className={`h-full ${item.color} transition-all duration-500`}
                        style={{
                          width: level.total > 0 ? `${(item.value / level.total) * 100}%` : "0%",
                        }}
                      />
                    </div>
                    <span className="text-sm text-slate-700 w-8 text-right">{item.value}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

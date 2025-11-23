import { Building2, TrendingDown } from "lucide-react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from "recharts";

const entities = [
  { 
    name: "GG > Depto de Conservação e Memória", 
    short: "Depto Conservação",
    tickets: 160, 
    color: "#3b82f6" 
  },
  { 
    name: "O > PIRATINI", 
    short: "PIRATINI",
    tickets: 116, 
    color: "#8b5cf6" 
  },
  { 
    name: "Outras Entidades", 
    short: "Outros",
    tickets: 85, 
    color: "#06b6d4" 
  },
];

export function EntityDistribution() {
  const total = entities.reduce((sum, e) => sum + e.tickets, 0);

  return (
    <div className="h-full bg-slate-800/50 backdrop-blur-sm rounded-xl border border-slate-700/50 p-4 shadow-xl flex flex-col">
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-white flex items-center gap-2">
          <Building2 className="w-5 h-5 text-blue-400" />
          Top 50 - Atribuição por Entidades
        </h2>
        <div className="text-xs text-slate-400 bg-slate-900/50 px-3 py-1 rounded-full border border-slate-700/30">
          {total} tickets
        </div>
      </div>
      
      <div className="flex-1 grid grid-cols-2 gap-4">
        {/* Chart */}
        <div className="bg-slate-900/50 rounded-lg p-3 border border-slate-700/30">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={entities} layout="vertical" margin={{ top: 5, right: 10, left: 5, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.3} />
              <XAxis type="number" stroke="#94a3b8" fontSize={11} />
              <YAxis dataKey="short" type="category" stroke="#94a3b8" fontSize={11} width={100} />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#1e293b",
                  border: "1px solid #334155",
                  borderRadius: "8px",
                  fontSize: "12px",
                }}
                labelStyle={{ color: "#e2e8f0" }}
              />
              <Bar dataKey="tickets" radius={[0, 4, 4, 0]}>
                {entities.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* List */}
        <div className="bg-slate-900/50 rounded-lg p-3 border border-slate-700/30 space-y-2 overflow-y-auto">
          {entities.map((entity, index) => {
            const percentage = ((entity.tickets / total) * 100).toFixed(1);
            return (
              <div key={index} className="group">
                <div className="flex items-start justify-between mb-1.5">
                  <div className="flex items-center gap-2">
                    <div 
                      className="w-6 h-6 rounded-lg flex items-center justify-center text-white text-xs shadow-md shrink-0"
                      style={{ backgroundColor: entity.color }}
                    >
                      {index + 1}
                    </div>
                    <div className="flex-1">
                      <div className="text-xs text-slate-300 leading-tight line-clamp-2">
                        {entity.name}
                      </div>
                    </div>
                  </div>
                  <div className="text-right ml-2 shrink-0">
                    <div className="text-lg text-white tabular-nums">{entity.tickets}</div>
                    <div className="text-xs text-slate-500">{percentage}%</div>
                  </div>
                </div>
                <div className="h-1.5 bg-slate-800 rounded-full overflow-hidden">
                  <div
                    className="h-full rounded-full transition-all duration-500"
                    style={{ 
                      width: `${percentage}%`,
                      backgroundColor: entity.color 
                    }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

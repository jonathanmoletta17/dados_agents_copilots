import { Tags } from "lucide-react";
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from "recharts";

const categories = [
  { name: "Manutenção > Marcenaria", short: "Marcenaria", tickets: 34, color: "#3b82f6" },
  { name: "Manutenção > Marcenaria > Outras", short: "Marc. Outras", tickets: 32, color: "#8b5cf6" },
  { name: "Manutenção > Elétrica", short: "Elétrica", tickets: 25, color: "#06b6d4" },
  { name: "Pedreiro", short: "Pedreiro", tickets: 24, color: "#10b981" },
  { name: "Pedreiro > Reparo", short: "Ped. Reparo", tickets: 13, color: "#f59e0b" },
  { name: "Outros", short: "Outros", tickets: 12, color: "#64748b" },
];

export function CategoryDistribution() {
  const total = categories.reduce((sum, c) => sum + c.tickets, 0);

  return (
    <div className="h-full bg-slate-800/50 backdrop-blur-sm rounded-xl border border-slate-700/50 p-4 shadow-xl flex flex-col">
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-white flex items-center gap-2">
          <Tags className="w-5 h-5 text-purple-400" />
          Top 50 - Atribuição por Categorias
        </h2>
        <div className="text-xs text-slate-400 bg-slate-900/50 px-3 py-1 rounded-full border border-slate-700/30">
          {total} tickets
        </div>
      </div>
      
      <div className="flex-1 grid grid-cols-2 gap-4">
        {/* Pie Chart */}
        <div className="bg-slate-900/50 rounded-lg p-3 border border-slate-700/30">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={categories}
                cx="50%"
                cy="50%"
                innerRadius={45}
                outerRadius={75}
                paddingAngle={2}
                dataKey="tickets"
              >
                {categories.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  backgroundColor: "#1e293b",
                  border: "1px solid #334155",
                  borderRadius: "8px",
                  fontSize: "12px",
                }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* List */}
        <div className="bg-slate-900/50 rounded-lg p-3 border border-slate-700/30 space-y-2 overflow-y-auto">
          {categories.map((category, index) => {
            const percentage = ((category.tickets / total) * 100).toFixed(1);
            return (
              <div key={index} className="flex items-center justify-between group hover:bg-slate-800/50 p-1.5 rounded transition-colors">
                <div className="flex items-center gap-2 flex-1 min-w-0">
                  <div 
                    className="w-3 h-3 rounded-full shrink-0"
                    style={{ backgroundColor: category.color }}
                  />
                  <div className="text-xs text-slate-300 truncate">
                    {category.name}
                  </div>
                </div>
                <div className="flex items-center gap-2 ml-2 shrink-0">
                  <div className="text-sm text-white tabular-nums">{category.tickets}</div>
                  <div className="text-xs text-slate-500 w-12 text-right">{percentage}%</div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

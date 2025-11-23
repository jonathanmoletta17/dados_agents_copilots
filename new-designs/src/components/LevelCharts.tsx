import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, PieChart, Pie, Legend } from "recharts";

const levelsData = [
  { level: "N1", total: 60, novos: 1, progresso: 2, pendentes: 1, resolvidos: 56 },
  { level: "N2", total: 140, novos: 1, progresso: 11, pendentes: 2, resolvidos: 126 },
  { level: "N3", total: 239, novos: 1, progresso: 9, pendentes: 0, resolvidos: 229 },
  { level: "N4", total: 0, novos: 0, progresso: 0, pendentes: 0, resolvidos: 0 },
];

const pieData = [
  { name: "N1", value: 60, color: "#3b82f6" },
  { name: "N2", value: 140, color: "#8b5cf6" },
  { name: "N3", value: 239, color: "#06b6d4" },
  { name: "N4", value: 0, color: "#64748b" },
];

const COLORS = {
  novos: "#3b82f6",
  progresso: "#f59e0b",
  pendentes: "#eab308",
  resolvidos: "#10b981",
};

export function LevelCharts() {
  return (
    <div className="h-full bg-slate-800/50 backdrop-blur-sm rounded-xl border border-slate-700/50 p-4 shadow-xl">
      <h2 className="text-white mb-3 flex items-center gap-2">
        <div className="w-1 h-6 bg-gradient-to-b from-blue-500 to-purple-600 rounded-full" />
        Distribuição por Níveis de Suporte
      </h2>

      <div className="grid grid-cols-5 gap-4 h-[calc(100%-3rem)]">
        {/* Bar Chart - 3 columns */}
        <div className="col-span-3 bg-slate-900/50 rounded-lg p-3 border border-slate-700/30">
          <div className="text-xs text-slate-400 mb-2">Status por Nível</div>
          <ResponsiveContainer width="100%" height="90%">
            <BarChart data={levelsData} margin={{ top: 5, right: 10, left: -20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.3} />
              <XAxis dataKey="level" stroke="#94a3b8" fontSize={12} />
              <YAxis stroke="#94a3b8" fontSize={10} />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#1e293b",
                  border: "1px solid #334155",
                  borderRadius: "8px",
                  fontSize: "12px",
                }}
                labelStyle={{ color: "#e2e8f0" }}
              />
              <Legend wrapperStyle={{ fontSize: "11px" }} />
              <Bar dataKey="novos" name="Novos" fill={COLORS.novos} radius={[4, 4, 0, 0]} />
              <Bar dataKey="progresso" name="Em Progresso" fill={COLORS.progresso} radius={[4, 4, 0, 0]} />
              <Bar dataKey="pendentes" name="Pendentes" fill={COLORS.pendentes} radius={[4, 4, 0, 0]} />
              <Bar dataKey="resolvidos" name="Resolvidos" fill={COLORS.resolvidos} radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Pie Chart - 2 columns */}
        <div className="col-span-2 bg-slate-900/50 rounded-lg p-3 border border-slate-700/30">
          <div className="text-xs text-slate-400 mb-2">Total por Nível</div>
          <ResponsiveContainer width="100%" height="90%">
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                innerRadius={40}
                outerRadius={70}
                paddingAngle={3}
                dataKey="value"
                label={({ cx, x, y, name, value }: any) => (
                  <text
                    x={x}
                    y={y}
                    fill="#e2e8f0"
                    fontSize="11px"
                    textAnchor={x > cx ? "start" : "end"}
                    dominantBaseline="central"
                  >
                    {`${name}: ${value}`}
                  </text>
                )}
              >
                {pieData.map((entry, index) => (
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
      </div>
    </div>
  );
}

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, PieChart, Pie, Legend } from "recharts";
import { LevelStats } from "../types/api";

interface LevelChartsProps {
  levelStats?: LevelStats;
}

const COLORS = {
  novos: "#3b82f6",
  progresso: "#f59e0b",
  pendentes: "#eab308",
  resolvidos: "#10b981",
};

const PIE_COLORS = {
  N1: "#3b82f6",
  N2: "#8b5cf6",
  N3: "#06b6d4",
  N4: "#64748b",
};

export function LevelCharts({ levelStats }: LevelChartsProps) {
  // Transforma os dados para o gráfico de barras
  const levelsData = levelStats ? [
    { level: "N1", ...levelStats.N1 },
    { level: "N2", ...levelStats.N2 },
    { level: "N3", ...levelStats.N3 },
    { level: "N4", ...levelStats.N4 },
  ] : [];

  // Transforma os dados para o gráfico de pizza (total por nível)
  const pieData = levelStats ? [
    { name: "N1", value: levelStats.N1.total, color: PIE_COLORS.N1 },
    { name: "N2", value: levelStats.N2.total, color: PIE_COLORS.N2 },
    { name: "N3", value: levelStats.N3.total, color: PIE_COLORS.N3 },
    { name: "N4", value: levelStats.N4.total, color: PIE_COLORS.N4 },
  ] : [];

  if (!levelStats) {
    return (
      <div className="h-full bg-slate-800/50 backdrop-blur-sm rounded-xl border border-slate-700/50 p-4 shadow-xl animate-pulse flex flex-col overflow-hidden">
        <div className="h-6 w-48 bg-slate-700 rounded mb-4" />
        <div className="grid grid-cols-5 gap-4 flex-1 min-h-0">
          <div className="col-span-3 bg-slate-900/50 rounded-lg h-full" />
          <div className="col-span-2 bg-slate-900/50 rounded-lg h-full" />
        </div>
      </div>
    );
  }

  return (
    <div className="h-full bg-slate-800/50 backdrop-blur-sm rounded-xl border border-slate-700/50 p-4 shadow-xl flex flex-col overflow-hidden">
      <h2 className="text-white mb-3 flex items-center gap-2">
        <div className="w-1 h-6 bg-gradient-to-b from-blue-500 to-purple-600 rounded-full" />
        Distribuição por Níveis de Suporte
      </h2>

      <div className="grid grid-cols-5 gap-4 flex-1 min-h-0">
        {/* Bar Chart - 3 columns */}
        <div className="col-span-3 bg-slate-900/50 rounded-lg p-3 border border-slate-700/30 h-full">
          <div className="text-xs text-slate-400 mb-2">Status por Nível</div>
          <ResponsiveContainer width="100%" height={280}>
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
              <Bar isAnimationActive={false} dataKey="novos" name="Novos" fill={COLORS.novos} radius={[4, 4, 0, 0]} />
              <Bar isAnimationActive={false} dataKey="em_progresso" name="Em Progresso" fill={COLORS.progresso} radius={[4, 4, 0, 0]} />
              <Bar isAnimationActive={false} dataKey="pendentes" name="Pendentes" fill={COLORS.pendentes} radius={[4, 4, 0, 0]} />
              <Bar isAnimationActive={false} dataKey="resolvidos" name="Resolvidos" fill={COLORS.resolvidos} radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Pie Chart - 2 columns */}
        <div className="col-span-2 bg-slate-900/50 rounded-lg p-3 border border-slate-700/30 h-full">
          <div className="text-xs text-slate-400 mb-2">Total por Nível</div>
          <ResponsiveContainer width="100%" height={280}>
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                innerRadius={40}
                outerRadius={70}
                paddingAngle={3}
                dataKey="value"
                label={({ name, value, cx, cy, midAngle, innerRadius, outerRadius }) => {
                  const RADIAN = Math.PI / 180;
                  const radius = innerRadius + (outerRadius - innerRadius) * 0.8;
                  const x = cx + radius * Math.cos(-midAngle * RADIAN);
                  const y = cy + radius * Math.sin(-midAngle * RADIAN);
                  return (
                    <text x={x} y={y} fill="#e2e8f0" fontSize={11} textAnchor={x > cx ? "start" : "end"} dominantBaseline="central">
                      {`${name}: ${value}`}
                    </text>
                  );
                }}
                labelLine={false}
                isAnimationActive={false}
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

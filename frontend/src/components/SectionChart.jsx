// Bar chart of section-wise scores (Recharts), coloured by score band.
import { Bar, BarChart, CartesianGrid, Cell, LabelList, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { scoreBand } from "@/lib/utils";
import { useTheme } from "./ThemeProvider.jsx";

const ORDER = ["skills", "experience", "education", "projects", "formatting"];

export default function SectionChart({ scores = {} }) {
  const { theme } = useTheme();
  const axis = theme === "dark" ? "#9a9ab3" : "#64748b";
  const grid = theme === "dark" ? "#27273a" : "#e5e7eb";
  const data = ORDER.map((k) => ({ name: k[0].toUpperCase() + k.slice(1), score: scores[k] ?? 0 }));

  return (
    <div className="h-72 w-full">
      <ResponsiveContainer>
        <BarChart data={data} margin={{ top: 20, right: 8, left: -20, bottom: 0 }}>
          <CartesianGrid vertical={false} stroke={grid} strokeDasharray="3 3" />
          <XAxis dataKey="name" tick={{ fill: axis, fontSize: 12 }} axisLine={false} tickLine={false} interval={0} />
          <YAxis domain={[0, 100]} tick={{ fill: axis, fontSize: 12 }} axisLine={false} tickLine={false} />
          <Tooltip
            cursor={{ fill: theme === "dark" ? "#ffffff0d" : "#0000000a" }}
            contentStyle={{
              background: theme === "dark" ? "#13131f" : "#fff",
              border: `1px solid ${grid}`,
              borderRadius: 8,
              fontSize: 13,
            }}
            formatter={(v) => [`${v}/100`, "Score"]}
          />
          <Bar dataKey="score" radius={[6, 6, 0, 0]} maxBarSize={56} animationDuration={900}>
            {data.map((d) => (
              <Cell key={d.name} fill={scoreBand(d.score).color} />
            ))}
            <LabelList dataKey="score" position="top" fill={axis} fontSize={12} fontWeight={600} />
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

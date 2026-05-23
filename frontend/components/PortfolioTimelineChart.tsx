"use client";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

type PortfolioTimelinePoint = {
  date: string;
  portfolio_value: string;
};

type PortfolioTimelineChartProps = {
  data: PortfolioTimelinePoint[];
};

export default function PortfolioTimelineChart({
  data,
}: PortfolioTimelineChartProps) {
  const chartData = data.map((item) => ({
    date: item.date,
    value: Number(item.portfolio_value),
  }));

  return (
    <div className="bg-white rounded-xl shadow p-4 mt-8">
      <h2 className="text-2xl font-bold mb-4">
        Portfolio Value Timeline
      </h2>

      <div className="w-full h-80 min-w-0 min-h-80">
        <ResponsiveContainer width="99%" height={320}>
          <LineChart data={chartData}>
            <XAxis dataKey="date" />
            <YAxis domain={["auto", "auto"]} />
            <Tooltip />
            <Line
              type="monotone"
              dataKey="value"
              strokeWidth={2}
              dot={true}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

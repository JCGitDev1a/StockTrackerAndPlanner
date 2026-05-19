"use client";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

type PriceHistoryPoint = {
  price_date: string;
  price: string;
};

type PriceHistoryChartProps = {
  data: PriceHistoryPoint[];
};

export default function PriceHistoryChart({
  data,
}: PriceHistoryChartProps) {
  const chartData = data.map((item) => ({
    date: item.price_date,
    price: Number(item.price),
  }));

  return (
    <div className="bg-white rounded-xl shadow p-4">
      <h2 className="text-2xl font-bold mb-4">
        Price History
      </h2>

      <div className="w-full h-80">
        <ResponsiveContainer
          width="100%"
          height="100%"
        >
          <LineChart data={chartData}>
            <XAxis dataKey="date" />

            <YAxis domain={["auto", "auto"]} />

            <Tooltip />

            <Line
              type="monotone"
              dataKey="price"
              strokeWidth={2}
              dot={true}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

"use client";

import { useEffect, useState } from "react";

import {
  DashboardSummary,
  fetchAccounts,
  fetchDashboardSummary,
  fetchPerformanceTimeline,
  PortfolioTimelinePoint,
} from "@/lib/api";

import PortfolioTimelineChart from "@/components/PortfolioTimelineChart";


export default function DashboardPage() {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [accountName, setAccountName] = useState("");
  const [error, setError] = useState("");
  const [timeline, setTimeline] =
  useState<PortfolioTimelinePoint[]>([]);

  useEffect(() => {
    async function loadDashboard() {
      const token = localStorage.getItem("access_token");

      if (!token) {
        setError("Not logged in.");
        return;
      }

      try {
        const accounts = await fetchAccounts(token);

        if (accounts.length === 0) {
          setError("No accounts found.");
          return;
        }

        const account = accounts[0];

        setAccountName(account.name);

        const data = await fetchDashboardSummary(
          account.id,
          token
        );

        setSummary(data);

        const timelineData = await fetchPerformanceTimeline(
          account.id,
          token
        );

        setTimeline(timelineData);

      } catch {
        setError("Failed to load dashboard.");
      }
    }

    loadDashboard();
  }, []);

  if (error) {
    return <main className="p-8 text-red-600">{error}</main>;
  }

  if (!summary) {
    return <main className="p-8">Loading dashboard...</main>;
  }

  return (
    <main className="min-h-screen bg-gray-100 p-8">
      <div className="mb-6">
        <h1 className="text-3xl font-bold">
          Portfolio Dashboard
        </h1>

        <p className="text-gray-600 mt-1">
          {accountName}
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <DashboardCard title="Market Value" value={`$${summary.total_market_value}`} />
        <DashboardCard title="Cost Basis" value={`$${summary.total_cost_basis}`} />
        <DashboardCard title="Gain / Loss" value={`$${summary.total_unrealized_gain_loss}`} />
        <DashboardCard title="Monthly Income" value={`$${summary.monthly_dividend_income}`} />
        <DashboardCard title="Annual Income" value={`$${summary.annual_dividend_income}`} />
        <DashboardCard title="Holdings" value={String(summary.holdings_count)} />
      </div>
      <PortfolioTimelineChart data={timeline} />
    </main>
  );
}

function DashboardCard({
  title,
  value,
}: {
  title: string;
  value: string;
}) {
  return (
    <div className="bg-white rounded-xl shadow p-5">
      <div className="text-sm text-gray-500">{title}</div>
      <div className="text-2xl font-bold mt-2">{value}</div>
    </div>
  );
}

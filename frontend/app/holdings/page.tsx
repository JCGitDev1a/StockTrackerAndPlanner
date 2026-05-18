"use client";

import { useEffect, useState } from "react";

import {
  fetchAccounts,
  fetchHoldings,
  Holding,
} from "@/lib/api";

import {
  formatCurrency,
  formatNumber,
  gainLossColor,
} from "@/lib/format";

export default function HoldingsPage() {
  const [holdings, setHoldings] = useState<Holding[]>([]);
  const [accountName, setAccountName] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadHoldings() {
      const token = localStorage.getItem(
        "access_token"
      );

      if (!token) {
        setError("Not logged in.");
        return;
      }

      try {
        const accounts = await fetchAccounts(
          token
        );

        if (accounts.length === 0) {
          setError("No accounts found.");
          return;
        }

        const account = accounts[0];

        setAccountName(account.name);

        const data = await fetchHoldings(
          account.id,
          token
        );

        setHoldings(data);
      } catch {
        setError("Failed to load holdings.");
      }
    }

    loadHoldings();
  }, []);

  if (error) {
    return (
      <main className="p-8 text-red-600">
        {error}
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-gray-100 p-8">
      <div className="mb-6">
        <h1 className="text-3xl font-bold">
          Holdings
        </h1>

        <p className="text-gray-600 mt-1">
          {accountName}
        </p>
      </div>

      <div className="bg-white rounded-xl shadow overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-gray-200">
            <tr>
              <th className="text-left p-3">
                Symbol
              </th>

              <th className="text-left p-3">
                Company
              </th>

              <th className="text-right p-3">
                Shares
              </th>

              <th className="text-right p-3">
                Avg Cost
              </th>

              <th className="text-right p-3">
                Current Price
              </th>

              <th className="text-right p-3">
                Market Value
              </th>

              <th className="text-right p-3">
                Gain / Loss
              </th>
            </tr>
          </thead>

          <tbody>
            {holdings.map((holding) => (
              <tr
                key={holding.security_id}
                className="border-t"
              >
                <td className="p-3 font-medium">
                  {holding.symbol}
                </td>

                <td className="p-3">
                  {holding.company}
                </td>

                <td className="p-3 text-right">
                  {formatNumber(holding.shares, 4)}
                </td>

                <td className="p-3 text-right">
                  {formatCurrency(holding.average_cost)}
                </td>

                <td className="p-3 text-right">
                  {formatCurrency(holding.current_price)}
                </td>

                <td className="p-3 text-right">
                  {formatCurrency(holding.market_value)}
                </td>

                <td
                  className={`p-3 text-right ${gainLossColor(
                    holding.unrealized_gain_loss
                  )}`}
                >
                  {formatCurrency(
                    holding.unrealized_gain_loss
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </main>
  );
}

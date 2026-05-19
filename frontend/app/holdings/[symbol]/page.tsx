"use client";

import { useEffect, useState } from "react";

import {
  fetchAccounts,
  fetchHolding,
  fetchHoldingTransactions,
  Holding,
  Transaction,
  fetchDividendEvents,
  DividendEvent,
  fetchPriceHistory,
  PriceHistoryPoint,
} from "@/lib/api";

import {
  formatCurrency,
  formatNumber,
  gainLossColor,
} from "@/lib/format";

import PriceHistoryChart from "@/components/PriceHistoryChart";

type HoldingDetailPageProps = {
  params: Promise<{
    symbol: string;
  }>;
};

export default function HoldingDetailPage({
  params,
}: HoldingDetailPageProps) {
  const [holding, setHolding] =
    useState<Holding | null>(null);

  const [transactions, setTransactions] =
    useState<Transaction[]>([]);

  const [accountName, setAccountName] =
    useState("");

  const [dividendEvents, setDividendEvents] =
    useState<DividendEvent[]>([]);

  const [priceHistory, setPriceHistory] =
    useState<PriceHistoryPoint[]>([]);

  const [error, setError] = useState("");

  useEffect(() => {
    async function loadHolding() {
      const token =
        localStorage.getItem("access_token");

      if (!token) {
        setError("Not logged in.");
        return;
      }

      try {
        const resolvedParams = await params;

        const accounts = await fetchAccounts(
          token
        );

        if (accounts.length === 0) {
          setError("No accounts found.");
          return;
        }

        const account = accounts[0];

        setAccountName(account.name);

        const data = await fetchHolding(
          account.id,
          resolvedParams.symbol,
          token
        );

        setHolding(data);

        const transactionData =
          await fetchHoldingTransactions(
            account.id,
            resolvedParams.symbol,
            token
          );

        setTransactions(transactionData);

        const dividendData = await fetchDividendEvents(
          resolvedParams.symbol,
          token
        );

        setDividendEvents(dividendData);

        const priceData = await fetchPriceHistory(
          resolvedParams.symbol,
          token
        );

        setPriceHistory(priceData);

      } catch {
        setError("Failed to load holding.");
      }
    }

    loadHolding();
  }, [params]);

  if (error) {
    return (
      <main className="p-8 text-red-600">
        {error}
      </main>
    );
  }

  if (!holding) {
    return (
      <main className="p-8">
        Loading holding...
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-gray-100 p-8">
      <div className="mb-6">
        <h1 className="text-4xl font-bold">
          {holding.symbol}
        </h1>

        <p className="text-gray-600 mt-1">
          {holding.company}
        </p>

        <p className="text-sm text-gray-500 mt-1">
          {accountName}
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <DetailCard
          title="Shares"
          value={formatNumber(
            holding.shares,
            4
          )}
        />

        <DetailCard
          title="Average Cost"
          value={formatCurrency(
            holding.average_cost
          )}
        />

        <DetailCard
          title="Current Price"
          value={formatCurrency(
            holding.current_price
          )}
        />

        <DetailCard
          title="Market Value"
          value={formatCurrency(
            holding.market_value
          )}
        />

        <DetailCard
          title="Cost Basis"
          value={formatCurrency(
            holding.total_basis
          )}
        />

        <DetailCard
          title="Gain / Loss"
          value={formatCurrency(
            holding.unrealized_gain_loss
          )}
          valueClassName={gainLossColor(
            holding.unrealized_gain_loss
          )}
        />
      </div>

      <div className="mt-8">
        <PriceHistoryChart data={priceHistory} />
      </div>

      <div className="mt-8">      
        <h2 className="text-2xl font-bold mb-4">      
          Recent Transactions      
        </h2>      
            
        <div className="bg-white rounded-xl shadow overflow-x-auto">      
          <table className="w-full text-sm">      
            <thead className="bg-gray-200">      
              <tr>      
                <th className="text-left p-3">      
                  Date      
                </th>      
            
                <th className="text-left p-3">      
                  Type      
                </th>      
            
                <th className="text-right p-3">      
                  Shares      
                </th>      
            
                <th className="text-right p-3">      
                  Price      
                </th>      
            
                <th className="text-right p-3">      
                  Cash Amount      
                </th>      
              </tr>      
            </thead>      
            
            <tbody>      
              {transactions.map((tx) => (      
                <tr      
                  key={tx.id}      
                  className="border-t"      
                >      
                  <td className="p-3">      
                    {tx.transaction_date}      
                  </td>      
            
                  <td className="p-3">      
                    {tx.type}      
                  </td>      
            
                  <td className="p-3 text-right">      
                    {formatNumber(tx.shares, 4)}      
                  </td>      
            
                  <td className="p-3 text-right">      
                    {formatCurrency(tx.price)}      
                  </td>      
            
                  <td className="p-3 text-right">      
                    {formatCurrency(      
                      tx.cash_amount      
                    )}      
                  </td>      
                </tr>      
              ))}      
            </tbody>      
          </table>      
        </div>      
      </div>
      
      <div className="mt-8">
        <h2 className="text-2xl font-bold mb-4">
          Dividend History
        </h2>
      
        <div className="bg-white rounded-xl shadow overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-200">
              <tr>
                <th className="text-left p-3">Ex Date</th>
                <th className="text-left p-3">Pay Date</th>
                <th className="text-right p-3">Amount</th>
                <th className="text-left p-3">Source</th>
              </tr>
            </thead>
      
            <tbody>
              {dividendEvents.map((event) => (
                <tr key={event.id} className="border-t">
                  <td className="p-3">{event.ex_date ?? "-"}</td>
                  <td className="p-3">{event.pay_date}</td>
                  <td className="p-3 text-right">
                    {formatCurrency(event.amount)}
                  </td>
                  <td className="p-3">{event.source_provider}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </main>
  );
}

function DetailCard({
  title,
  value,
  valueClassName = "",
}: {
  title: string;
  value: string;
  valueClassName?: string;
}) {
  return (
    <div className="bg-white rounded-xl shadow p-5">
      <div className="text-sm text-gray-500">
        {title}
      </div>

      <div
        className={`text-2xl font-bold mt-2 ${valueClassName}`}
      >
        {value}
      </div>
    </div>
  );
}

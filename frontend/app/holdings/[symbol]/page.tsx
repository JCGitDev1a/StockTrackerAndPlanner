type HoldingDetailPageProps = {
  params: Promise<{
    symbol: string;
  }>;
};

export default async function HoldingDetailPage({
  params,
}: HoldingDetailPageProps) {
  const { symbol } = await params;

  return (
    <main className="min-h-screen bg-gray-100 p-8">
      <h1 className="text-3xl font-bold">
        {symbol.toUpperCase()}
      </h1>

      <p className="text-gray-600 mt-2">
        Holding detail page coming soon.
      </p>
    </main>
  );
}

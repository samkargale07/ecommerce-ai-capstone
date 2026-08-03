import { getCategorySales, getMonthlyTrends, getTopProducts } from "../lib/api";
import AnalyticsCharts from "../components/AnalyticsCharts";

export const dynamic = "force-dynamic";

export default async function DashboardPage() {
  let categorySales, monthlyTrends, topProducts;
  let error: string | null = null;

  try {
    [categorySales, monthlyTrends, topProducts] = await Promise.all([
      getCategorySales(),
      getMonthlyTrends(),
      getTopProducts(10),
    ]);
  } catch (e) {
    error = "Could not reach the API. Is the FastAPI backend running on port 8000?";
    categorySales = [];
    monthlyTrends = [];
    topProducts = [];
  }

  return (
    <div className="max-w-6xl mx-auto px-6 py-12">
      <div className="mb-10 max-w-2xl">
        <p className="font-mono-data text-xs uppercase tracking-wider mb-2" style={{ color: "var(--accent)" }}>
          Day 3 · Big Data Analytics
        </p>
        <h1 className="font-display text-4xl font-semibold mb-3" style={{ color: "var(--ink)" }}>
          What the numbers say.
        </h1>
        <p style={{ color: "var(--ink-soft)" }}>
          Pre-computed from ~99,000 real orders using Pandas aggregation — not calculated
          live on every page load.
        </p>
      </div>

      {error && (
        <div
          className="mb-8 p-4 rounded border text-sm"
          style={{ borderColor: "var(--accent)", color: "var(--accent)", background: "#fdf0ea" }}
        >
          {error}
        </div>
      )}

      {!error && (
        <AnalyticsCharts
          categorySales={categorySales}
          monthlyTrends={monthlyTrends}
          topProducts={topProducts}
        />
      )}
    </div>
  );
}

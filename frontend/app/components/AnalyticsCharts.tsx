"use client";

import {
  ResponsiveContainer,
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from "recharts";
import type { CategorySales, MonthlyTrend, TopProduct } from "../lib/api";

const COLORS = {
  primary: "#0f6b5c",
  accent: "#f2734a",
  sandLine: "#d9d0bd",
  inkSoft: "#5a5750",
};

function formatCategoryLabel(name: string) {
  return name.replace(/_/g, " ").replace(/^\w/, (c) => c.toUpperCase());
}

function CustomTooltip({ active, payload, label }: any) {
  if (!active || !payload || !payload.length) return null;
  return (
    <div
      className="rounded-lg border px-3 py-2 text-xs shadow-md"
      style={{ background: "white", borderColor: COLORS.sandLine }}
    >
      <p className="font-medium mb-1">{label}</p>
      {payload.map((p: any, i: number) => (
        <p key={i} style={{ color: p.color }}>
          {p.name}: {typeof p.value === "number" ? p.value.toLocaleString() : p.value}
        </p>
      ))}
    </div>
  );
}

export default function AnalyticsCharts({
  categorySales,
  monthlyTrends,
  topProducts,
}: {
  categorySales: CategorySales[];
  monthlyTrends: MonthlyTrend[];
  topProducts: TopProduct[];
}) {
  const topCategories = [...categorySales]
    .sort((a, b) => b.total_revenue - a.total_revenue)
    .slice(0, 8)
    .map((c) => ({ ...c, label: formatCategoryLabel(c.product_category_name) }));

  const totalRevenue = categorySales.reduce((sum, c) => sum + c.total_revenue, 0);
  const totalOrders = categorySales.reduce((sum, c) => sum + c.total_orders, 0);
  const avgOrderValue = totalOrders > 0 ? totalRevenue / totalOrders : 0;

  return (
    <div className="space-y-12">
      {/* KPI strip */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: "Total Revenue", value: `$${totalRevenue.toLocaleString(undefined, { maximumFractionDigits: 0 })}` },
          { label: "Total Orders", value: totalOrders.toLocaleString() },
          { label: "Avg Order Value", value: `$${avgOrderValue.toFixed(2)}` },
          { label: "Categories Tracked", value: categorySales.length.toString() },
        ].map((kpi) => (
          <div
            key={kpi.label}
            className="rounded-lg border p-4"
            style={{ borderColor: "var(--sand-line)", background: "white" }}
          >
            <p className="text-xs uppercase tracking-wide mb-1" style={{ color: "var(--ink-soft)" }}>
              {kpi.label}
            </p>
            <p className="font-display text-2xl font-semibold" style={{ color: "var(--primary-dark)" }}>
              {kpi.value}
            </p>
          </div>
        ))}
      </div>

      {/* Monthly revenue trend */}
      <section>
        <h2 className="font-display text-2xl font-semibold mb-1" style={{ color: "var(--ink)" }}>
          Revenue over time
        </h2>
        <p className="text-sm mb-4" style={{ color: "var(--ink-soft)" }}>
          Monthly totals computed by the Day 3 Pandas aggregation pipeline.
        </p>
        <div
          className="rounded-lg border p-4"
          style={{ borderColor: "var(--sand-line)", background: "white" }}
        >
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={monthlyTrends}>
              <CartesianGrid strokeDasharray="3 3" stroke={COLORS.sandLine} />
              <XAxis dataKey="sales_month" tick={{ fontSize: 11, fill: COLORS.inkSoft }} />
              <YAxis tick={{ fontSize: 11, fill: COLORS.inkSoft }} />
              <Tooltip content={<CustomTooltip />} />
              <Line
                type="monotone"
                dataKey="total_revenue"
                name="Revenue ($)"
                stroke={COLORS.primary}
                strokeWidth={2}
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </section>

      {/* Top categories by revenue */}
      <section>
        <h2 className="font-display text-2xl font-semibold mb-1" style={{ color: "var(--ink)" }}>
          Top categories by revenue
        </h2>
        <p className="text-sm mb-4" style={{ color: "var(--ink-soft)" }}>
          The 8 highest-earning categories across the full order history.
        </p>
        <div
          className="rounded-lg border p-4"
          style={{ borderColor: "var(--sand-line)", background: "white" }}
        >
          <ResponsiveContainer width="100%" height={320}>
            <BarChart data={topCategories} layout="vertical" margin={{ left: 40 }}>
              <CartesianGrid strokeDasharray="3 3" stroke={COLORS.sandLine} horizontal={false} />
              <XAxis type="number" tick={{ fontSize: 11, fill: COLORS.inkSoft }} />
              <YAxis
                type="category"
                dataKey="label"
                width={110}
                tick={{ fontSize: 11, fill: COLORS.inkSoft }}
              />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="total_revenue" name="Revenue ($)" fill={COLORS.accent} radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </section>

      {/* Top products table */}
      <section>
        <h2 className="font-display text-2xl font-semibold mb-1" style={{ color: "var(--ink)" }}>
          Best-selling products
        </h2>
        <p className="text-sm mb-4" style={{ color: "var(--ink-soft)" }}>
          Ranked by total revenue (Day 3 analytics).
        </p>
        <div className="rounded-lg border overflow-hidden" style={{ borderColor: "var(--sand-line)" }}>
          <table className="w-full text-sm">
            <thead>
              <tr style={{ background: "var(--sand)" }}>
                <th className="text-left px-4 py-2 font-medium" style={{ color: "var(--ink-soft)" }}>
                  Product
                </th>
                <th className="text-left px-4 py-2 font-medium" style={{ color: "var(--ink-soft)" }}>
                  Category
                </th>
                <th className="text-right px-4 py-2 font-medium" style={{ color: "var(--ink-soft)" }}>
                  Units Sold
                </th>
                <th className="text-right px-4 py-2 font-medium" style={{ color: "var(--ink-soft)" }}>
                  Revenue
                </th>
              </tr>
            </thead>
            <tbody>
              {topProducts.map((p, i) => (
                <tr
                  key={p.product_id}
                  style={{ borderTop: i > 0 ? `1px solid var(--sand-line)` : "none", background: "white" }}
                >
                  <td className="px-4 py-2">
                    <span className="product-id-tag">{p.product_id.slice(0, 14)}…</span>
                  </td>
                  <td className="px-4 py-2 capitalize" style={{ color: "var(--ink)" }}>
                    {(p.product_category_name || "—").replace(/_/g, " ")}
                  </td>
                  <td className="px-4 py-2 text-right font-mono-data">{p.total_quantity_sold}</td>
                  <td className="px-4 py-2 text-right font-mono-data" style={{ color: "var(--primary-dark)" }}>
                    ${p.total_revenue.toLocaleString(undefined, { maximumFractionDigits: 2 })}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}

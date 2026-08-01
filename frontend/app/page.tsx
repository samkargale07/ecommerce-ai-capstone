import Link from "next/link";
import { getProducts } from "./lib/api";

export const dynamic = "force-dynamic";

export default async function HomePage() {
  let products;
  let error: string | null = null;

  try {
    products = await getProducts(24);
  } catch (e) {
    error = "Could not reach the API. Is the FastAPI backend running on port 8000?";
    products = [];
  }

  return (
    <div className="max-w-6xl mx-auto px-6 py-12">
      <div className="mb-10 max-w-2xl">
        <p className="font-mono-data text-xs uppercase tracking-wider mb-2" style={{ color: "var(--accent)" }}>
          {products.length} products indexed
        </p>
        <h1 className="font-display text-4xl font-semibold mb-3" style={{ color: "var(--ink)" }}>
          A catalog built on real transactions.
        </h1>
        <p style={{ color: "var(--ink-soft)" }}>
          Every product below comes from actual order data — recommendations, categories,
          and dimensions are all computed from real purchase patterns, not placeholders.
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

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-5">
        {products.map((product) => (
          <Link
            key={product.product_id}
            href={`/products/${product.product_id}`}
            className="group block rounded-lg border p-4 transition hover:shadow-md"
            style={{ borderColor: "var(--sand-line)", background: "white" }}
          >
            <div
              className="w-full aspect-square rounded mb-3 flex items-center justify-center"
              style={{ background: "var(--sand)" }}
            >
              <span className="font-display text-lg" style={{ color: "var(--primary)" }}>
                {(product.product_category_name || "?").slice(0, 2).toUpperCase()}
              </span>
            </div>
            <p className="text-sm font-medium mb-1 capitalize" style={{ color: "var(--ink)" }}>
              {(product.product_category_name_english || product.product_category_name || "uncategorized").replace(/_/g, " ")}
            </p>
            <p className="text-xs mb-2" style={{ color: "var(--ink-soft)" }}>
              {product.product_weight_g ? `${product.product_weight_g}g` : "—"}
              {product.product_length_cm && ` · ${product.product_length_cm}×${product.product_height_cm}×${product.product_width_cm}cm`}
            </p>
            <span className="product-id-tag">{product.product_id.slice(0, 12)}…</span>
          </Link>
        ))}
      </div>

      {!error && products.length === 0 && (
        <p style={{ color: "var(--ink-soft)" }}>No products found.</p>
      )}
    </div>
  );
}

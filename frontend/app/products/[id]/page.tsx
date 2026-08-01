import Link from "next/link";
import { getProduct, getRecommendations } from "../../lib/api";

export const dynamic = "force-dynamic";

export default async function ProductDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;

  let product;
  let recommendations;
  let error: string | null = null;

  try {
    [product, recommendations] = await Promise.all([
      getProduct(id),
      getRecommendations(id).catch(() => []),
    ]);
  } catch (e) {
    error = "Product not found.";
  }

  if (error || !product) {
    return (
      <div className="max-w-3xl mx-auto px-6 py-16 text-center">
        <p className="font-display text-2xl mb-2">Product not found</p>
        <p style={{ color: "var(--ink-soft)" }} className="mb-6">
          This ID doesn&apos;t exist in the catalog.
        </p>
        <Link href="/" className="underline" style={{ color: "var(--primary)" }}>
          Back to catalog
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-6 py-12">
      <Link href="/" className="text-sm underline mb-8 inline-block" style={{ color: "var(--primary)" }}>
        ← Back to catalog
      </Link>

      <div className="grid md:grid-cols-2 gap-10 mb-16">
        <div
          className="aspect-square rounded-lg flex items-center justify-center"
          style={{ background: "var(--sand)" }}
        >
          <span className="font-display text-5xl" style={{ color: "var(--primary)" }}>
            {(product.product_category_name || "?").slice(0, 2).toUpperCase()}
          </span>
        </div>

        <div>
          <p className="product-id-tag mb-4">{product.product_id}</p>
          <h1 className="font-display text-3xl font-semibold mb-1 capitalize" style={{ color: "var(--ink)" }}>
            {(product.product_category_name_english || product.product_category_name || "Uncategorized").replace(/_/g, " ")}
          </h1>
          {product.product_category_name_english && product.product_category_name && (
            <p className="text-xs mb-4" style={{ color: "var(--ink-soft)" }}>
              Original category (Portuguese): {product.product_category_name.replace(/_/g, " ")}
            </p>
          )}
          <dl className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <dt style={{ color: "var(--ink-soft)" }}>Weight</dt>
              <dd className="font-mono-data">{product.product_weight_g ?? "—"} g</dd>
            </div>
            <div>
              <dt style={{ color: "var(--ink-soft)" }}>Length</dt>
              <dd className="font-mono-data">{product.product_length_cm ?? "—"} cm</dd>
            </div>
            <div>
              <dt style={{ color: "var(--ink-soft)" }}>Height</dt>
              <dd className="font-mono-data">{product.product_height_cm ?? "—"} cm</dd>
            </div>
            <div>
              <dt style={{ color: "var(--ink-soft)" }}>Width</dt>
              <dd className="font-mono-data">{product.product_width_cm ?? "—"} cm</dd>
            </div>
          </dl>
        </div>
      </div>

      <section>
        <h2 className="font-display text-2xl font-semibold mb-1" style={{ color: "var(--ink)" }}>
          Recommended alongside this
        </h2>
        <p className="text-sm mb-6" style={{ color: "var(--ink-soft)" }}>
          Computed from co-purchase patterns and attribute similarity (Day 5 ML pipeline).
        </p>

        {recommendations.length === 0 ? (
          <p
            className="text-sm p-4 rounded border"
            style={{ borderColor: "var(--sand-line)", color: "var(--ink-soft)" }}
          >
            No recommendations available for this product yet — it may not have appeared
            in enough multi-item orders for collaborative filtering.
          </p>
        ) : (
          <div className="grid sm:grid-cols-2 gap-3">
            {recommendations.map((rec) => (
              <Link
                key={`${rec.recommended_product_id}-${rec.method}`}
                href={`/products/${rec.recommended_product_id}`}
                className="block rounded-lg border p-4 hover:shadow-md transition"
                style={{ borderColor: "var(--sand-line)", background: "white" }}
              >
                <div className="flex items-center justify-between mb-2">
                  <span
                    className="text-xs uppercase tracking-wide px-2 py-0.5 rounded-full"
                    style={{
                      background: rec.method === "collaborative" ? "var(--mint)" : "#fdf0ea",
                      color: rec.method === "collaborative" ? "var(--primary-dark)" : "var(--accent)",
                    }}
                  >
                    {rec.method}
                  </span>
                  <span className="font-mono-data text-xs" style={{ color: "var(--ink-soft)" }}>
                    {(rec.score * 100).toFixed(0)}% match
                  </span>
                </div>
                <span className="product-id-tag">{rec.recommended_product_id.slice(0, 16)}…</span>
              </Link>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

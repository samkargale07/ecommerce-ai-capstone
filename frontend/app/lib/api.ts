// Typed client for the FastAPI backend built in Days 4-9.
// Centralizing fetch calls here means every page shares the same
// error handling and base URL configuration.

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface Product {
  product_id: string;
  product_category_name: string | null;
  product_category_name_english: string | null;
  product_weight_g: number | null;
  product_length_cm: number | null;
  product_height_cm: number | null;
  product_width_cm: number | null;
}

export interface Category {
  product_category_name: string;
  product_category_name_english: string | null;
}

export interface Recommendation {
  recommended_product_id: string;
  method: string;
  score: number;
}

async function apiFetch<T>(path: string): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, { cache: "no-store" });
  if (!res.ok) {
    throw new Error(`API request failed: ${path} (${res.status})`);
  }
  return res.json();
}

export interface AgentResponse {
  query: string;
  answer: string;
  tools_available: string[];
}

export function getProducts(limit = 24, category?: string): Promise<Product[]> {
  const params = new URLSearchParams({ limit: String(limit) });
  if (category) params.set("category", category);
  return apiFetch<Product[]>(`/products/?${params.toString()}`);
}

export function getCategories(): Promise<Category[]> {
  return apiFetch<Category[]>(`/products/categories`);
}

export function getProduct(id: string): Promise<Product> {
  return apiFetch<Product>(`/products/${id}`);
}

export function getRecommendations(id: string): Promise<Recommendation[]> {
  return apiFetch<Recommendation[]>(`/products/${id}/recommendations`);
}

export function searchProducts(query: string, limit = 24): Promise<Product[]> {
  const params = new URLSearchParams({ q: query, limit: String(limit) });
  return apiFetch<Product[]>(`/products/semantic-search?${params.toString()}`);
}

export function askAgent(query: string): Promise<AgentResponse> {
  const params = new URLSearchParams({ q: query });
  return apiFetch<AgentResponse>(`/agent/?${params.toString()}`);
}

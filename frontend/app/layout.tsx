import type { Metadata } from "next";
import { Fraunces, Inter, IBM_Plex_Mono } from "next/font/google";
import Link from "next/link";
import "./globals.css";

const fraunces = Fraunces({
  subsets: ["latin"],
  variable: "--font-fraunces",
  weight: ["500", "600", "700"],
});

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

const plexMono = IBM_Plex_Mono({
  subsets: ["latin"],
  variable: "--font-plex-mono",
  weight: ["400", "500"],
});

export const metadata: Metadata = {
  title: "Mercado — AI Shopping Assistant",
  description: "An AI-powered product catalog and shopping assistant built on real Brazilian e-commerce data.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${fraunces.variable} ${inter.variable} ${plexMono.variable} antialiased`}>
        <header className="border-b" style={{ borderColor: "var(--sand-line)" }}>
          <div className="max-w-6xl mx-auto px-6 py-5 flex items-center justify-between">
            <Link href="/" className="font-display text-2xl font-semibold" style={{ color: "var(--primary-dark)" }}>
              Mercado
            </Link>
            <nav className="flex gap-6 text-sm" style={{ color: "var(--ink-soft)" }}>
              <Link href="/" className="hover:underline">Catalog</Link>
            </nav>
          </div>
        </header>
        <main>{children}</main>
      </body>
    </html>
  );
}

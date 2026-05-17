import type { Metadata } from "next";
import { Inter } from "next/font/google";
import Link from "next/link";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "AI SaaS Platform",
  description: "RAG Chatbot & AI Data Analyst",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="h-full">
      <body className={`${inter.className} min-h-full flex flex-col`}>
        <nav className="border-b bg-white">
          <div className="max-w-6xl mx-auto px-4 py-3 flex items-center gap-8">
            <Link href="/" className="font-bold text-lg">
              AI SaaS
            </Link>
            <Link
              href="/chat"
              className="text-sm text-gray-600 hover:text-gray-900"
            >
              RAG Chat
            </Link>
            <Link
              href="/analyst"
              className="text-sm text-gray-600 hover:text-gray-900"
            >
              Data Analyst
            </Link>
          </div>
        </nav>
        <main className="flex-1 flex flex-col">{children}</main>
      </body>
    </html>
  );
}

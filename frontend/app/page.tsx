import Link from "next/link";
import { MessageSquare, BarChart3 } from "lucide-react";

export default function Home() {
  return (
    <div className="flex-1 flex items-center justify-center">
      <div className="max-w-2xl mx-auto text-center px-4">
        <h1 className="text-4xl font-bold mb-4">AI SaaS Platform</h1>
        <p className="text-gray-600 mb-10 text-lg">
          Upload your documents and data. Ask questions. Get answers.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Link
            href="/chat"
            className="border rounded-xl p-8 hover:border-blue-500 hover:shadow-md transition-all group"
          >
            <MessageSquare className="h-10 w-10 mx-auto mb-4 text-blue-600 group-hover:scale-110 transition-transform" />
            <h2 className="text-xl font-semibold mb-2">RAG Chatbot</h2>
            <p className="text-gray-500 text-sm">
              Upload PDFs or website links and ask questions based on your
              documents.
            </p>
          </Link>

          <Link
            href="/analyst"
            className="border rounded-xl p-8 hover:border-green-500 hover:shadow-md transition-all group"
          >
            <BarChart3 className="h-10 w-10 mx-auto mb-4 text-green-600 group-hover:scale-110 transition-transform" />
            <h2 className="text-xl font-semibold mb-2">Data Analyst</h2>
            <p className="text-gray-500 text-sm">
              Upload CSV or Excel files and get insights, charts, and answers in
              natural language.
            </p>
          </Link>
        </div>
      </div>
    </div>
  );
}

"use client";

import { useState, useEffect } from "react";
import { FileText, Globe, Loader2, X } from "lucide-react";
import ChatWindow, { Message } from "@/components/ChatWindow";
import FileUpload from "@/components/FileUpload";
import {
  uploadPDF,
  uploadURL,
  listDocuments,
  queryRAG,
  DocumentInfo,
} from "@/lib/api";

export default function ChatPage() {
  const [documents, setDocuments] = useState<DocumentInfo[]>([]);
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [urlInput, setUrlInput] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    listDocuments().then(setDocuments).catch(() => {});
  }, []);

  const handlePDF = async (file: File) => {
    setUploading(true);
    setError("");
    try {
      const doc = await uploadPDF(file);
      setDocuments((prev) => [...prev, doc]);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setUploading(false);
    }
  };

  const handleURL = async () => {
    if (!urlInput.trim()) return;
    setUploading(true);
    setError("");
    try {
      const doc = await uploadURL(urlInput.trim());
      setDocuments((prev) => [...prev, doc]);
      setUrlInput("");
    } catch (e: any) {
      setError(e.message);
    } finally {
      setUploading(false);
    }
  };

  const handleSend = async (question: string) => {
    setMessages((prev) => [...prev, { role: "user", content: question }]);
    setLoading(true);
    try {
      const res = await queryRAG(question);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: res.answer, sources: res.sources },
      ]);
    } catch (e: any) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Error: " + e.message },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex-1 flex">
      {/* Sidebar */}
      <div className="w-80 border-r bg-gray-50 p-4 flex flex-col gap-4 overflow-y-auto">
        <h2 className="font-semibold text-lg">Documents</h2>

        <FileUpload
          accept={{ "application/pdf": [".pdf"] }}
          onFile={handlePDF}
          label="Drop a PDF here or click to upload"
          disabled={uploading}
        />

        <div className="flex gap-2">
          <input
            type="text"
            value={urlInput}
            onChange={(e) => setUrlInput(e.target.value)}
            placeholder="https://example.com"
            className="flex-1 border rounded px-3 py-2 text-sm"
            onKeyDown={(e) => e.key === "Enter" && handleURL()}
          />
          <button
            onClick={handleURL}
            disabled={uploading || !urlInput.trim()}
            className="bg-blue-600 text-white rounded px-3 py-2 text-sm hover:bg-blue-700 disabled:opacity-50"
          >
            <Globe className="h-4 w-4" />
          </button>
        </div>

        {uploading && (
          <div className="flex items-center gap-2 text-sm text-gray-500">
            <Loader2 className="h-4 w-4 animate-spin" /> Processing...
          </div>
        )}

        {error && (
          <p className="text-red-500 text-sm">{error}</p>
        )}

        <div className="space-y-2 mt-2">
          {documents.map((doc) => (
            <div
              key={doc.id}
              className="flex items-center gap-2 bg-white border rounded p-2 text-sm"
            >
              <FileText className="h-4 w-4 text-blue-500 shrink-0" />
              <span className="truncate flex-1">{doc.filename}</span>
              <span className="text-gray-400 text-xs shrink-0">
                {doc.chunk_count} chunks
              </span>
            </div>
          ))}
          {documents.length === 0 && (
            <p className="text-gray-400 text-sm text-center">
              No documents uploaded yet
            </p>
          )}
        </div>
      </div>

      {/* Chat */}
      <div className="flex-1 flex flex-col">
        <ChatWindow
          messages={messages}
          onSend={handleSend}
          loading={loading}
          placeholder="Ask a question about your documents..."
        />
      </div>
    </div>
  );
}

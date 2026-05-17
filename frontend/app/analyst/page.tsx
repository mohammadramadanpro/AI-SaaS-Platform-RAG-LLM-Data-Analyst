"use client";

import { useState, useEffect } from "react";
import { Table, Loader2 } from "lucide-react";
import ChatWindow, { Message } from "@/components/ChatWindow";
import FileUpload from "@/components/FileUpload";
import {
  uploadDataset,
  listDatasets,
  queryAnalyst,
  chartURL,
  DatasetInfo,
} from "@/lib/api";

export default function AnalystPage() {
  const [datasets, setDatasets] = useState<DatasetInfo[]>([]);
  const [selectedId, setSelectedId] = useState<string>("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    listDatasets()
      .then((ds) => {
        setDatasets(ds);
        if (ds.length > 0) setSelectedId(ds[0].id);
      })
      .catch(() => {});
  }, []);

  const handleUpload = async (file: File) => {
    setUploading(true);
    setError("");
    try {
      const ds = await uploadDataset(file);
      setDatasets((prev) => [...prev, ds]);
      setSelectedId(ds.id);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setUploading(false);
    }
  };

  const handleSend = async (question: string) => {
    if (!selectedId) {
      setError("Please upload a dataset first");
      return;
    }
    setMessages((prev) => [...prev, { role: "user", content: question }]);
    setLoading(true);
    try {
      const res = await queryAnalyst(question, selectedId);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: res.error ? "" : res.answer,
          chart_url: res.chart_url ? chartURL(res.chart_url) : null,
          error: res.error,
        },
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

  const selected = datasets.find((d) => d.id === selectedId);

  return (
    <div className="flex-1 flex">
      {/* Sidebar */}
      <div className="w-80 border-r bg-gray-50 p-4 flex flex-col gap-4 overflow-y-auto">
        <h2 className="font-semibold text-lg">Datasets</h2>

        <FileUpload
          accept={{
            "text/csv": [".csv"],
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
              [".xlsx"],
            "application/vnd.ms-excel": [".xls"],
          }}
          onFile={handleUpload}
          label="Drop a CSV or Excel file"
          disabled={uploading}
        />

        {uploading && (
          <div className="flex items-center gap-2 text-sm text-gray-500">
            <Loader2 className="h-4 w-4 animate-spin" /> Processing...
          </div>
        )}

        {error && <p className="text-red-500 text-sm">{error}</p>}

        <div className="space-y-2 mt-2">
          {datasets.map((ds) => (
            <button
              key={ds.id}
              onClick={() => setSelectedId(ds.id)}
              className={`w-full text-left flex items-center gap-2 border rounded p-2 text-sm transition-colors ${
                ds.id === selectedId
                  ? "border-green-500 bg-green-50"
                  : "bg-white hover:bg-gray-100"
              }`}
            >
              <Table className="h-4 w-4 text-green-500 shrink-0" />
              <div className="flex-1 truncate">
                <p className="truncate font-medium">{ds.filename}</p>
                <p className="text-gray-400 text-xs">
                  {ds.row_count} rows x {ds.col_count} cols
                </p>
              </div>
            </button>
          ))}
          {datasets.length === 0 && (
            <p className="text-gray-400 text-sm text-center">
              No datasets uploaded yet
            </p>
          )}
        </div>

        {selected && (
          <div className="border rounded p-3 bg-white">
            <p className="text-xs font-semibold text-gray-500 mb-1">Columns</p>
            <div className="flex flex-wrap gap-1">
              {selected.columns.map((col) => (
                <span
                  key={col}
                  className="bg-gray-100 text-gray-700 text-xs px-2 py-0.5 rounded"
                >
                  {col}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Chat */}
      <div className="flex-1 flex flex-col">
        <ChatWindow
          messages={messages}
          onSend={handleSend}
          loading={loading}
          placeholder={
            selectedId
              ? "Ask about your data (e.g., 'show sales by month')..."
              : "Upload a dataset first..."
          }
        />
      </div>
    </div>
  );
}

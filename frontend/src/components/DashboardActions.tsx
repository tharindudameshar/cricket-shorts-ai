"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { Trash2 } from "lucide-react";
import { api } from "@/lib/api";

export function DashboardActions({ completedCount }: { completedCount: number }) {
  const router = useRouter();
  const [loading, setLoading] = useState(false);

  if (completedCount === 0) return null;

  const clearCompleted = async () => {
    if (
      !confirm(
        `Delete ${completedCount} completed/failed project(s) and all their shorts?`
      )
    ) {
      return;
    }
    setLoading(true);
    try {
      await api.deleteCompletedJobs();
      router.refresh();
    } catch (e) {
      alert(e instanceof Error ? e.message : "Delete failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <button
      type="button"
      onClick={clearCompleted}
      disabled={loading}
      className="inline-flex items-center gap-2 rounded-lg border border-white/10 px-4 py-2.5 text-sm text-zinc-300 hover:border-red-500/40 hover:text-red-400 disabled:opacity-50"
    >
      <Trash2 className="h-4 w-4" />
      {loading ? "Clearing..." : "Clear completed"}
    </button>
  );
}

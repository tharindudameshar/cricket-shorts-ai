"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { Trash2 } from "lucide-react";
import { ProgressBar } from "./ProgressBar";
import { api, type Job } from "@/lib/api";

const statusColors: Record<string, string> = {
  pending: "text-amber-400",
  downloading: "text-blue-400",
  analyzing: "text-cyan-400",
  generating: "text-purple-400",
  completed: "text-emerald-400",
  failed: "text-red-400",
};

export function JobCard({ job }: { job: Job }) {
  const router = useRouter();
  const canDelete = ["completed", "failed"].includes(job.status);

  const remove = async (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (!confirm(`Delete "${job.title}" and all its shorts?`)) return;
    try {
      await api.deleteJob(job.id);
      router.refresh();
    } catch (err) {
      alert(err instanceof Error ? err.message : "Delete failed");
    }
  };

  return (
    <div className="relative rounded-xl border border-white/10 bg-[#14141c] transition hover:border-emerald-500/40 hover:bg-[#18182a]">
      {canDelete && (
        <button
          type="button"
          onClick={remove}
          title="Delete project"
          className="absolute right-3 top-3 z-10 rounded-lg p-1.5 text-zinc-500 hover:bg-red-500/10 hover:text-red-400"
        >
          <Trash2 className="h-4 w-4" />
        </button>
      )}
      <Link href={`/jobs/${job.id}`} className="block p-5">
        <div className="flex items-start justify-between gap-3 pr-8">
          <div>
            <h3 className="font-medium text-white line-clamp-1">{job.title}</h3>
            <p className="mt-1 text-xs text-zinc-500">
              {new Date(job.created_at).toLocaleString()}
            </p>
          </div>
          <span
            className={`shrink-0 text-xs font-medium uppercase ${statusColors[job.status] || "text-zinc-400"}`}
          >
            {job.status}
          </span>
        </div>
        {job.status !== "completed" && job.status !== "failed" && (
          <div className="mt-4">
            <ProgressBar value={job.progress} label={job.status_message} />
          </div>
        )}
        <div className="mt-4 flex gap-4 text-sm text-zinc-400">
          <span>{job.highlight_count} highlights</span>
          <span>{job.short_count} shorts</span>
        </div>
      </Link>
    </div>
  );
}

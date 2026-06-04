import Link from "next/link";
import { ProgressBar } from "./ProgressBar";
import type { Job } from "@/lib/api";

const statusColors: Record<string, string> = {
  pending: "text-amber-400",
  downloading: "text-blue-400",
  analyzing: "text-cyan-400",
  generating: "text-purple-400",
  completed: "text-emerald-400",
  failed: "text-red-400",
};

export function JobCard({ job }: { job: Job }) {
  return (
    <Link
      href={`/jobs/${job.id}`}
      className="block rounded-xl border border-white/10 bg-[#14141c] p-5 transition hover:border-emerald-500/40 hover:bg-[#18182a]"
    >
      <div className="flex items-start justify-between gap-3">
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
  );
}

import Link from "next/link";
import { notFound } from "next/navigation";
import { ProgressBar } from "@/components/ProgressBar";
import { ShortCard } from "@/components/ShortCard";
import { Timeline } from "@/components/Timeline";
import { JobPoller } from "./JobPoller";
import { api } from "@/lib/api";

export const dynamic = "force-dynamic";

export default async function JobPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  let job: Awaited<ReturnType<typeof api.getJob>>;
  let highlights: Awaited<ReturnType<typeof api.getHighlights>> = [];
  let shorts: Awaited<ReturnType<typeof api.getShorts>> = [];

  try {
    job = await api.getJob(id);
    if (job.status === "completed" || job.status === "failed") {
      highlights = await api.getHighlights(id);
      shorts = await api.getShorts(id);
    }
  } catch {
    notFound();
  }

  const isActive = !["completed", "failed"].includes(job.status);

  return (
    <div>
      <Link href="/" className="text-sm text-zinc-500 hover:text-zinc-300">
        ← Dashboard
      </Link>
      <h1 className="mt-4 text-3xl font-bold text-white">{job.title}</h1>
      <p className="mt-2 capitalize text-zinc-400">
        {job.status} · {job.source}
        {job.league && ` · ${job.league.toUpperCase()}`}
      </p>

      {isActive && (
        <div className="mt-6">
          <JobPoller jobId={id} initial={job} />
        </div>
      )}

      {job.error_message && (
        <p className="mt-4 rounded-lg bg-red-500/10 px-4 py-2 text-red-400">
          {job.error_message}
        </p>
      )}

      {highlights.length > 0 && (
        <div className="mt-10">
          <Timeline
            highlights={highlights}
            duration={job.duration_seconds ?? undefined}
          />
        </div>
      )}

      {shorts.length > 0 && (
        <section className="mt-10">
          <h2 className="mb-4 text-xl font-medium text-white">
            Generated shorts ({shorts.length})
          </h2>
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {shorts.map((s) => (
              <ShortCard key={s.id} short={s} />
            ))}
          </div>
        </section>
      )}

      {job.status === "completed" && shorts.length === 0 && (
        <p className="mt-8 text-zinc-500">No shorts generated for this job.</p>
      )}
    </div>
  );
}

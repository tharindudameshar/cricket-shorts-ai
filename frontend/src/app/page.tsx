import Link from "next/link";
import { ArrowRight, Sparkles } from "lucide-react";
import { JobCard } from "@/components/JobCard";
import { DashboardActions } from "@/components/DashboardActions";
import { api } from "@/lib/api";

export const dynamic = "force-dynamic";

export default async function DashboardPage() {
  let jobs: Awaited<ReturnType<typeof api.listJobs>> = [];
  try {
    jobs = await api.listJobs();
  } catch {
    jobs = [];
  }

  const processing = jobs.filter(
    (j) => !["completed", "failed"].includes(j.status)
  );
  const completed = jobs.filter((j) => j.status === "completed");

  return (
    <div>
      <header className="mb-8 flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-white">
            Dashboard
          </h1>
          <p className="mt-2 text-zinc-400">
            AI turns full matches into viral-ready vertical shorts.
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-3">
          <DashboardActions
            completedCount={
              jobs.filter((j) => j.status === "completed" || j.status === "failed")
                .length
            }
          />
          <Link
            href="/upload"
            className="inline-flex items-center gap-2 rounded-lg bg-gradient-to-r from-emerald-600 to-cyan-600 px-5 py-2.5 text-sm font-medium text-white"
          >
            New project
            <ArrowRight className="h-4 w-4" />
          </Link>
        </div>
      </header>

      <section className="mb-10 grid gap-4 sm:grid-cols-3">
        {[
          {
            label: "Active jobs",
            value: processing.length,
            sub: "Analyzing or generating",
          },
          {
            label: "Completed",
            value: completed.length,
            sub: "Ready to export",
          },
          {
            label: "Total shorts",
            value: jobs.reduce((a, j) => a + j.short_count, 0),
            sub: "Across all matches",
          },
        ].map((stat) => (
          <div
            key={stat.label}
            className="rounded-xl border border-white/10 bg-[#14141c] p-5"
          >
            <p className="text-sm text-zinc-500">{stat.label}</p>
            <p className="mt-1 text-3xl font-semibold text-white">
              {stat.value}
            </p>
            <p className="mt-1 text-xs text-zinc-500">{stat.sub}</p>
          </div>
        ))}
      </section>

      <div className="mb-6 flex items-center gap-2">
        <Sparkles className="h-5 w-5 text-emerald-400" />
        <h2 className="text-lg font-medium text-white">Recent projects</h2>
      </div>

      {jobs.length === 0 ? (
        <div className="rounded-xl border border-dashed border-white/15 p-12 text-center">
          <p className="text-zinc-400">No projects yet.</p>
          <Link
            href="/upload"
            className="mt-4 inline-block text-emerald-400 hover:underline"
          >
            Upload your first match →
          </Link>
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {jobs.map((job) => (
            <JobCard key={job.id} job={job} />
          ))}
        </div>
      )}
    </div>
  );
}

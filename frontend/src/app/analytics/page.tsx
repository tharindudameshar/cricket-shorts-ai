import { api } from "@/lib/api";

export const dynamic = "force-dynamic";

export default async function AnalyticsPage() {
  let data: Awaited<ReturnType<typeof api.getAnalytics>> | null = null;
  try {
    data = await api.getAnalytics();
  } catch {
    data = null;
  }

  if (!data) {
    return (
      <div>
        <h1 className="text-3xl font-bold text-white">Analytics</h1>
        <p className="mt-4 text-zinc-500">
          Start the API server to view analytics.
        </p>
      </div>
    );
  }

  return (
    <div>
      <h1 className="text-3xl font-bold text-white">Analytics</h1>
      <p className="mt-2 text-zinc-400">
        Performance insights across your cricket content pipeline.
      </p>

      <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {[
          { label: "Total jobs", value: data.total_jobs },
          { label: "Completed", value: data.completed_jobs },
          { label: "Highlights detected", value: data.total_highlights },
          { label: "Shorts generated", value: data.total_shorts },
        ].map((s) => (
          <div
            key={s.label}
            className="rounded-xl border border-white/10 bg-[#14141c] p-5"
          >
            <p className="text-sm text-zinc-500">{s.label}</p>
            <p className="mt-2 text-2xl font-semibold text-white">{s.value}</p>
          </div>
        ))}
      </div>

      <div className="mt-8 grid gap-6 lg:grid-cols-2">
        <div className="rounded-xl border border-white/10 bg-[#14141c] p-6">
          <h2 className="text-lg font-medium text-white">Viral performance</h2>
          <p className="mt-4 text-4xl font-bold text-emerald-400">
            {data.avg_viral_score.toFixed(1)}
          </p>
          <p className="text-sm text-zinc-500">Average viral score</p>
          <p className="mt-6 text-sm text-zinc-400">
            Estimated editing time saved:{" "}
            <span className="text-white">
              {data.processing_hours_saved} hours
            </span>
          </p>
        </div>
        <div className="rounded-xl border border-white/10 bg-[#14141c] p-6">
          <h2 className="text-lg font-medium text-white">Top moment types</h2>
          <ul className="mt-4 space-y-2">
            {data.top_highlight_types.map((t) => (
              <li
                key={t.type}
                className="flex justify-between text-sm text-zinc-300"
              >
                <span className="capitalize">{t.type.replace(/_/g, " ")}</span>
                <span className="text-zinc-500">{t.count}</span>
              </li>
            ))}
            {data.top_highlight_types.length === 0 && (
              <li className="text-zinc-500">No data yet</li>
            )}
          </ul>
        </div>
      </div>
    </div>
  );
}

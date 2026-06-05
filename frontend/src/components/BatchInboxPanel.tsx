"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { FolderOpen, Loader2, RefreshCw, ScanLine } from "lucide-react";
import { api, type BatchFolderResult, type BatchFolderStatus } from "@/lib/api";

export function BatchInboxPanel() {
  const [status, setStatus] = useState<BatchFolderStatus | null>(null);
  const [league, setLeague] = useState("ipl");
  const [loading, setLoading] = useState(false);
  const [scanning, setScanning] = useState(false);
  const [lastScan, setLastScan] = useState<BatchFolderResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      setStatus(await api.batchFolderStatus());
    } catch (e) {
      setError(e instanceof Error ? e.message : "Could not load inbox status");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
    const t = setInterval(refresh, 5000);
    return () => clearInterval(t);
  }, [refresh]);

  const scanNow = async () => {
    setScanning(true);
    setError(null);
    try {
      const result = await api.batchFolderScan(league);
      setLastScan(result);
      await refresh();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Scan failed");
    } finally {
      setScanning(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="rounded-2xl border border-white/10 bg-[#14141c] p-6">
        <div className="flex items-start gap-4">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-emerald-500/15">
            <FolderOpen className="h-6 w-6 text-emerald-400" />
          </div>
          <div className="flex-1">
            <h2 className="text-lg font-medium text-white">Batch inbox folder</h2>
            <p className="mt-1 text-sm text-zinc-400">
              Drop match videos into the inbox folder. Each file becomes a job
              that generates ~15 vertical shorts. The worker auto-scans every
              few seconds when running.
            </p>
            {status && (
              <code className="mt-3 block rounded-lg bg-black/50 px-3 py-2 text-sm text-emerald-300">
                {status.inbox_path}
              </code>
            )}
          </div>
        </div>

        <div className="mt-6 grid gap-4 sm:grid-cols-3">
          {[
            { label: "Waiting", value: status?.pending_count ?? "—" },
            { label: "Processed", value: status?.processed_count ?? "—" },
            { label: "Failed", value: status?.failed_count ?? "—" },
          ].map((s) => (
            <div key={s.label} className="rounded-lg bg-white/5 px-4 py-3">
              <p className="text-xs text-zinc-500">{s.label}</p>
              <p className="text-2xl font-semibold text-white">{s.value}</p>
            </div>
          ))}
        </div>

        {status && status.pending_files.length > 0 && (
          <ul className="mt-4 space-y-1 rounded-lg bg-black/30 p-3 text-sm text-zinc-300">
            {status.pending_files.map((f) => (
              <li key={f}>📹 {f}</li>
            ))}
          </ul>
        )}

        <div className="mt-6 flex flex-wrap items-end gap-4">
          <label className="text-sm text-zinc-400">
            Scoreboard
            <select
              value={league}
              onChange={(e) => setLeague(e.target.value)}
              className="mt-1 block rounded-lg border border-white/10 bg-black/40 px-3 py-2 text-white"
            >
              <option value="ipl">IPL</option>
              <option value="icc">ICC</option>
              <option value="generic">Generic</option>
            </select>
          </label>
          <button
            type="button"
            onClick={scanNow}
            disabled={scanning}
            className="inline-flex items-center gap-2 rounded-lg bg-gradient-to-r from-emerald-600 to-cyan-600 px-5 py-2.5 text-sm font-medium text-white disabled:opacity-50"
          >
            {scanning ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <ScanLine className="h-4 w-4" />
            )}
            Scan inbox now
          </button>
          <button
            type="button"
            onClick={refresh}
            disabled={loading}
            className="inline-flex items-center gap-2 rounded-lg border border-white/10 px-4 py-2.5 text-sm text-zinc-300 hover:bg-white/5"
          >
            <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
            Refresh
          </button>
        </div>

        {status && (
          <p className="mt-4 text-xs text-zinc-500">
            Auto-scan: {status.auto_scan_enabled ? "on (via worker)" : "off"}
          </p>
        )}
      </div>

      {lastScan && (
        <div className="rounded-xl border border-emerald-500/30 bg-emerald-500/10 p-4 text-sm text-emerald-100">
          Queued {lastScan.queued} of {lastScan.scanned} video(s).
          {lastScan.jobs.length > 0 && (
            <ul className="mt-2 space-y-1">
              {lastScan.jobs.map((j) => (
                <li key={j.id}>
                  <Link href={`/jobs/${j.id}`} className="underline">
                    {j.title}
                  </Link>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}

      {error && (
        <p className="rounded-lg bg-red-500/10 px-4 py-2 text-sm text-red-400">
          {error}
        </p>
      )}

      <div className="rounded-xl border border-white/10 bg-[#14141c] p-5 text-sm text-zinc-400">
        <p className="font-medium text-zinc-200">Terminal (optional)</p>
        <pre className="mt-2 overflow-x-auto rounded-lg bg-black/50 p-3 text-xs text-zinc-300">
{`cd backend
./run-batch.sh --status
./run-batch.sh --watch   # watch folder continuously`}
        </pre>
      </div>
    </div>
  );
}

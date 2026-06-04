"use client";

import { useCallback, useState } from "react";
import { Film, Link2, Loader2, Upload } from "lucide-react";
import { api } from "@/lib/api";
import { useRouter } from "next/navigation";

export function UploadZone() {
  const router = useRouter();
  const [mode, setMode] = useState<"file" | "youtube">("file");
  const [title, setTitle] = useState("IPL Match Highlights");
  const [league, setLeague] = useState("ipl");
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [dragOver, setDragOver] = useState(false);

  const submitFile = async (file: File) => {
    setLoading(true);
    setError(null);
    try {
      const job = await api.upload(file, title, league || undefined);
      router.push(`/jobs/${job.id}`);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Upload failed");
    } finally {
      setLoading(false);
    }
  };

  const onDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragOver(false);
      const file = e.dataTransfer.files[0];
      if (file) submitFile(file);
    },
    [title, league]
  );

  const submitYoutube = async () => {
    if (!url.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const job = await api.youtube(url, title, league || undefined);
      router.push(`/jobs/${job.id}`);
    } catch (e) {
      setError(e instanceof Error ? e.message : "YouTube import failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex gap-2 rounded-lg bg-white/5 p-1">
        <button
          type="button"
          onClick={() => setMode("file")}
          className={`flex flex-1 items-center justify-center gap-2 rounded-md py-2 text-sm ${
            mode === "file" ? "bg-white/10 text-white" : "text-zinc-400"
          }`}
        >
          <Upload className="h-4 w-4" />
          Upload Video
        </button>
        <button
          type="button"
          onClick={() => setMode("youtube")}
          className={`flex flex-1 items-center justify-center gap-2 rounded-md py-2 text-sm ${
            mode === "youtube" ? "bg-white/10 text-white" : "text-zinc-400"
          }`}
        >
          <Link2 className="h-4 w-4" />
          YouTube URL
        </button>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <label className="block text-sm text-zinc-400">
          Match title
          <input
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="mt-1 w-full rounded-lg border border-white/10 bg-black/40 px-3 py-2 text-white"
          />
        </label>
        <label className="block text-sm text-zinc-400">
          Scoreboard profile
          <select
            value={league}
            onChange={(e) => setLeague(e.target.value)}
            className="mt-1 w-full rounded-lg border border-white/10 bg-black/40 px-3 py-2 text-white"
          >
            <option value="ipl">IPL</option>
            <option value="icc">ICC</option>
            <option value="generic">Generic</option>
          </select>
        </label>
      </div>

      {mode === "file" ? (
        <div
          onDragOver={(e) => {
            e.preventDefault();
            setDragOver(true);
          }}
          onDragLeave={() => setDragOver(false)}
          onDrop={onDrop}
          className={`flex flex-col items-center justify-center rounded-2xl border-2 border-dashed px-8 py-16 transition ${
            dragOver
              ? "border-emerald-400 bg-emerald-500/10"
              : "border-white/15 bg-[#14141c]"
          }`}
        >
          <Film className="mb-4 h-12 w-12 text-zinc-500" />
          <p className="text-center text-zinc-300">
            Drop a cricket match video (20–60 min)
          </p>
          <p className="mt-1 text-sm text-zinc-500">MP4, MOV, MKV up to 2GB</p>
          <label className="mt-6 cursor-pointer rounded-lg bg-gradient-to-r from-emerald-600 to-cyan-600 px-6 py-2.5 text-sm font-medium text-white hover:opacity-90">
            {loading ? (
              <span className="flex items-center gap-2">
                <Loader2 className="h-4 w-4 animate-spin" />
                Uploading...
              </span>
            ) : (
              "Browse files"
            )}
            <input
              type="file"
              accept="video/*"
              className="hidden"
              disabled={loading}
              onChange={(e) => {
                const f = e.target.files?.[0];
                if (f) submitFile(f);
              }}
            />
          </label>
        </div>
      ) : (
        <div className="rounded-2xl border border-white/10 bg-[#14141c] p-8">
          <input
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://youtube.com/watch?v=..."
            className="w-full rounded-lg border border-white/10 bg-black/40 px-4 py-3 text-white placeholder:text-zinc-600"
          />
          <button
            type="button"
            onClick={submitYoutube}
            disabled={loading || !url.trim()}
            className="mt-4 flex w-full items-center justify-center gap-2 rounded-lg bg-gradient-to-r from-emerald-600 to-cyan-600 py-3 text-sm font-medium text-white disabled:opacity-50"
          >
            {loading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Link2 className="h-4 w-4" />
            )}
            Import & Analyze
          </button>
        </div>
      )}

      {error && (
        <p className="rounded-lg bg-red-500/10 px-4 py-2 text-sm text-red-400">
          {error}
        </p>
      )}
    </div>
  );
}

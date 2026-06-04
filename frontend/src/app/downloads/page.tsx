"use client";

import { useEffect, useState } from "react";
import { api, type Short } from "@/lib/api";
import { ShortCard } from "@/components/ShortCard";

const PLATFORMS = [
  { id: "youtube_shorts", label: "YouTube Shorts" },
  { id: "tiktok", label: "TikTok" },
  { id: "instagram_reels", label: "Instagram Reels" },
  { id: "facebook_reels", label: "Facebook Reels" },
];

export default function DownloadsPage() {
  const [shorts, setShorts] = useState<Short[]>([]);
  const [platform, setPlatform] = useState("youtube_shorts");
  const [fps, setFps] = useState(30);
  const [msg, setMsg] = useState<string | null>(null);

  useEffect(() => {
    api.getAllShorts().then(setShorts).catch(() => setShorts([]));
  }, []);

  const applyExport = async () => {
    try {
      const res = await api.exportShorts(platform, fps);
      setMsg(res.message);
    } catch (e) {
      setMsg(e instanceof Error ? e.message : "Export failed");
    }
  };

  return (
    <div>
      <h1 className="text-3xl font-bold text-white">Download Center</h1>
      <p className="mt-2 text-zinc-400">
        Export presets: MP4, 1080×1920, 30 or 60 FPS for each platform.
      </p>

      <div className="mt-8 flex flex-wrap gap-4 rounded-xl border border-white/10 bg-[#14141c] p-6">
        <label className="text-sm text-zinc-400">
          Platform
          <select
            value={platform}
            onChange={(e) => setPlatform(e.target.value)}
            className="mt-1 block rounded-lg border border-white/10 bg-black/40 px-3 py-2 text-white"
          >
            {PLATFORMS.map((p) => (
              <option key={p.id} value={p.id}>
                {p.label}
              </option>
            ))}
          </select>
        </label>
        <label className="text-sm text-zinc-400">
          Frame rate
          <select
            value={fps}
            onChange={(e) => setFps(Number(e.target.value))}
            className="mt-1 block rounded-lg border border-white/10 bg-black/40 px-3 py-2 text-white"
          >
            <option value={30}>30 FPS</option>
            <option value={60}>60 FPS</option>
          </select>
        </label>
        <button
          type="button"
          onClick={applyExport}
          className="self-end rounded-lg bg-emerald-600 px-5 py-2 text-sm font-medium text-white hover:bg-emerald-500"
        >
          Apply export preset
        </button>
      </div>
      {msg && (
        <p className="mt-4 text-sm text-emerald-400">{msg}</p>
      )}

      <div className="mt-8 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {shorts.map((s) => (
          <ShortCard key={s.id} short={s} />
        ))}
      </div>
    </div>
  );
}

import { api, type Short } from "@/lib/api";
import { Download, TrendingUp } from "lucide-react";

export function ShortCard({ short }: { short: Short }) {
  const thumb = short.thumbnail_url
    ? api.fileUrl(short.thumbnail_url)
    : null;
  const download = short.download_url
    ? api.fileUrl(short.download_url)
    : "#";

  return (
    <article className="overflow-hidden rounded-xl border border-white/10 bg-[#14141c]">
      <div className="relative aspect-[9/16] max-h-72 bg-black/60">
        {thumb ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={thumb}
            alt={short.title}
            className="h-full w-full object-cover"
          />
        ) : (
          <div className="flex h-full items-center justify-center text-4xl">
            🏏
          </div>
        )}
        <span className="absolute right-2 top-2 rounded bg-black/70 px-2 py-0.5 text-xs text-emerald-400">
          {short.viral_score.toFixed(0)} viral
        </span>
      </div>
      <div className="p-4">
        <h3 className="font-medium text-white line-clamp-2">{short.title}</h3>
        <p className="mt-1 text-xs text-zinc-500 line-clamp-2">
          {short.hashtags}
        </p>
        <div className="mt-3 flex items-center justify-between text-xs text-zinc-400">
          <span className="flex items-center gap-1">
            <TrendingUp className="h-3 w-3" />
            ~{(short.views_predicted / 1000).toFixed(1)}K views
          </span>
          <span>
            {short.width}×{short.height} · {short.fps}fps
          </span>
        </div>
        <a
          href={download}
          download
          className="mt-3 flex w-full items-center justify-center gap-2 rounded-lg bg-white/10 py-2 text-sm text-white hover:bg-white/15"
        >
          <Download className="h-4 w-4" />
          Download MP4
        </a>
      </div>
    </article>
  );
}

import type { Highlight } from "@/lib/api";

const typeEmoji: Record<string, string> = {
  six: "🚀",
  four: "⚡",
  wicket: "🔥",
  catch: "😱",
  hat_trick: "🎩",
  milestone_50: "🎯",
  milestone_100: "💯",
  drs: "👀",
  last_over: "🤯",
  crowd_reaction: "📣",
};

function formatTime(sec: number) {
  const m = Math.floor(sec / 60);
  const s = Math.floor(sec % 60);
  return `${m}:${s.toString().padStart(2, "0")}`;
}

export function Timeline({
  highlights,
  duration,
}: {
  highlights: Highlight[];
  duration?: number;
}) {
  const max = duration || Math.max(...highlights.map((h) => h.end_time), 1);

  return (
    <div className="rounded-xl border border-white/10 bg-[#14141c] p-5">
      <h3 className="mb-4 text-sm font-medium text-zinc-300">Highlight Timeline</h3>
      <div className="relative h-24 rounded-lg bg-black/50">
        <div className="absolute inset-x-0 bottom-8 h-1 rounded bg-white/10" />
        {highlights.map((h) => {
          const left = (h.start_time / max) * 100;
          const width = Math.max(
            2,
            ((h.end_time - h.start_time) / max) * 100
          );
          return (
            <div
              key={h.id}
              title={`${h.caption} (${formatTime(h.start_time)})`}
              className="absolute bottom-6 h-8 rounded bg-gradient-to-t from-emerald-600/80 to-cyan-500/60 hover:ring-2 hover:ring-white/30"
              style={{ left: `${left}%`, width: `${width}%` }}
            />
          );
        })}
      </div>
      <ul className="mt-4 max-h-64 space-y-2 overflow-y-auto">
        {highlights.map((h) => (
          <li
            key={h.id}
            className="flex items-center justify-between gap-3 rounded-lg bg-white/5 px-3 py-2 text-sm"
          >
            <span className="text-white">
              {typeEmoji[h.highlight_type] || "🏏"} {h.caption}
            </span>
            <span className="shrink-0 text-zinc-500">
              {formatTime(h.start_time)} · {h.viral_score.toFixed(0)} viral
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}

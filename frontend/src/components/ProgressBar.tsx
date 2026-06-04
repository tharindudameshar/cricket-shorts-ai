export function ProgressBar({
  value,
  label,
}: {
  value: number;
  label?: string;
}) {
  return (
    <div className="space-y-1">
      {label && (
        <div className="flex justify-between text-xs text-zinc-400">
          <span>{label}</span>
          <span>{Math.round(value)}%</span>
        </div>
      )}
      <div className="h-2 overflow-hidden rounded-full bg-white/10">
        <div
          className="h-full rounded-full bg-gradient-to-r from-emerald-500 to-cyan-400 transition-all duration-500"
          style={{ width: `${Math.min(100, value)}%` }}
        />
      </div>
    </div>
  );
}

import { ShortCard } from "@/components/ShortCard";
import { api } from "@/lib/api";

export const dynamic = "force-dynamic";

export default async function GalleryPage() {
  let shorts: Awaited<ReturnType<typeof api.getAllShorts>> = [];
  try {
    shorts = await api.getAllShorts();
  } catch {
    shorts = [];
  }

  return (
    <div>
      <h1 className="text-3xl font-bold text-white">Shorts Gallery</h1>
      <p className="mt-2 text-zinc-400">
        All AI-generated vertical shorts, ranked by viral score.
      </p>
      {shorts.length === 0 ? (
        <p className="mt-12 text-center text-zinc-500">
          No shorts yet. Process a match to see results here.
        </p>
      ) : (
        <div className="mt-8 grid gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {shorts.map((s) => (
            <ShortCard key={s.id} short={s} />
          ))}
        </div>
      )}
    </div>
  );
}

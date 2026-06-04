import { UploadZone } from "@/components/UploadZone";

export default function UploadPage() {
  return (
    <div>
      <h1 className="text-3xl font-bold text-white">Upload Match</h1>
      <p className="mt-2 max-w-xl text-zinc-400">
        Upload a 20–60 minute cricket video or paste a YouTube URL. Our AI
        detects sixes, wickets, catches, DRS, milestones, and crowd reactions —
        then generates 10–20 vertical shorts automatically.
      </p>
      <div className="mt-8 max-w-2xl">
        <UploadZone />
      </div>
    </div>
  );
}

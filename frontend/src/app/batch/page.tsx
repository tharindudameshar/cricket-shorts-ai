import { BatchInboxPanel } from "@/components/BatchInboxPanel";

export default function BatchPage() {
  return (
    <div>
      <h1 className="text-3xl font-bold text-white">Batch Folder</h1>
      <p className="mt-2 max-w-2xl text-zinc-400">
        Drop multiple cricket match videos into one folder and generate 15+
        shorts per video automatically.
      </p>
      <div className="mt-8 max-w-3xl">
        <BatchInboxPanel />
      </div>
    </div>
  );
}

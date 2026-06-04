"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api, type Job } from "@/lib/api";
import { ProgressBar } from "@/components/ProgressBar";

export function JobPoller({
  jobId,
  initial,
}: {
  jobId: string;
  initial: Job;
}) {
  const router = useRouter();
  const [job, setJob] = useState(initial);

  useEffect(() => {
    if (["completed", "failed"].includes(job.status)) return;
    const t = setInterval(async () => {
      try {
        const updated = await api.getJob(jobId);
        setJob(updated);
        if (updated.status === "completed" || updated.status === "failed") {
          router.refresh();
        }
      } catch {
        /* ignore */
      }
    }, 2000);
    return () => clearInterval(t);
  }, [jobId, job.status, router]);

  return (
    <ProgressBar value={job.progress} label={job.status_message} />
  );
}

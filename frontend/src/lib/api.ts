const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export type JobStatus =
  | "pending"
  | "downloading"
  | "analyzing"
  | "generating"
  | "completed"
  | "failed";

export interface Job {
  id: string;
  title: string;
  source: string;
  source_url?: string | null;
  status: JobStatus;
  progress: number;
  status_message: string;
  duration_seconds?: number | null;
  league?: string | null;
  error_message?: string | null;
  highlight_count: number;
  short_count: number;
  created_at: string;
  updated_at: string;
}

export interface Highlight {
  id: string;
  job_id: string;
  highlight_type: string;
  title: string;
  caption: string;
  start_time: number;
  end_time: number;
  excitement_score: number;
  viral_score: number;
  rank: number;
  player_name?: string | null;
  team_name?: string | null;
  commentary_snippet?: string | null;
}

export interface Short {
  id: string;
  job_id: string;
  highlight_id?: string | null;
  title: string;
  description: string;
  hashtags: string;
  file_path: string;
  download_url?: string | null;
  thumbnail_url?: string | null;
  duration_seconds: number;
  width: number;
  height: number;
  fps: number;
  platform: string;
  viral_score: number;
  views_predicted: number;
  created_at: string;
}

export interface Analytics {
  total_jobs: number;
  completed_jobs: number;
  total_highlights: number;
  total_shorts: number;
  avg_viral_score: number;
  top_highlight_types: { type: string; count: number }[];
  processing_hours_saved: number;
}

export interface BatchFolderStatus {
  inbox_path: string;
  pending_count: number;
  pending_files: string[];
  processed_count: number;
  failed_count: number;
  auto_scan_enabled: boolean;
}

export interface BatchFolderResult {
  inbox_path: string;
  scanned: number;
  queued: number;
  skipped: number;
  failed: number;
  errors: string[];
  jobs: Job[];
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}/api${path}`, {
    ...init,
    headers: {
      ...(init?.headers || {}),
    },
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || res.statusText);
  }
  return res.json() as Promise<T>;
}

export const api = {
  listJobs: () => request<Job[]>("/jobs"),
  getJob: (id: string) => request<Job>(`/jobs/${id}`),
  getHighlights: (id: string) => request<Highlight[]>(`/jobs/${id}/highlights`),
  getShorts: (id: string) => request<Short[]>(`/jobs/${id}/shorts`),
  getAllShorts: () => request<Short[]>("/shorts"),
  getAnalytics: () => request<Analytics>("/jobs/analytics"),
  upload: async (file: File, title: string, league?: string) => {
    const form = new FormData();
    form.append("file", file);
    const params = new URLSearchParams({ title });
    if (league) params.set("league", league);
    const res = await fetch(`${API_BASE}/api/jobs/upload?${params}`, {
      method: "POST",
      body: form,
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json() as Promise<Job>;
  },
  youtube: (url: string, title?: string, league?: string) =>
    request<Job>("/jobs/youtube", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url, title, league }),
    }),
  batchFolderStatus: () => request<BatchFolderStatus>("/jobs/batch-folder/status"),
  batchFolderScan: (league?: string) =>
    request<BatchFolderResult>("/jobs/batch-folder", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ league }),
    }),
  exportShorts: (platform: string, fps: number, jobId?: string) =>
    request<{ exported: number; message: string }>("/shorts/export", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        platform,
        fps,
        ...(jobId ? {} : {}),
      }),
    }),
  fileUrl: (path: string) => `${API_BASE}${path}`,
  deleteJob: (id: string) =>
    request<{ deleted: boolean }>(`/jobs/${id}`, { method: "DELETE" }),
  deleteCompletedJobs: () =>
    request<{ deleted: number }>("/jobs/completed", { method: "DELETE" }),
};

# Cricket Shorts AI

Automatically convert long cricket match videos (20–60 minutes) into viral-ready vertical shorts using AI-powered highlight detection.

## Features

- Upload local videos or paste YouTube URLs
- AI pipeline: frame extraction, vision (scoreboard/wicket/replay), audio excitement, combined scoring
- Auto-detect: sixes, fours, wickets, run outs, catches, milestones, DRS, crowd reactions, and more
- Generate 15–60s vertical shorts (9:16) with smart crop, slow-mo, transitions
- Auto captions, titles, hashtags, thumbnails, viral score
- Export presets: YouTube Shorts, TikTok, Instagram Reels, Facebook Reels (1080×1920, 30/60 FPS)
- Dashboard: upload, processing status, timeline, gallery, downloads, analytics

## Stack

| Layer | Tech |
|-------|------|
| Frontend | Next.js 15, React, TypeScript, Tailwind CSS |
| Backend | Python FastAPI |
| AI | OpenCV, YOLOv11, Whisper, FFmpeg, PyTorch |
| DB | PostgreSQL |
| Storage | AWS S3 (local filesystem fallback) |

## Quick Start

### One terminal (easiest)

```bash
cd ~/Projects/cricket-shorts-ai
./run.sh
```

Opens **http://localhost:3000** (API + worker + frontend). Press **Ctrl+C** to stop everything.

### Prerequisites

- Node.js 20+
- Python 3.11+
- FFmpeg (`brew install ffmpeg`)
- PostgreSQL (Homebrew or Docker)

### 1. Environment

```bash
cp .env.example .env
# Edit DATABASE_URL, AWS keys, optional OPENAI_API_KEY for titles
```

### 2. Database

**Option A — Homebrew (no Docker)** — you already have PostgreSQL 16:

```bash
# Start Postgres (if not running)
brew services start postgresql@16

# One-time: create app user + database
psql -h localhost -d postgres <<'SQL'
CREATE ROLE cricket WITH LOGIN PASSWORD 'cricket' CREATEDB;
CREATE DATABASE cricket_shorts OWNER cricket;
SQL
```

Default `DATABASE_URL` in `.env.example` matches this setup:

`postgresql+asyncpg://cricket:cricket@localhost:5432/cricket_shorts`

**Option B — Docker** (requires [Docker Desktop](https://www.docker.com/products/docker-desktop/)):

```bash
docker compose up -d postgres
```

### 3. Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

In another terminal, start the worker:

```bash
cd backend
./run-worker.sh
```

If you use **conda** `(base)` alongside `.venv`, `python` may point at the wrong interpreter (missing packages). Always use `.venv/bin/python` or the helper scripts above—not bare `python`.

### 4. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000). API docs: [http://localhost:8000/docs](http://localhost:8000/docs).

## Batch folder processing

Process many match videos at once — **~15 shorts per video**.

### How it works

1. Drop `.mp4`, `.mov`, `.mkv` files into the inbox folder (default: `storage/inbox/`)
2. The **worker** auto-scans the inbox every ~10 seconds and queues each video
3. Processed originals move to `storage/inbox/processed/`; failures go to `storage/inbox/failed/`
4. Shorts appear in **Gallery** and **Download Center** when each job completes

### UI

Open **Batch Folder** in the app, or trigger a scan manually.

### CLI

```bash
cd backend
./run-batch.sh --status              # pending / processed counts
./run-batch.sh                       # one-time scan
./run-batch.sh --watch               # watch folder continuously
./run-batch.sh --folder /path/to/videos --league ipl
```

### API

```bash
curl http://localhost:8000/api/jobs/batch-folder/status
curl -X POST http://localhost:8000/api/jobs/batch-folder \
  -H "Content-Type: application/json" \
  -d '{"league":"ipl"}'
```

Ensure `./run-worker.sh` is running — it processes queued jobs and auto-scans the inbox.

## Demo Mode

Set `AI_DEMO_MODE=true` in `.env` to run without GPU/YOLO/Whisper weights. The pipeline simulates realistic highlights for UI testing.

## Project Structure

```
cricket-shorts-ai/
├── backend/          # FastAPI + AI pipeline
├── frontend/         # Next.js dashboard
├── docker-compose.yml
└── .env.example
```

## License

MIT

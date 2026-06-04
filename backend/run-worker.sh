#!/usr/bin/env bash
# Use the project venv explicitly (avoids conda/system python hijacking `python`).
set -euo pipefail
cd "$(dirname "$0")"
exec .venv/bin/python -m app.workers.processor

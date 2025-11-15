#!/bin/bash
set -euo pipefail

: "${PORT:=8000}"
: "${SCRAPER_HEADLESS:=0}"

exec xvfb-run -a --server-args="-screen 0 1920x1080x24" \
  uvicorn app.main:app --host 0.0.0.0 --port "${PORT}"

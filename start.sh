#!/usr/bin/env bash
set -euo pipefail

if [ "${VERCEL:-}" = "1" ]; then
    echo "Running on Vercel"
    pip install -r requirements.txt
    exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}" --log-level info
else
    echo "Running locally"
    if [ ! -d ".venv" ]; then
        python3 -m venv .venv
        ./.venv/bin/pip install -r requirements.txt
    fi
    exec ./.venv/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
fi

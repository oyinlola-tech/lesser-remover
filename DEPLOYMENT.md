# Deployment

One codebase, two targets. Storage, logging, and capability gating switch
based on environment variables.

## Local

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
./start.sh          # serves http://127.0.0.1:8000
```

Requirements:

- Python 3.10+
- Ghostscript (`gs`) for PDF compression and PDF→image tools
- Free disk space for `storage/` (uploads, jobs, downloads are cleaned by
  the job TTL sweeper)

Production-like local run (no reload):

```bash
.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-level info
```

## Vercel

The repo is wired for Vercel serverless (Python):

- `vercel.json` builds `api/index.py` and routes `/(.*)` to it; FastAPI
  serves pages, static assets, and API routes through the same handler.
- `api/index.py` wraps the app with `Mangum`.

### Setup

1. Import the repo into Vercel (root = repository root).
2. Create a **Vercel Blob** store and copy its read-write token.
3. Set environment variables:
   - `STORAGE_DRIVER=vercel`
   - `BLOB_READ_WRITE_TOKEN=<token>`
   - `CORS_ORIGINS=https://<your-domain>.vercel.app`
   - `APP_ENV=production`, `DEBUG=false`
4. Deploy.

### What changes on Vercel

| Concern | Behavior |
|---|---|
| Storage | all files go to Vercel Blob via the `vercel` storage driver |
| Logs | file logging disabled; everything streams to stdout (Vercel dashboard) |
| Ghostscript tools | unavailable — `pdf-compressor` and `pdf-to-image` report `unavailable` via `/api/v1/capabilities` and their pages show the disabled state |
| Background remover | works; the rembg model is fetched on first request |
| Temp files | `TEMP_DIRECTORY` / `XDG_CACHE_HOME` point under `/tmp` (serverless) |

The capabilities endpoint is the source of truth: the frontend never hardcodes
which tools exist, so the same pages work in both environments.

### Blob notes

- `BLOB_READ_WRITE_TOKEN` is read at import time; a missing token raises a
  startup error on Vercel (the local driver remains usable without it).
- Download URLs are time-limited via the blob SDK's signed URLs.

## Troubleshooting

- **Startup error `BLOB_READ_WRITE_TOKEN is required`** — running with
  `STORAGE_DRIVER=vercel` outside Vercel, or the env var is unset on the
  platform.
- **`gs --version` not found** — install Ghostscript; the two `gs` tools
  will otherwise be flagged unavailable (capabilities), so pages degrade
  cleanly instead of crashing.
- **Model download slow on first background-removal request** — cold start
  on Vercel; subsequent calls are fast.

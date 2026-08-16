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
   - `BLOB_ACCESS_MODE=public` (or `private`, matching the store)
   - `CORS_ORIGINS=https://<your-domain>.vercel.app`
   - `APP_ENV=production`, `DEBUG=false`
4. Deploy.

### What changes on Vercel

| Concern | Behavior |
|---|---|
| Storage | all files go to Vercel Blob via the `vercel` storage driver |
| Logs | file logging disabled; everything streams to stdout (Vercel dashboard) |
| Ghostscript tools | unavailable — `pdf-compressor` and `pdf-to-image` report `unavailable` via `/api/v1/capabilities` and their pages show the disabled state |
| Background tools | unavailable on the current build — `rembg` was trimmed from `api/requirements.txt` to fit the 500 MB function limit, so `background-remover` and `background-replacement` report `unavailable` and their pages show the disabled state |
| Temp files | `TEMP_DIRECTORY` / `XDG_CACHE_HOME` point under `/tmp` (serverless) |

The capabilities endpoint is the source of truth: the frontend never hardcodes
which tools exist, so the same pages work in both environments.

### Blob notes

- Storage goes through the official Vercel Python SDK (`vercel.blob`,
  pinned in `api/requirements.txt`), which handles API versioning headers,
  retries for transient failures and signed URLs.
- `BLOB_READ_WRITE_TOKEN` is read at import time; a missing token raises a
  startup error on Vercel (the local driver remains usable without it).
- `BLOB_ACCESS_MODE` must match the store's access mode (`public` or
  `private`). Private stores return time-limited signed download URLs.

## Troubleshooting

- **Startup error `BLOB_READ_WRITE_TOKEN is required`** — running with
  `STORAGE_DRIVER=vercel` outside Vercel, or the env var is unset on the
  platform.
- **`gs --version` not found** — install Ghostscript; the two `gs` tools
  will otherwise be flagged unavailable (capabilities), so pages degrade
  cleanly instead of crashing.
- **Background removal unavailable on Vercel** — `rembg` (with its
  ONNX runtime and models) is excluded from `api/requirements.txt` to stay
  under the 500 MB serverless function limit, so the two background tools
  are reported unavailable and their pages show the disabled state. They
  work fully in local mode.

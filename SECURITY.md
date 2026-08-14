# Security Notes

## Upload validation pipeline

Every upload passes `app/shared/file_inspection/` before any processing:

1. **Magic-byte detection** — the file type is decided by inspecting the
   file's actual bytes, never the filename extension or the browser-provided
   MIME type.
2. **Pillow verification** — images are opened, `verify()`d, and `load()`d;
   truncated or malformed images are rejected.
3. **Decompression-bomb protection** — `Image.MAX_IMAGE_PIXELS = 50_000_000`
   caps pixel dimensions before decode.
4. **Size limits** — enforced per-route (images 25 MB, PDFs 50 MB, and the
   global `MAX_UPLOAD_SIZE_MB`), applied before any processing work.

## Filenames

- Uploaded filenames are sanitized (`Path` traversal, control characters,
  and unsafe separators removed) before they are used for storage keys or
  download URLs.
- Download routes serve files only through generated URLs scoped to stored
  names; the `/download/{filename}` endpoints validate that the name resolves
  inside the owning directory.

## Secrets

- `BLOB_READ_WRITE_TOKEN` is consumed server-side only; it is never included
  in API responses, capabilities, or frontend assets (regression-tested in
  `test_api.py`).
- `vercel.json` pins `MODEL_CHECKSUM_DISABLED=1` and keeps the token out of
  the repo; the token lives in Vercel project env vars.

## Storage

- Local mode: files live under `storage/` with the server process as the
  only writer; jobs expire after `JOB_TTL_MINUTES` (default 30) and are
  swept by the startup cleanup job.
- Vercel mode: Blob URLs are signed and time-limited.

## Error handling

- Internal exceptions are mapped to a unified error envelope with a
  `request_id`; tracebacks, absolute paths, and environment values are
  never leaked to clients (regression-tested).

## Logging

- Local logs split by area (`system`, `activities`, `background_remover`,
  `compression`) under `logs/`; production streams to stdout. No file
  contents are ever logged.

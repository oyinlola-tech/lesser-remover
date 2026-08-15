"""Request ID and rate-limit middleware.

Every request receives a short random ID that is attached to log
records and returned in the ``X-Request-ID`` header, so errors can be
traced without leaking internals.

The rate limiter protects the API from being overwhelmed by bursts of
requests, returning a designed 429 page for browsers and the standard
error envelope for API clients.
"""

import logging
import time
import uuid
from collections import deque

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.api import API_PREFIX
from app.core.config import settings
from app.core.exceptions import _error_page_response

logger = logging.getLogger(__name__)

_RATE_LIMIT_BUCKETS: dict[str, deque[float]] = {}


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID")
        if not request_id or len(request_id) > 64:
            request_id = uuid.uuid4().hex[:16]
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """In-memory sliding-window limiter for API requests.

    One window per client IP. Limits are best-effort on serverless
    runtimes (state is per instance) but are enough to absorb accidental
    bursts and abusive loops.
    """

    async def dispatch(self, request: Request, call_next):
        if not request.url.path.startswith(API_PREFIX):
            return await call_next(request)
        if settings.app_env != "production":
            return await call_next(request)

        client = self._client_key(request)
        now = time.monotonic()
        window = float(settings.rate_limit_window_seconds)
        limit = settings.rate_limit_max_requests

        bucket = _RATE_LIMIT_BUCKETS.setdefault(client, deque())
        while bucket and now - bucket[0] > window:
            bucket.popleft()

        if len(bucket) >= limit:
            response = _error_page_response(
                request,
                429,
                "RATE_LIMITED",
                "Too many requests. Please try again in a moment.",
            )
            response.headers["Retry-After"] = str(int(window))
            return response

        bucket.append(now)
        return await call_next(request)

    @staticmethod
    def _client_key(request: Request) -> str:
        forwarded = request.headers.get("x-forwarded-for", "")
        if forwarded:
            return forwarded.split(",")[0].strip()
        host = request.client.host if request.client else "unknown"
        return host

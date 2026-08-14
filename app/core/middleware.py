"""Request ID middleware.

Every request receives a short random ID that is attached to
log records and returned in the ``X-Request-ID`` header, so errors
can be traced without leaking internals.
"""

import logging
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

logger = logging.getLogger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID")
        if not request_id or len(request_id) > 64:
            request_id = uuid.uuid4().hex[:16]
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response

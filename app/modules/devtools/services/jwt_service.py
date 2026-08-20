"""JWT decoding for the jwt-decoder tool."""

import base64
import json
import time

from app.core.logging import get_tool_logger


class JwtService:
    """Decode a JWT token into header and payload."""

    def jwt_decode(self, token: str) -> dict:
        tool_logger = get_tool_logger("jwt-decoder")
        started = time.monotonic()

        parts = token.strip().split(".")
        if len(parts) < 2:
            raise ValueError(
                "Invalid JWT token structure (must contain at least 2 segments)."
            )

        try:
            header = _b64decode(parts[0])
            payload = _b64decode(parts[1])
            tool_logger.info(
                "decoded jwt (%d segments) in %.2fs",
                len(parts),
                time.monotonic() - started,
            )
            return {
                "header": header,
                "payload": payload,
                "signature_present": len(parts) >= 3 and bool(parts[2]),
            }
        except Exception as err:
            raise ValueError(f"Failed to decode JWT token: {err}")


def _b64decode(s: str) -> dict:
    padded = s + "=" * (-len(s) % 4)
    decoded_bytes = base64.urlsafe_b64decode(padded)
    return json.loads(decoded_bytes.decode("utf-8"))


jwt_service = JwtService()

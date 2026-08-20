"""SVG minification for the svg-optimizer tool."""

import re
import time
from xml.etree import ElementTree

from app.core.logging import get_tool_logger


class SvgOptimizerService:
    """Minify an SVG while keeping it structurally valid."""

    def optimize_svg(
        self,
        svg_data: bytes,
        precision: int = 2,
    ) -> dict:
        """Minify an SVG while keeping it structurally valid.

        Uses safe text-level transforms (comment strip, whitespace
        collapse, numeric rounding) and verifies the result still
        parses as XML before returning it.
        """
        tool_logger = get_tool_logger("svg-optimizer")
        started = time.monotonic()
        text = svg_data.decode("utf-8")

        try:
            ElementTree.fromstring(svg_data)
        except ElementTree.ParseError as error:
            raise ValueError(f"Invalid SVG file: {error}") from error

        minified = self._minify(text, precision)
        try:
            ElementTree.fromstring(minified.encode("utf-8"))
        except ElementTree.ParseError as error:
            raise ValueError(
                f"Minification produced invalid SVG: {error}"
            ) from error

        minified_bytes = minified.encode("utf-8")
        tool_logger.info(
            "optimized svg %d -> %d bytes (%.1f%%) in %.2fs",
            len(svg_data),
            len(minified_bytes),
            100 * (1 - len(minified_bytes) / max(1, len(svg_data))),
            time.monotonic() - started,
        )
        return {
            "data": minified_bytes,
            "original_size": len(svg_data),
            "minified_size": len(minified_bytes),
        }

    @staticmethod
    def _minify(raw: str, precision: int | None) -> str:
        cleaned = re.sub(r"<!--.*?-->", "", raw, flags=re.DOTALL)
        cleaned = re.sub(r">\s+<", "><", cleaned)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        cleaned = cleaned.replace(" />", "/>")
        if precision is not None and precision >= 0:
            cleaned = re.sub(
                r"(?<![\w#])(-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?)",
                lambda m: SvgOptimizerService._round(m, precision),
                cleaned,
            )
        return cleaned

    @staticmethod
    def _round(match: re.Match, precision: int) -> str:
        try:
            value = float(match.group(0))
        except ValueError:
            return match.group(0)
        if value == int(value):
            return str(int(value))
        return format(value, f".{precision}f").rstrip("0").rstrip(".")


svg_optimizer_service = SvgOptimizerService()

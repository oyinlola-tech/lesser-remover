from io import BytesIO
from typing import Iterable, Optional, Tuple
from PIL import Image

from app.infrastructure.compression.pillow_adapter import pillow_adapter
from app.infrastructure.compression.ghostscript_adapter import (
    ghostscript_adapter,
)


class CompressionEngine:
    IMAGE_QUALITY_PRESETS = {
        "best": 95,
        "balanced": 85,
        "smallest": 70,
    }

    PDF_PRESETS = ["screen", "ebook", "printer", "prepress"]

    def _resize_preserve_aspect(self, image: Image.Image, max_dimensions: Tuple[int, int]) -> Image.Image:
        max_w, max_h = max_dimensions
        w, h = image.size
        if w <= max_w and h <= max_h:
            return image.copy()
        ratio = min(max_w / w, max_h / h)
        new_size = (int(w * ratio), int(h * ratio))
        return image.resize(new_size, Image.LANCZOS)

    def _remove_metadata(self, image: Image.Image) -> Image.Image:
        # Create a new image object with same pixel data but without info/metadata
        new_img = Image.new(image.mode, image.size)
        new_img.paste(image)
        return new_img

    def _encode_image(self, image: Image.Image, output_format: str, quality: int) -> bytes:
        fmt = output_format.lower()
        if fmt == "webp":
            return pillow_adapter.encode_webp(image, quality=quality)
        if fmt == "jpeg" or fmt == "jpg":
            return pillow_adapter.encode_jpeg(image, quality=quality)
        if fmt == "png":
            return pillow_adapter.encode_png(image)
        raise ValueError(f"Unsupported output format: {output_format}")

    def compress_image(
        self,
        file_data: bytes,
        output_format: str = "webp",
        quality: Optional[int] = None,
        target_size_bytes: Optional[int] = None,
        max_dimensions: Optional[Tuple[int, int]] = None,
        try_remove_metadata: bool = True,
    ) -> Tuple[bytes, str, int]:
        image = Image.open(BytesIO(file_data))
        image.load()

        candidates = []

        dimension_variants = [image]
        if max_dimensions:
            resized = self._resize_preserve_aspect(image, max_dimensions)
            if resized.size != image.size:
                dimension_variants.append(resized)

        metadata_variants = [False, True] if try_remove_metadata else [False]

        # If target_size provided, use binary search per variant to find highest quality <= target
        if target_size_bytes is not None:
            for img_variant in dimension_variants:
                for remove_meta in metadata_variants:
                    working_img = self._remove_metadata(img_variant) if remove_meta else img_variant
                    # binary search for quality
                    low, high = 20, 100
                    best_data = None
                    best_q = 0
                    while low <= high:
                        q = (low + high) // 2
                        data = self._encode_image(working_img, output_format, q)
                        if len(data) <= target_size_bytes:
                            best_data = data
                            best_q = q
                            low = q + 1
                        else:
                            high = q - 1
                    if best_data is None:
                        # fallback to lowest quality
                        data = self._encode_image(working_img, output_format, 20)
                        candidates.append((data, remove_meta, 20, working_img.size))
                    else:
                        candidates.append((best_data, remove_meta, best_q, working_img.size))
            # pick candidate with size closest to target (largest <= target)
            best = None
            for data, rm, q, dims in candidates:
                if len(data) <= target_size_bytes:
                    if best is None or len(data) > len(best[0]):
                        best = (data, rm, q, dims)
            if best is None:
                # choose smallest produced
                best = min(candidates, key=lambda c: len(c[0]))
            data, rm, q, dims = best
            content_type = "image/webp" if output_format.lower() == "webp" else (
                "image/jpeg" if output_format.lower() in ("jpeg", "jpg") else "image/png"
            )
            return data, content_type, q

        # No target size: try presets and pick smallest result
        qualities = [quality] if quality is not None else list(self.IMAGE_QUALITY_PRESETS.values())
        for img_variant in dimension_variants:
            for remove_meta in metadata_variants:
                working_img = self._remove_metadata(img_variant) if remove_meta else img_variant
                for q in qualities:
                    # skip None
                    if q is None:
                        continue
                    data = self._encode_image(working_img, output_format, q)
                    candidates.append((data, remove_meta, q, working_img.size))

        # pick smallest file size; tie-breaker: higher quality
        best = min(candidates, key=lambda c: (len(c[0]), -c[2]))
        data, rm, q, dims = best
        content_type = "image/webp" if output_format.lower() == "webp" else (
            "image/jpeg" if output_format.lower() in ("jpeg", "jpg") else "image/png"
        )
        return data, content_type, q


compression_engine = CompressionEngine()

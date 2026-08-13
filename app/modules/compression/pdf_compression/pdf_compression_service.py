from app.infrastructure.compression.ghostscript_adapter import (
    ghostscript_adapter,
)


class PdfCompressionService:

    def compress(
        self,
        file_data: bytes,
        quality: str = "ebook",
    ) -> bytes:
        return ghostscript_adapter.compress(
            file_data=file_data,
            quality=quality,
        )

    def compress_best(
        self,
        file_data: bytes,
        preset: str = "balanced",
    ) -> tuple[bytes, str]:

        quality_order = {
            "smallest": (
                "screen",
                "ebook",
                "printer",
            ),

            "balanced": (
                "ebook",
                "screen",
                "printer",
            ),

            "best_quality": (
                "printer",
                "prepress",
                "ebook",
            ),
        }

        qualities = quality_order.get(
            preset
        )

        if not qualities:
            raise ValueError(
                "Unsupported PDF preset."
            )

        candidates = []

        original_size = len(file_data)

        for quality in qualities:

            try:

                data = (
                    ghostscript_adapter
                    .compress(
                        file_data=file_data,
                        quality=quality,
                    )
                )

                candidates.append(
                    (
                        quality,
                        data,
                    )
                )

            except RuntimeError:
                continue

        if not candidates:
            raise RuntimeError(
                "Unable to compress PDF."
            )

        # pick smallest; if none are smaller than original, keep original
        quality, data = min(
            candidates,
            key=lambda item: len(item[1]),
        )

        if len(data) >= original_size:
            return file_data, "original"

        return data, quality


pdf_compression_service = PdfCompressionService()

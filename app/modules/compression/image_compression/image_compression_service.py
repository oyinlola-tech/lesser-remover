from io import BytesIO

from PIL import Image

from app.modules.compression.image_compression.image_compression_settings import (
    PRESETS,
)
from app.infrastructure.compression.pillow_adapter import (
    pillow_adapter,
)


class ImageCompressionService:

    def _prepare_image(
        self,
        file_data: bytes,
        max_dimension: int | None = None,
    ) -> Image.Image:

        image = Image.open(
            BytesIO(file_data)
        )

        image.load()

        if max_dimension:
            image.thumbnail(
                (
                    max_dimension,
                    max_dimension,
                ),
                Image.Resampling.LANCZOS,
            )

        return image

    def _encode(
        self,
        image: Image.Image,
        output_format: str,
        quality: int,
    ) -> tuple[bytes, str]:

        output_format = (
            output_format.lower()
        )

        if output_format == "webp":
            return (
                pillow_adapter.encode_webp(
                    image,
                    quality=quality,
                ),
                "image/webp",
            )

        if output_format == "jpeg":
            return (
                pillow_adapter.encode_jpeg(
                    image,
                    quality=quality,
                ),
                "image/jpeg",
            )

        if output_format == "png":
            return (
                pillow_adapter.encode_png(
                    image
                ),
                "image/png",
            )

        raise ValueError(
            f"Unsupported output format: "
            f"{output_format}"
        )

    def compress(
        self,
        file_data: bytes,
        output_format: str = "webp",
        quality: int = 85,
        max_dimension: int | None = None,
    ) -> tuple[bytes, str, int, int]:

        image = self._prepare_image(
            file_data,
            max_dimension,
        )

        data, content_type = self._encode(
            image,
            output_format,
            quality,
        )

        return data, content_type, image.width, image.height

    def _compress_with_preset_details(
        self,
        file_data: bytes,
        preset: str = "balanced",
        output_format: str = "webp",
        max_dimension: int | None = None,
    ) -> tuple[bytes, str, int, int, int]:

        settings = PRESETS.get(
            preset
        )

        if not settings:
            raise ValueError(
                f"Unsupported compression preset: "
                f"{preset}"
            )

        image = self._prepare_image(
            file_data,
            max_dimension,
        )

        best_data: bytes | None = None
        best_content_type = ""
        best_quality = 0

        for quality in settings.qualities:

            data, content_type = (
                self._encode(
                    image,
                    output_format,
                    quality,
                )
            )

            if (
                best_data is None
                or len(data)
                < len(best_data)
            ):
                best_data = data
                best_content_type = (
                    content_type
                )
                best_quality = quality

        if best_data is None:
            raise RuntimeError(
                "Unable to compress image."
            )

        return (
            best_data,
            best_content_type,
            best_quality,
            image.width,
            image.height,
        )

    def compress_with_preset(
        self,
        file_data: bytes,
        preset: str = "balanced",
        output_format: str = "webp",
        max_dimension: int | None = None,
    ) -> tuple[bytes, str, int, int, int]:

        best_data, best_content_type, best_quality, width, height = (
            self._compress_with_preset_details(
                file_data=file_data,
                preset=preset,
                output_format=output_format,
                max_dimension=max_dimension,
            )
        )

        return (
            best_data,
            best_content_type,
            best_quality,
            width,
            height,
        )

    def _compress_to_target_details(
        self,
        file_data: bytes,
        target_size_bytes: int,
        output_format: str = "webp",
        max_dimension: int | None = None,
    ) -> tuple[bytes, str, int, int, int]:

        if output_format == "png":
            raise ValueError(
                "Target size compression "
                "requires a lossy-capable "
                "format such as WebP or JPEG."
            )

        image = self._prepare_image(
            file_data,
            max_dimension,
        )

        low = 20
        high = 100

        best_data: bytes | None = None
        best_content_type = ""
        best_quality = 0

        while low <= high:

            quality = (
                low + high
            ) // 2

            data, content_type = (
                self._encode(
                    image,
                    output_format,
                    quality,
                )
            )

            if len(data) <= target_size_bytes:

                best_data = data
                best_content_type = (
                    content_type
                )
                best_quality = quality

                low = quality + 1

            else:

                high = quality - 1

        if best_data is None:

            data, content_type = (
                self._encode(
                    image,
                    output_format,
                    20,
                )
            )

            return (
                data,
                content_type,
                20,
                image.width,
                image.height,
            )

        return (
            best_data,
            best_content_type,
            best_quality,
            image.width,
            image.height,
        )

    def compress_to_target(
        self,
        file_data: bytes,
        target_size_bytes: int,
        output_format: str = "webp",
        max_dimension: int | None = None,
    ) -> tuple[bytes, str, int, int, int]:

        best_data, best_content_type, best_quality, width, height = (
            self._compress_to_target_details(
                file_data=file_data,
                target_size_bytes=target_size_bytes,
                output_format=output_format,
                max_dimension=max_dimension,
            )
        )

        return (
            best_data,
            best_content_type,
            best_quality,
            width,
            height,
        )


image_compression_service = (
    ImageCompressionService()
)

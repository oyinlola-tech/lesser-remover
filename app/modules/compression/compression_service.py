from app.modules.compression.image_compression.image_compression_service import (
    image_compression_service,
)
from app.modules.compression.pdf_compression.pdf_compression_service import (
    pdf_compression_service,
)


class CompressionService:

    def compress_image(
        self,
        file_data: bytes,
        preset: str = "balanced",
        output_format: str = "webp",
        target_size_bytes: int | None = None,
        max_dimension: int | None = None,
    ) -> tuple[bytes, str, int, int, int]:

        if target_size_bytes is not None:

            return (
                image_compression_service
                .compress_to_target(
                    file_data=file_data,
                    target_size_bytes=target_size_bytes,
                    output_format=output_format,
                    max_dimension=max_dimension,
                )
            )

        return (
            image_compression_service
            .compress_with_preset(
                file_data=file_data,
                preset=preset,
                output_format=output_format,
                max_dimension=max_dimension,
            )
        )

    def compress_pdf(
        self,
        file_data: bytes,
        preset: str = "balanced",
    ) -> tuple[bytes, str, str]:

        data, quality = (
            pdf_compression_service.compress_best(
                file_data=file_data,
                preset=preset,
            )
        )

        return (
            data,
            "application/pdf",
            quality,
        )


compression_service = CompressionService()

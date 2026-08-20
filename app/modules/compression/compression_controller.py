"""Facade over the single and batch compression controllers."""

from app.modules.compression.controllers.batch_compression_controller import (
    batch_compression_controller,
)
from app.modules.compression.controllers.single_compression_controller import (
    single_compression_controller,
)


class CompressionController:

    async def compress_file(
        self,
        file,
        output_format: str = "webp",
        compression_preset: str = "balanced",
        target_size_kb: int | None = None,
        max_dimension: int | None = None,
    ):
        return await single_compression_controller.compress_file(
            file=file,
            output_format=output_format,
            compression_preset=compression_preset,
            target_size_kb=target_size_kb,
            max_dimension=max_dimension,
        )

    async def compress_batch(
        self,
        files,
        image_output_format: str = "webp",
        compression_preset: str = "balanced",
        max_dimension: int | None = None,
    ):
        return await batch_compression_controller.compress_batch(
            files=files,
            image_output_format=image_output_format,
            compression_preset=compression_preset,
            max_dimension=max_dimension,
        )


compression_controller = CompressionController()

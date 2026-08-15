from io import BytesIO

from PIL import Image, ImageFilter


def _get_rembg_adapter():
    from app.infrastructure.image.rembg_adapter import rembg_adapter
    return rembg_adapter


class BackgroundService:
    def remove_background(
        self,
        file_data: bytes,
        original_filename: str,
    ) -> tuple[Image.Image, int, int]:
        image = Image.open(
            BytesIO(file_data),
        )
        image.load()
        width, height = image.size
        processed_image = (
            _get_rembg_adapter().remove_background(
                image,
            )
        )
        return (
            processed_image,
            width,
            height,
        )

    def replace_background(
        self,
        file_data: bytes,
        color: str | None = None,
        image_data: bytes | None = None,
        blur: int = 0,
    ) -> tuple[Image.Image, int, int]:
        """Remove the subject's background and place it on a solid
        color, an uploaded image, or a blurred copy of itself.
        """
        source = Image.open(BytesIO(file_data))
        source.load()
        width, height = source.size
        subject = _get_rembg_adapter().remove_background(source)

        if image_data is not None:
            try:
                background = Image.open(BytesIO(image_data))
                background.load()
            except Exception as error:
                raise ValueError(
                    "The uploaded background image is not valid."
                ) from error
            background = background.convert("RGBA")
            if background.size != subject.size:
                background = background.resize(
                    subject.size,
                    Image.Resampling.LANCZOS,
                )
            if blur > 0:
                background = background.filter(
                    ImageFilter.GaussianBlur(blur)
                )
        elif color is not None:
            background = Image.new(
                "RGBA",
                subject.size,
                color,
            )
        else:
            blurred = source.convert("RGBA")
            background = blurred.filter(
                ImageFilter.GaussianBlur(blur or 20)
            )

        return (
            Image.alpha_composite(background, subject),
            width,
            height,
        )


background_service = BackgroundService()

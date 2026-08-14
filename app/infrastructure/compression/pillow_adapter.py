from io import BytesIO
from PIL import Image


class PillowAdapter:
    def encode_png(
        self,
        image: Image.Image,
    ) -> bytes:
        output = BytesIO()
        try:
            image.save(
                output,
                format="PNG",
                optimize=True,
            )
            return output.getvalue()
        finally:
            output.close()

    def encode_webp(
        self,
        image: Image.Image,
        quality: int = 95,
    ) -> bytes:
        output = BytesIO()
        try:
            image.save(
                output,
                format="WEBP",
                quality=quality,
                method=6,
            )
            return output.getvalue()
        finally:
            output.close()

    def encode_jpeg(
        self,
        image: Image.Image,
        quality: int = 95,
    ) -> bytes:
        if image.mode in ("RGBA", "LA", "P"):
            background = Image.new(
                "RGB",
                image.size,
                "white",
            )
            if image.mode == "P":
                image = image.convert("RGBA")
            background.paste(
                image,
                mask=image.getchannel("A"),
            )
            image = background
        elif image.mode != "RGB":
            image = image.convert("RGB")
        output = BytesIO()
        try:
            image.save(
                output,
                format="JPEG",
                quality=quality,
                optimize=True,
                progressive=True,
            )
            return output.getvalue()
        finally:
            output.close()

    def encode_avif(
        self,
        image: Image.Image,
        quality: int = 85,
    ) -> bytes:
        if image.mode not in ("RGBA", "RGB", "LA"):
            image = image.convert("RGBA")
        output = BytesIO()
        try:
            image.save(
                output,
                format="AVIF",
                quality=quality,
            )
            return output.getvalue()
        finally:
            output.close()

    def encode(
        self,
        image: Image.Image,
        output_format: str,
        quality: int = 92,
    ) -> tuple[bytes, str]:
        output_format = output_format.lower()
        if output_format in {"jpg", "jpeg"}:
            return (
                self.encode_jpeg(image, quality=quality),
                "image/jpeg",
            )
        if output_format == "png":
            return self.encode_png(image), "image/png"
        if output_format == "webp":
            return (
                self.encode_webp(image, quality=quality),
                "image/webp",
            )
        if output_format == "avif":
            return (
                self.encode_avif(image, quality=quality),
                "image/avif",
            )
        raise ValueError(f"Unsupported output format: {output_format}")


pillow_adapter = PillowAdapter()

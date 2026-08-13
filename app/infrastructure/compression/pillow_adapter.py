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


pillow_adapter = PillowAdapter()

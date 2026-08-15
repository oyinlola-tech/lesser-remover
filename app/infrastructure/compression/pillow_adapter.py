from io import BytesIO

from PIL import Image
from PIL.PngImagePlugin import PngInfo


class PillowAdapter:
    def _filter_metadata(
        self,
        image: Image.Image,
        strip: bool,
    ) -> dict:
        """Return save-kwargs for metadata.

        When ``strip`` is True, no EXIF/ICC/text chunks are embedded so the
        resulting file carries only pixel data.  When False, the common
        metadata keys are preserved when present.
        """
        if not strip:
            kwargs: dict = {}
            if image.info.get("exif"):
                kwargs["exif"] = image.info["exif"]
            if image.info.get("icc_profile"):
                kwargs["icc_profile"] = image.info["icc_profile"]
            png_info = PngInfo()
            preserved = False
            if image.info.get("pnginfo"):
                png_info = image.info["pnginfo"]
                preserved = True
            for key, value in image.info.items():
                if key in ("exif", "icc_profile", "pnginfo"):
                    continue
                if isinstance(value, (str, bytes)):
                    png_info.add_text(
                        key,
                        value if isinstance(value, str) else value.decode(
                            "utf-8",
                            errors="replace",
                        ),
                    )
                    preserved = True
            if preserved:
                kwargs["pnginfo"] = png_info
            return kwargs
        return {}

    def encode_png(
        self,
        image: Image.Image,
        strip_metadata: bool = True,
    ) -> bytes:
        output = BytesIO()
        try:
            save_kwargs = self._filter_metadata(
                image,
                strip=strip_metadata,
            )
            image.save(
                output,
                format="PNG",
                optimize=True,
                **save_kwargs,
            )
            return output.getvalue()
        finally:
            output.close()

    def encode_webp(
        self,
        image: Image.Image,
        quality: int = 95,
        strip_metadata: bool = True,
    ) -> bytes:
        output = BytesIO()
        try:
            save_kwargs = self._filter_metadata(
                image,
                strip=strip_metadata,
            )
            image.save(
                output,
                format="WEBP",
                quality=quality,
                method=6,
                **save_kwargs,
            )
            return output.getvalue()
        finally:
            output.close()

    def encode_jpeg(
        self,
        image: Image.Image,
        quality: int = 95,
        strip_metadata: bool = True,
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
            save_kwargs = self._filter_metadata(
                image,
                strip=strip_metadata,
            )
            image.save(
                output,
                format="JPEG",
                quality=quality,
                optimize=True,
                progressive=True,
                **save_kwargs,
            )
            return output.getvalue()
        finally:
            output.close()

    def encode_avif(
        self,
        image: Image.Image,
        quality: int = 85,
        strip_metadata: bool = True,
    ) -> bytes:
        if image.mode not in ("RGBA", "RGB", "LA"):
            image = image.convert("RGBA")
        output = BytesIO()
        try:
            save_kwargs = self._filter_metadata(
                image,
                strip=strip_metadata,
            )
            image.save(
                output,
                format="AVIF",
                quality=quality,
                **save_kwargs,
            )
            return output.getvalue()
        finally:
            output.close()

    def encode(
        self,
        image: Image.Image,
        output_format: str,
        quality: int = 92,
        strip_metadata: bool = True,
    ) -> tuple[bytes, str]:
        output_format = output_format.lower()
        if output_format in {"jpg", "jpeg"}:
            return (
                self.encode_jpeg(
                    image,
                    quality=quality,
                    strip_metadata=strip_metadata,
                ),
                "image/jpeg",
            )
        if output_format == "png":
            return (
                self.encode_png(
                    image,
                    strip_metadata=strip_metadata,
                ),
                "image/png",
            )
        if output_format == "webp":
            return (
                self.encode_webp(
                    image,
                    quality=quality,
                    strip_metadata=strip_metadata,
                ),
                "image/webp",
            )
        if output_format == "avif":
            return (
                self.encode_avif(
                    image,
                    quality=quality,
                    strip_metadata=strip_metadata,
                ),
                "image/avif",
            )
        raise ValueError(f"Unsupported output format: {output_format}")


pillow_adapter = PillowAdapter()

from io import BytesIO

from PIL import Image
from rembg import remove


class RemBGAdapter:
    def remove_background(self, image: Image.Image) -> Image.Image:
        output = remove(image)
        if isinstance(output, Image.Image):
            return output
        buffer = BytesIO(output)
        try:
            loaded = Image.open(buffer)
            loaded.load()
            return loaded
        finally:
            buffer.close()

    def remove_background_to_png(
        self,
        image: Image.Image,
    ) -> bytes:
        result = self.remove_background(image)
        output = BytesIO()
        try:
            result.save(
                output,
                format="PNG",
            )
            return output.getvalue()
        finally:
            output.close()


rembg_adapter = RemBGAdapter()
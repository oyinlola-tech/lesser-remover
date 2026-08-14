import os
from io import BytesIO
from pathlib import Path

from PIL import Image
from rembg import new_session, remove

from app.core.config import settings

MODELS_DIR = Path(__file__).resolve().parents[3] / "models"


class RemBGAdapter:
    def __init__(self) -> None:
        self._session = None

    def _get_session(self):
        if self._session is None:
            if (MODELS_DIR / f"{settings.rembg_model}.onnx").exists():
                os.environ["U2NET_HOME"] = str(MODELS_DIR)
            self._session = new_session(settings.rembg_model)
        return self._session

    def remove_background(self, image: Image.Image) -> Image.Image:
        output = remove(image, session=self._get_session())
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
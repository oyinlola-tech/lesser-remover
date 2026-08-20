"""HTTP-facing logic for the palette-extractor tool."""

from fastapi import HTTPException, UploadFile

from app.modules.image.controllers.image_controller_helpers import read_image
from app.modules.image.services.palette_service import palette_extractor_service


class PaletteController:
    """Extract a dominant color palette from an image."""

    async def extract_palette(
        self,
        file: UploadFile,
        num_colors: int = 6,
    ) -> dict:
        file_data, filename = await read_image(file)
        try:
            colors = palette_extractor_service.extract_palette(
                file_data,
                num_colors=num_colors,
            )
            return {"success": True, "filename": filename, "colors": colors}
        except ValueError as err:
            raise HTTPException(status_code=400, detail=str(err)) from err


palette_controller = PaletteController()

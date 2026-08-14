from fastapi import HTTPException, UploadFile

from app.modules.devtools.dev_tools_service import (
    dev_tools_service,
)


class DevToolsController:
    async def _read_upload(
        self,
        file: UploadFile | None,
        field: str,
    ) -> bytes | None:
        if file is None:
            return None
        file_data = await file.read()
        if not file_data:
            raise HTTPException(
                status_code=400,
                detail=f"Uploaded file is empty: {field}",
            )
        return file_data

    async def favicon(
        self,
        image: UploadFile,
        size: int = 64,
        add_padding: bool = False,
    ) -> dict:
        image_data = await self._read_upload(image, "image")
        try:
            result = dev_tools_service.generate_favicon(
                image_data,
                size=size,
                add_padding=add_padding,
            )
        except (OSError, ValueError) as error:
            raise HTTPException(
                status_code=400,
                detail=f"Unable to generate favicon: {error}",
            ) from error
        return {
            "success": True,
            "sizes": result["sizes"],
            "ico": result["ico"],
            "png": result["png"],
        }

    async def optimize_svg(
        self,
        file: UploadFile,
        precision: int = 2,
    ) -> dict:
        svg_data = await self._read_upload(file, "svg")
        try:
            result = dev_tools_service.optimize_svg(
                svg_data,
                precision=precision,
            )
        except (OSError, ValueError) as error:
            raise HTTPException(
                status_code=400,
                detail=f"Unable to optimize SVG: {error}",
            ) from error
        return {
            "success": True,
            "data": result["data"],
            "original_size": result["original_size"],
            "minified_size": result["minified_size"],
            "saved_percent": round(
                (1 - result["minified_size"] / max(1, result["original_size"]))
                * 100,
                1,
            ),
        }

    async def qr(
        self,
        content: str,
        box_size: int = 10,
        border: int = 4,
        fill_color: str = "#163300",
        back_color: str = "#ffffff",
        output_format: str = "png",
        logo: UploadFile | None = None,
    ) -> tuple[bytes, str]:
        logo_data = await self._read_upload(logo, "logo")
        try:
            data, content_type = dev_tools_service.generate_qr(
                content,
                box_size=box_size,
                border=border,
                fill_color=fill_color,
                back_color=back_color,
                output_format=output_format,
                image_data=logo_data,
            )
        except (OSError, ValueError) as error:
            raise HTTPException(
                status_code=400,
                detail=f"Unable to generate QR code: {error}",
            ) from error
        return data, content_type

    async def barcode(
        self,
        content: str,
        code_type: str = "code128",
        output_format: str = "png",
    ) -> tuple[bytes, str]:
        try:
            data, content_type = dev_tools_service.generate_barcode(
                content,
                code_type=code_type,
                output_format=output_format,
            )
        except (OSError, ValueError) as error:
            raise HTTPException(
                status_code=400,
                detail=f"Unable to generate barcode: {error}",
            ) from error
        return data, content_type


dev_tools_controller = DevToolsController()

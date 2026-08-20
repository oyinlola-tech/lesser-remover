"""HTTP-facing logic for the devtools tools."""

from fastapi import HTTPException, UploadFile

from app.modules.devtools.controllers.devtools_controller_helpers import (
    as_http_error,
    read_upload,
)
from app.modules.devtools.services.barcode_service import barcode_service
from app.modules.devtools.services.favicon_service import favicon_service
from app.modules.devtools.services.json_service import json_service
from app.modules.devtools.services.jwt_service import jwt_service
from app.modules.devtools.services.qr_service import qr_service
from app.modules.devtools.services.svg_generator_service import svg_generator_service
from app.modules.devtools.services.svg_optimizer_service import svg_optimizer_service


class FaviconController:
    async def favicon(
        self,
        image: UploadFile,
        size: int = 64,
        add_padding: bool = False,
    ) -> dict:
        image_data = await read_upload(image, "image")
        try:
            result = favicon_service.generate_favicon(
                image_data,
                size=size,
                add_padding=add_padding,
            )
        except (OSError, ValueError) as error:
            raise as_http_error("Unable to generate favicon", error) from error
        return {
            "success": True,
            "sizes": result["sizes"],
            "ico": result["ico"],
            "png": result["png"],
        }


class SvgController:
    async def optimize_svg(self, file: UploadFile, precision: int = 2) -> dict:
        svg_data = await read_upload(file, "svg")
        try:
            result = svg_optimizer_service.optimize_svg(
                svg_data,
                precision=precision,
            )
        except (OSError, ValueError) as error:
            raise as_http_error("Unable to optimize SVG", error) from error
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

    async def svg(
        self,
        image: UploadFile,
        threshold: int = 128,
        background_color: str = "white",
        foreground_color: str = "black",
    ) -> tuple[bytes, str]:
        image_data = await read_upload(image, "image")
        try:
            svg_text = svg_generator_service.generate_svg(
                image_data,
                threshold=threshold,
                background_color=background_color,
                foreground_color=foreground_color,
            )
        except (OSError, ValueError, RuntimeError) as error:
            raise as_http_error("Unable to generate SVG", error) from error
        return svg_text.encode("utf-8"), "image/svg+xml"


class QrController:
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
        logo_data = await read_upload(logo, "logo")
        try:
            return qr_service.generate_qr(
                content,
                box_size=box_size,
                border=border,
                fill_color=fill_color,
                back_color=back_color,
                output_format=output_format,
                image_data=logo_data,
            )
        except (OSError, ValueError) as error:
            raise as_http_error("Unable to generate QR code", error) from error


class BarcodeController:
    async def barcode(
        self,
        content: str,
        code_type: str = "code128",
        output_format: str = "png",
    ) -> tuple[bytes, str]:
        try:
            return barcode_service.generate_barcode(
                content,
                code_type=code_type,
                output_format=output_format,
            )
        except (OSError, ValueError) as error:
            raise as_http_error("Unable to generate barcode", error) from error


class JsonController:
    def json_to_csv(self, json_text: str) -> dict:
        try:
            return {"success": True, "csv": json_service.json_to_csv(json_text)}
        except ValueError as err:
            raise HTTPException(status_code=400, detail=str(err))

    def csv_to_json(self, csv_text: str) -> dict:
        try:
            return {"success": True, "json": json_service.csv_to_json(csv_text)}
        except ValueError as err:
            raise HTTPException(status_code=400, detail=str(err))

    def json_format(self, json_text: str, minify: bool = False) -> dict:
        try:
            result = json_service.json_format(json_text, minify=minify)
            return {"success": True, "result": result}
        except ValueError as err:
            raise HTTPException(status_code=400, detail=str(err))


class JwtController:
    def jwt_decode(self, token: str) -> dict:
        try:
            return {"success": True, "data": jwt_service.jwt_decode(token)}
        except ValueError as err:
            raise HTTPException(status_code=400, detail=str(err))

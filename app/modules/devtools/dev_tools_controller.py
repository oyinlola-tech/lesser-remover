"""Facade over the per-tool devtools controllers."""

from fastapi import UploadFile

from app.modules.devtools.controllers import (
    barcode_controller,
    favicon_controller,
    json_controller,
    jwt_controller,
    qr_controller,
    svg_controller,
)


class DevToolsController:
    """Delegates devtool operations to their per-tool controllers."""

    async def favicon(self, image: UploadFile, *args, **kwargs) -> dict:
        return await favicon_controller.favicon(image, *args, **kwargs)

    async def optimize_svg(self, file: UploadFile, *args, **kwargs) -> dict:
        return await svg_controller.optimize_svg(file, *args, **kwargs)

    async def svg(self, image: UploadFile, *args, **kwargs) -> tuple[bytes, str]:
        return await svg_controller.svg(image, *args, **kwargs)

    async def qr(self, content: str, *args, **kwargs) -> tuple[bytes, str]:
        return await qr_controller.qr(content, *args, **kwargs)

    async def barcode(self, content: str, *args, **kwargs) -> tuple[bytes, str]:
        return await barcode_controller.barcode(content, *args, **kwargs)

    def json_to_csv(self, json_text: str) -> dict:
        return json_controller.json_to_csv(json_text)

    def csv_to_json(self, csv_text: str) -> dict:
        return json_controller.csv_to_json(csv_text)

    def json_format(self, json_text: str, minify: bool = False) -> dict:
        return json_controller.json_format(json_text, minify=minify)

    def jwt_decode(self, token: str) -> dict:
        return jwt_controller.jwt_decode(token)


dev_tools_controller = DevToolsController()

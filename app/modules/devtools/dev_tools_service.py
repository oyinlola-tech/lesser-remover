"""Facade over the per-tool devtools services."""

from app.modules.devtools.services import (
    barcode_service,
    favicon_service,
    json_service,
    jwt_service,
    qr_service,
    svg_generator_service,
    svg_optimizer_service,
)


class DevToolsService:
    """Delegates devtool operations to their per-tool services."""

    def generate_favicon(self, *args, **kwargs) -> dict:
        return favicon_service.generate_favicon(*args, **kwargs)

    def optimize_svg(self, *args, **kwargs) -> dict:
        return svg_optimizer_service.optimize_svg(*args, **kwargs)

    def generate_svg(self, *args, **kwargs) -> str:
        return svg_generator_service.generate_svg(*args, **kwargs)

    def generate_qr(self, *args, **kwargs) -> tuple[bytes, str]:
        return qr_service.generate_qr(*args, **kwargs)

    def generate_barcode(self, *args, **kwargs) -> tuple[bytes, str]:
        return barcode_service.generate_barcode(*args, **kwargs)

    def json_to_csv(self, json_text: str) -> str:
        return json_service.json_to_csv(json_text)

    def csv_to_json(self, csv_text: str) -> str:
        return json_service.csv_to_json(csv_text)

    def json_format(self, json_text: str, minify: bool = False) -> str:
        return json_service.json_format(json_text, minify=minify)

    def jwt_decode(self, token: str) -> dict:
        return jwt_service.jwt_decode(token)


dev_tools_service = DevToolsService()

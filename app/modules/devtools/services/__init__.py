"""Devtools service package.

Each devtool gets its own service class; the module-level
``dev_tools_service`` facade delegates so controllers and tests keep a
single entry point.
"""

from app.modules.devtools.services.barcode_service import barcode_service
from app.modules.devtools.services.favicon_service import favicon_service
from app.modules.devtools.services.json_service import json_service
from app.modules.devtools.services.jwt_service import jwt_service
from app.modules.devtools.services.qr_service import qr_service
from app.modules.devtools.services.svg_generator_service import svg_generator_service
from app.modules.devtools.services.svg_optimizer_service import svg_optimizer_service

__all__ = [
    "barcode_service",
    "favicon_service",
    "json_service",
    "jwt_service",
    "qr_service",
    "svg_generator_service",
    "svg_optimizer_service",
]

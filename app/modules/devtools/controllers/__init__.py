"""Devtools controller package.

Each devtool gets its own controller; :data:`DevToolsController` in
``app.modules.devtools.dev_tools_controller`` composes them.
"""

from app.modules.devtools.controllers.barcode_controller import barcode_controller
from app.modules.devtools.controllers.favicon_controller import favicon_controller
from app.modules.devtools.controllers.json_controller import json_controller
from app.modules.devtools.controllers.jwt_controller import jwt_controller
from app.modules.devtools.controllers.qr_controller import qr_controller
from app.modules.devtools.controllers.svg_controller import svg_controller

__all__ = [
    "barcode_controller",
    "favicon_controller",
    "json_controller",
    "jwt_controller",
    "qr_controller",
    "svg_controller",
]

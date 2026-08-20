"""Devtools route package.

Each devtool exposes its own sub-router; the module-level ``router`` in
``app.modules.devtools.dev_tools_route`` composes them.
"""

from app.modules.devtools.routes.data_routes import data_router
from app.modules.devtools.routes.favicon_route import favicon_router
from app.modules.devtools.routes.image_gen_routes import image_gen_router
from app.modules.devtools.routes.svg_routes import svg_router

__all__ = ["data_router", "favicon_router", "image_gen_router", "svg_router"]

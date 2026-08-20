"""Facade over the background controllers."""

from app.modules.background.controllers.remove_background_controller import (
    remove_background_controller,
)
from app.modules.background.controllers.replace_background_controller import (
    replace_background_controller,
)


class BackgroundController:

    async def remove_background(self, file, output_format="webp"):
        return await remove_background_controller.remove_background(
            file,
            output_format,
        )

    async def replace_background(
        self,
        file,
        color=None,
        background_image=None,
        blur=0,
        output_format="png",
    ):
        return await replace_background_controller.replace_background(
            file,
            color,
            background_image,
            blur,
            output_format,
        )


background_controller = BackgroundController()

"""Routes for the qr-generator and barcode-generator tools."""

import logging

from fastapi import APIRouter, File, Form, Response, UploadFile

from app.modules.devtools.dev_tools_controller import dev_tools_controller

logger = logging.getLogger(__name__)

image_gen_router = APIRouter(tags=["Developer Tools"])


@image_gen_router.post("/qr")
async def generate_qr(
    content: str = Form(...),
    box_size: int = Form(10),
    border: int = Form(4),
    fill_color: str = Form("#163300"),
    back_color: str = Form("#ffffff"),
    output_format: str = Form("png"),
    logo: UploadFile | None = File(None),
):
    logger.info(
        "generate_qr: content_len=%d format=%s has_logo=%s",
        len(content), output_format, bool(logo),
    )
    data, content_type = await dev_tools_controller.qr(
        content,
        box_size=box_size,
        border=border,
        fill_color=fill_color,
        back_color=back_color,
        output_format=output_format,
        logo=logo,
    )
    return Response(content=data, media_type=content_type)


@image_gen_router.post("/barcode")
async def generate_barcode(
    content: str = Form(...),
    code_type: str = Form("code128"),
    output_format: str = Form("png"),
):
    logger.info(
        "generate_barcode: content_len=%d type=%s format=%s",
        len(content), code_type, output_format,
    )
    data, content_type = await dev_tools_controller.barcode(
        content,
        code_type=code_type,
        output_format=output_format,
    )
    return Response(content=data, media_type=content_type)

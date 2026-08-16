import logging

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import Response

from app.api import API_PREFIX
from app.core.capabilities import capability_registry
from app.modules.devtools.dev_tools_controller import (
    dev_tools_controller,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix=f"{API_PREFIX}/tools/dev",
    tags=["Developer Tools"],
)


def _check_svg_capability() -> None:
    if not capability_registry.is_available("svg-generator"):
        raise HTTPException(
            status_code=503,
            detail="SVG generation is unavailable in the current environment.",
        )


@router.post("/favicon")
async def generate_favicon(
    image: UploadFile = File(...),
    size: int = Form(64),
    add_padding: bool = Form(False),
):
    logger.info("generate_favicon: image=%s size=%d padding=%s", image.filename, size, add_padding)
    result = await dev_tools_controller.favicon(
        image,
        size=size,
        add_padding=add_padding,
    )
    from io import BytesIO
    from zipfile import ZIP_DEFLATED, ZipFile

    archive_buffer = BytesIO()
    with ZipFile(
        archive_buffer,
        mode="w",
        compression=ZIP_DEFLATED,
        compresslevel=9,
    ) as archive:
        for item, data in [
            ("favicon.ico", result["ico"]),
            (f"favicon-{result['sizes'][-1]}x{result['sizes'][-1]}.png", result["png"]),
        ]:
            archive.writestr(item, data)
    headers = {"Content-Disposition": "attachment; filename=favicon-set.zip"}
    return Response(
        content=archive_buffer.getvalue(),
        media_type="application/zip",
        headers=headers,
    )


@router.post("/svg-optimize")
async def optimize_svg(
    file: UploadFile = File(...),
):
    logger.info("optimize_svg: file=%s", file.filename)
    result = await dev_tools_controller.optimize_svg(file)
    headers = {"Content-Disposition": "attachment; filename=optimized.svg"}
    return Response(
        content=result["data"],
        media_type="image/svg+xml",
        headers=headers,
    )


@router.post("/svg-generate")
async def generate_svg(
    image: UploadFile = File(...),
    threshold: int = Form(128),
    background_color: str = Form("white"),
    foreground_color: str = Form("black"),
):
    _check_svg_capability()
    logger.info("generate_svg: image=%s threshold=%d", image.filename, threshold)
    data, content_type = await dev_tools_controller.svg(
        image,
        threshold=threshold,
        background_color=background_color,
        foreground_color=foreground_color,
    )
    headers = {"Content-Disposition": "attachment; filename=converted.svg"}
    return Response(
        content=data,
        media_type=content_type,
        headers=headers,
    )


@router.post("/qr")
async def generate_qr(
    content: str = Form(...),
    box_size: int = Form(10),
    border: int = Form(4),
    fill_color: str = Form("#163300"),
    back_color: str = Form("#ffffff"),
    output_format: str = Form("png"),
    logo: UploadFile | None = File(None),
):
    logger.info("generate_qr: content_len=%d format=%s has_logo=%s", len(content), output_format, bool(logo))
    data, content_type = await dev_tools_controller.qr(
        content,
        box_size=box_size,
        border=border,
        fill_color=fill_color,
        back_color=back_color,
        output_format=output_format,
        logo=logo,
    )
    media_type = content_type if content_type != "image/svg+xml" else "image/svg+xml"
    return Response(
        content=data,
        media_type=media_type,
    )


@router.post("/barcode")
async def generate_barcode(
    content: str = Form(...),
    code_type: str = Form("code128"),
    output_format: str = Form("png"),
):
    logger.info("generate_barcode: content_len=%d type=%s format=%s", len(content), code_type, output_format)
    data, content_type = await dev_tools_controller.barcode(
        content,
        code_type=code_type,
        output_format=output_format,
    )
    return Response(
        content=data,
        media_type=content_type,
    )

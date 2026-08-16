import logging

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse

from app.api import API_PREFIX
from app.core.capabilities import capability_registry
from app.modules.pdf.pdf_controller import pdf_controller
from app.modules.pdf.pdf_repository import pdf_repository
from app.modules.pdf.pdf_schema import (
    PdfImagesResponse,
    PdfInfoResponse,
    PdfToolResponse,
)
from app.shared.utils.file_util import is_safe_filename

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix=f"{API_PREFIX}/tools/pdf",
    tags=["PDF Tools"],
)


def _check_pdf_to_image_capability() -> None:
    if not capability_registry.is_available("pdf-to-image"):
        raise HTTPException(
            status_code=503,
            detail="PDF to image conversion is unavailable in the current environment.",
        )


@router.post("/merge", response_model=PdfToolResponse)
async def merge_pdfs(
    files: list[UploadFile] = File(...),
):
    logger.info("merge_pdfs: files=%d", len(files))
    return await pdf_controller.merge(files)


@router.post("/split", response_model=PdfToolResponse)
async def split_pdf(
    file: UploadFile = File(...),
):
    logger.info("split_pdf: file=%s", file.filename)
    return await pdf_controller.split(file)


@router.post("/rotate", response_model=PdfToolResponse)
async def rotate_pdf(
    file: UploadFile = File(...),
    angle: int = Form(90),
    pages: str = Form("all"),
):
    logger.info("rotate_pdf: file=%s angle=%d pages=%s", file.filename, angle, pages)
    return await pdf_controller.rotate(
        file,
        angle=angle,
        pages_spec=pages,
    )


@router.post("/extract", response_model=PdfToolResponse)
async def extract_pdf_pages(
    file: UploadFile = File(...),
    pages: str = Form(...),
):
    logger.info("extract_pdf_pages: file=%s pages=%s", file.filename, pages)
    return await pdf_controller.extract_pages(
        file,
        pages_spec=pages,
    )


@router.post("/to-images", response_model=PdfImagesResponse)
async def pdf_to_images(
    file: UploadFile = File(...),
    image_format: str = Form("png"),
    dpi: int = Form(150),
    as_zip: bool = Form(False),
):
    _check_pdf_to_image_capability()
    logger.info(
        "pdf_to_images: file=%s format=%s dpi=%d as_zip=%s",
        file.filename,
        image_format,
        dpi,
        as_zip,
    )
    return await pdf_controller.to_images(
        file,
        image_format=image_format,
        dpi=dpi,
        as_zip=as_zip,
    )


@router.post("/from-images", response_model=PdfToolResponse)
async def images_to_pdf(
    files: list[UploadFile] = File(...),
):
    logger.info("images_to_pdf: files=%d", len(files))
    return await pdf_controller.from_images(files)


@router.post("/info", response_model=PdfInfoResponse)
async def pdf_info(
    file: UploadFile = File(...),
):
    logger.info("pdf_info: file=%s", file.filename)
    return await pdf_controller.info(file)


@router.get("/download/{filename}")
async def download_output_file(
    filename: str,
):
    if not is_safe_filename(filename):
        raise HTTPException(
            status_code=400,
            detail="Invalid filename",
        )
    file_path = pdf_repository.get_output_file(filename)
    if not file_path.is_file():
        raise HTTPException(
            status_code=404,
            detail="Output file not found",
        )
    content_types = {
        ".pdf": "application/pdf",
        ".zip": "application/zip",
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
    }
    media_type = content_types.get(
        file_path.suffix.lower(),
        "application/octet-stream",
    )
    return FileResponse(
        path=file_path,
        media_type=media_type,
        filename=file_path.name,
    )

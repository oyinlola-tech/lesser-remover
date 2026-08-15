from fastapi import HTTPException, UploadFile

from app.infrastructure.archive.zip_adapter import zip_adapter
from app.modules.pdf.pdf_repository import pdf_repository
from app.modules.pdf.pdf_schema import (
    PdfImagesResponse,
    PdfInfoResponse,
    PdfPageFile,
    PdfToolResponse,
)
from app.modules.pdf.pdf_service import pdf_service
from app.shared.file_inspection.file_validation import (
    inspect_and_validate,
)


class PdfController:
    async def _read_pdf(
        self,
        file: UploadFile,
    ) -> tuple[bytes, str]:
        if not file.filename:
            raise HTTPException(
                status_code=400,
                detail="Filename is required",
            )
        file_data = await file.read()
        if not file_data:
            raise HTTPException(
                status_code=400,
                detail="Uploaded file is empty",
            )
        inspection = inspect_and_validate(file_data)
        if inspection.category.value != "pdf":
            raise HTTPException(
                status_code=415,
                detail="Only PDF files are supported",
            )
        return file_data, file.filename

    def _save(
        self,
        data: bytes,
        filename: str,
        details: dict | None = None,
    ) -> PdfToolResponse:
        output_path = pdf_repository.save_output_file(
            data,
            filename,
        )
        return PdfToolResponse(
            success=True,
            filename=output_path.name,
            size_bytes=len(data),
            download_url=f"/api/v1/tools/pdf/download/{output_path.name}",
            details=details or {},
        )

    async def merge(
        self,
        files: list[UploadFile],
    ) -> PdfToolResponse:
        if len(files) < 2:
            raise HTTPException(
                status_code=400,
                detail="At least two PDF files are required to merge.",
            )
        sources: list[tuple[str, bytes]] = []
        for file in files:
            file_data, filename = await self._read_pdf(file)
            sources.append((filename, file_data))
        try:
            data, page_count = pdf_service.merge(sources)
        except (OSError, ValueError, RuntimeError) as error:
            raise HTTPException(
                status_code=400,
                detail=f"Unable to merge PDFs: {error}",
            ) from error
        return self._save(
            data,
            "merged.pdf",
            {
                "source_count": len(sources),
                "page_count": page_count,
            },
        )

    async def split(
        self,
        file: UploadFile,
    ) -> PdfToolResponse:
        file_data, filename = await self._read_pdf(file)
        try:
            data, entries = pdf_service.split(file_data, filename)
        except (OSError, ValueError, RuntimeError) as error:
            raise HTTPException(
                status_code=400,
                detail=f"Unable to split PDF: {error}",
            ) from error
        base_name = filename.rsplit(".", 1)[0]
        return self._save(
            data,
            f"{base_name}-split.zip",
            {"page_count": len(entries)},
        )

    async def rotate(
        self,
        file: UploadFile,
        angle: int,
        pages_spec: str,
    ) -> PdfToolResponse:
        file_data, filename = await self._read_pdf(file)
        try:
            data, page_count = pdf_service.rotate(
                file_data,
                angle,
                pages_spec,
            )
        except (OSError, ValueError, RuntimeError) as error:
            raise HTTPException(
                status_code=400,
                detail=f"Unable to rotate PDF: {error}",
            ) from error
        return self._save(
            data,
            f"{filename.rsplit('.', 1)[0]}-rotated.pdf",
            {
                "angle": angle,
                "page_count": page_count,
            },
        )

    async def extract_pages(
        self,
        file: UploadFile,
        pages_spec: str,
    ) -> PdfToolResponse:
        file_data, filename = await self._read_pdf(file)
        try:
            data, entries = pdf_service.extract_pages(
                file_data,
                pages_spec,
                filename,
            )
        except (OSError, ValueError, RuntimeError) as error:
            raise HTTPException(
                status_code=400,
                detail=f"Unable to extract pages: {error}",
            ) from error
        base_name = filename.rsplit(".", 1)[0]
        return self._save(
            data,
            f"{base_name}-extracted.zip",
            {"page_count": len(entries)},
        )

    async def to_images(
        self,
        file: UploadFile,
        image_format: str,
        dpi: int,
        as_zip: bool = False,
    ) -> PdfImagesResponse:
        file_data, filename = await self._read_pdf(file)
        try:
            pages = pdf_service.to_images(
                file_data,
                image_format=image_format,
                dpi=dpi,
            )
        except (OSError, ValueError, RuntimeError) as error:
            raise HTTPException(
                status_code=400,
                detail=f"Unable to convert PDF: {error}",
            ) from error
        base_name = filename.rsplit(".", 1)[0]
        details = {
            "page_count": len(pages),
            "image_format": image_format,
            "dpi": dpi,
        }
        if as_zip:
            data = zip_adapter.create_archive(pages)
            output_path = pdf_repository.save_output_file(
                data,
                f"{base_name}-pages.zip",
            )
            return PdfImagesResponse(
                success=True,
                image_format=image_format,
                dpi=dpi,
                page_count=len(pages),
                as_zip=True,
                filename=output_path.name,
                size_bytes=len(data),
                download_url=(
                    f"/api/v1/tools/pdf/download/{output_path.name}"
                ),
                details=details,
            )
        page_files: list[PdfPageFile] = []
        for index, (page_name, page_data) in enumerate(
            pages,
            start=1,
        ):
            output_path = pdf_repository.save_output_file(
                page_data,
                page_name,
            )
            page_files.append(
                PdfPageFile(
                    filename=output_path.name,
                    size_bytes=len(page_data),
                    download_url=(
                        f"/api/v1/tools/pdf/download/"
                        f"{output_path.name}"
                    ),
                    page=index,
                )
            )
        return PdfImagesResponse(
            success=True,
            image_format=image_format,
            dpi=dpi,
            page_count=len(pages),
            as_zip=False,
            details=details,
            pages=page_files,
        )

    async def from_images(
        self,
        files: list[UploadFile],
    ) -> PdfToolResponse:
        if not files:
            raise HTTPException(
                status_code=400,
                detail="At least one image is required.",
            )
        images: list[tuple[str, bytes]] = []
        for file in files:
            if not file.filename:
                raise HTTPException(
                    status_code=400,
                    detail="Filename is required",
                )
            file_data = await file.read()
            if not file_data:
                raise HTTPException(
                    status_code=400,
                    detail="Uploaded file is empty",
                )
            inspection = inspect_and_validate(file_data)
            if inspection.category.value != "image":
                raise HTTPException(
                    status_code=415,
                    detail=f"Not an image file: {file.filename}",
                )
            images.append((file.filename, file_data))
        try:
            data, page_count = pdf_service.from_images(images)
        except (OSError, ValueError, RuntimeError) as error:
            raise HTTPException(
                status_code=400,
                detail=f"Unable to create PDF: {error}",
            ) from error
        return self._save(
            data,
            "images.pdf",
            {"page_count": page_count},
        )

    async def info(
        self,
        file: UploadFile,
    ) -> PdfInfoResponse:
        file_data, filename = await self._read_pdf(file)
        try:
            page_count = pdf_service.page_count(file_data)
        except (OSError, ValueError, RuntimeError) as error:
            raise HTTPException(
                status_code=400,
                detail=f"Unable to read PDF: {error}",
            ) from error
        return PdfInfoResponse(
            success=True,
            filename=filename,
            page_count=page_count,
            file_size_bytes=len(file_data),
        )


pdf_controller = PdfController()

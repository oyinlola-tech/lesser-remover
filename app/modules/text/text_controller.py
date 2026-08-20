"""Controller for text & speech tool HTTP operations."""

import logging
from pathlib import Path
from typing import Any, Dict

from fastapi import HTTPException
from fastapi.responses import FileResponse

from app.core.config import settings
from app.core.exceptions import ProcessingError
from app.modules.text.text_schema import (
    CaseConverterRequest,
    TextDiffRequest,
    TextToSpeechRequest,
    WordCounterRequest,
)
from app.modules.text.text_service import text_service

logger = logging.getLogger(__name__)


class TextController:
    def diff(self, request: TextDiffRequest) -> Dict[str, Any]:
        try:
            result = text_service.diff(request.text1, request.text2)
            return {"success": True, "data": result}
        except ProcessingError as err:
            raise HTTPException(status_code=400, detail=str(err))

    def convert_case(self, request: CaseConverterRequest) -> Dict[str, Any]:
        try:
            result = text_service.convert_case(request.text, request.target_case)
            return {"success": True, "result": result}
        except ProcessingError as err:
            raise HTTPException(status_code=400, detail=str(err))

    def count_words(self, request: WordCounterRequest) -> Dict[str, Any]:
        try:
            result = text_service.count_words(request.text)
            return {"success": True, "data": result}
        except ProcessingError as err:
            raise HTTPException(status_code=400, detail=str(err))

    def text_to_speech(self, request: TextToSpeechRequest) -> Dict[str, Any]:
        try:
            output_path = text_service.text_to_speech(request.text, request.language)
            file_size = output_path.stat().st_size if output_path.exists() else 0
            filename = output_path.name
            return {
                "success": True,
                "filename": filename,
                "size_bytes": file_size,
                "download_url": f"/api/v1/tools/text/download/{filename}",
            }
        except ProcessingError as err:
            raise HTTPException(status_code=400, detail=str(err))

    def serve_file(self, filename: str) -> FileResponse:
        download_dir = Path(settings.temp_directory)
        file_path = download_dir / filename
        if not file_path.exists() or not file_path.is_file():
            raise HTTPException(status_code=404, detail="File not found or expired.")
        return FileResponse(path=file_path, filename=filename, media_type="audio/mpeg")


text_controller = TextController()

"""HTTP-facing logic for the json-csv-converter and json-formatter tools."""

from fastapi import HTTPException

from app.modules.devtools.services.json_service import json_service


class JsonController:
    def json_to_csv(self, json_text: str) -> dict:
        try:
            return {"success": True, "csv": json_service.json_to_csv(json_text)}
        except ValueError as err:
            raise HTTPException(status_code=400, detail=str(err)) from err

    def csv_to_json(self, csv_text: str) -> dict:
        try:
            return {"success": True, "json": json_service.csv_to_json(csv_text)}
        except ValueError as err:
            raise HTTPException(status_code=400, detail=str(err)) from err

    def json_format(self, json_text: str, minify: bool = False) -> dict:
        try:
            result = json_service.json_format(json_text, minify=minify)
            return {"success": True, "result": result}
        except ValueError as err:
            raise HTTPException(status_code=400, detail=str(err)) from err


json_controller = JsonController()

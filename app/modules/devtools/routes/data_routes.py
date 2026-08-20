"""Routes for the json-csv-converter, json-formatter and jwt-decoder tools."""

from fastapi import APIRouter
from pydantic import BaseModel

from app.modules.devtools.dev_tools_controller import dev_tools_controller

data_router = APIRouter(tags=["Developer Tools"])


class JsonCsvPayload(BaseModel):
    data: str


class JsonFormatPayload(BaseModel):
    json_text: str
    minify: bool = False


class JwtDecodePayload(BaseModel):
    token: str


@data_router.post("/json-to-csv")
async def json_to_csv(payload: JsonCsvPayload):
    return dev_tools_controller.json_to_csv(payload.data)


@data_router.post("/csv-to-json")
async def csv_to_json(payload: JsonCsvPayload):
    return dev_tools_controller.csv_to_json(payload.data)


@data_router.post("/json-format")
async def json_format(payload: JsonFormatPayload):
    return dev_tools_controller.json_format(payload.json_text, minify=payload.minify)


@data_router.post("/jwt-decode")
async def jwt_decode(payload: JwtDecodePayload):
    return dev_tools_controller.jwt_decode(payload.token)

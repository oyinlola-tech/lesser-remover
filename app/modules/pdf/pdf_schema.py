from pydantic import BaseModel


class PdfSchema(BaseModel):
    filename: str
    size_bytes: int

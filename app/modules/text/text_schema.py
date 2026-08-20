"""Pydantic schemas for Text & Audio Tools API requests."""

from pydantic import BaseModel, Field


class TextDiffRequest(BaseModel):
    text1: str = Field(..., description="Original text")
    text2: str = Field(..., description="Modified text")


class CaseConverterRequest(BaseModel):
    text: str = Field(..., description="Text to convert")
    target_case: str = Field(
        ...,
        description="Target case (camel, snake, kebab, title, upper, lower)",
    )


class WordCounterRequest(BaseModel):
    text: str = Field(..., description="Text to analyze")


class TextToSpeechRequest(BaseModel):
    text: str = Field(..., description="Text input to speak")
    language: str = Field(default="en", description="Language code (e.g., en, es, fr, de)")

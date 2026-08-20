"""Unit tests for the 11 new Vercel-compatible utility tools."""

from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.modules.devtools.dev_tools_service import dev_tools_service
from app.modules.text.text_service import text_service
from app.modules.image.image_service import image_service

client = TestClient(app)


def test_json_to_csv_service():
    json_str = '[{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]'
    csv_out = dev_tools_service.json_to_csv(json_str)
    assert "name,age" in csv_out
    assert "Alice,30" in csv_out


def test_csv_to_json_service():
    csv_str = "name,age\nAlice,30\nBob,25"
    json_out = dev_tools_service.csv_to_json(csv_str)
    assert '"name": "Alice"' in json_out


def test_json_format_service():
    raw_json = '{"b": 2, "a": 1}'
    formatted = dev_tools_service.json_format(raw_json, minify=False)
    assert "\n" in formatted
    minified = dev_tools_service.json_format(raw_json, minify=True)
    assert "\n" not in minified


def test_jwt_decode_service():
    # Sample un-signed JWT token string (header.payload.sig)
    # Header: {"alg":"HS256","typ":"JWT"} -> eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9
    # Payload: {"sub":"1234567890","name":"John Doe"} -> eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIn0
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIn0.signature"
    res = dev_tools_service.jwt_decode(token)
    assert res["header"]["alg"] == "HS256"
    assert res["payload"]["name"] == "John Doe"


def test_text_diff_service():
    res = text_service.diff("line1\nline2", "line1\nline2_modified")
    assert res["has_changes"] is True
    assert "-line2" in res["diff"]
    assert "+line2_modified" in res["diff"]


def test_case_converter_service():
    assert text_service.convert_case("hello world", "camel") == "helloWorld"
    assert text_service.convert_case("hello world", "snake") == "hello_world"
    assert text_service.convert_case("hello world", "kebab") == "hello-world"
    assert text_service.convert_case("hello world", "upper") == "HELLO WORLD"


def test_word_counter_service():
    stats = text_service.count_words("Hello world! This is a test.")
    assert stats["words"] == 6
    assert stats["sentences"] == 2
    assert stats["characters"] == 28


@patch("gtts.gTTS.save")
def test_text_to_speech_service(mock_save):
    output_file = text_service.text_to_speech("Hello world", language="en")
    assert output_file.suffix == ".mp3"
    assert mock_save.called


def test_api_text_routes():
    res = client.post("/api/v1/tools/text/convert-case", json={"text": "hello world", "target_case": "snake"})
    assert res.status_code == 200
    assert res.json()["result"] == "hello_world"

    res = client.post("/api/v1/tools/text/word-counter", json={"text": "Quick brown fox"})
    assert res.status_code == 200
    assert res.json()["data"]["words"] == 3


def test_api_dev_json_csv_routes():
    res = client.post("/api/v1/tools/dev/json-to-csv", json={"data": '[{"a":1}]'})
    assert res.status_code == 200
    assert "a" in res.json()["csv"]

    res = client.post("/api/v1/tools/dev/jwt-decode", json={"token": "eyJhbGciOiJIUzI1NiJ9.eyJ1c2VyIjoiYWxpY2UifQ.sig"})
    assert res.status_code == 200
    assert res.json()["data"]["payload"]["user"] == "alice"

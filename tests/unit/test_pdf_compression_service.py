from app.modules.compression.pdf_compression.pdf_compression_service import (
    pdf_compression_service,
)

from app.infrastructure.compression import ghostscript_adapter


class DummyGs:
    def __init__(self, mapping):
        self.mapping = mapping

    def compress(self, file_data: bytes, quality: str) -> bytes:
        if quality not in self.mapping:
            raise RuntimeError("quality unsupported")
        size = self.mapping[quality]
        return b"x" * size


def test_compress_best_prefers_smallest(monkeypatch):
    original = b"o" * 1000
    # mapping returns sizes for qualities
    mapping = {"ebook": 800, "screen": 600, "printer": 700}
    dummy = DummyGs(mapping)

    monkeypatch.setattr(ghostscript_adapter.ghostscript_adapter, "compress", dummy.compress)

    data, q = pdf_compression_service.compress_best(original, preset="balanced")

    assert q == "screen"
    assert len(data) == 600


def test_compress_best_keeps_original_if_no_improvement(monkeypatch):
    original = b"o" * 500
    mapping = {"ebook": 500, "screen": 600, "printer": 700}
    dummy = DummyGs(mapping)

    monkeypatch.setattr(ghostscript_adapter.ghostscript_adapter, "compress", dummy.compress)

    data, q = pdf_compression_service.compress_best(original, preset="balanced")

    assert q == "original"
    assert data == original


def test_compress_best_raises_when_all_fail(monkeypatch):
    original = b"o" * 1000

    def fail_compress(file_data: bytes, quality: str) -> bytes:
        raise RuntimeError("failed")

    monkeypatch.setattr(ghostscript_adapter.ghostscript_adapter, "compress", fail_compress)

    try:
        pdf_compression_service.compress_best(original, preset="balanced")
        raised = False
    except RuntimeError:
        raised = True

    assert raised

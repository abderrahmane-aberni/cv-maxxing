import io

import pytest
from pypdf import PdfWriter

from app.pdf_parser import PDFTextExtractionError, extract_text_from_pdf


def _blank_pdf_bytes() -> bytes:
    """A structurally valid but textless PDF (pypdf's writer has no
    text-drawing API) — enough to exercise the "no usable text" path."""
    writer = PdfWriter()
    writer.add_blank_page(width=612, height=792)
    buffer = io.BytesIO()
    writer.write(buffer)
    return buffer.getvalue()


def test_blank_pdf_raises_extraction_error():
    with pytest.raises(PDFTextExtractionError):
        extract_text_from_pdf(_blank_pdf_bytes())


def test_not_a_pdf_raises_extraction_error():
    with pytest.raises(PDFTextExtractionError):
        extract_text_from_pdf(b"this is not a pdf")

"""Extract plain text from an uploaded CV PDF.

Tries pypdf first (fast, pure-Python). Falls back to pdfplumber, which is
slower but sometimes recovers text pypdf misses on oddly-encoded PDFs.
Raises PDFTextExtractionError if neither backend can extract usable text
(e.g. a scanned/image-only PDF with no text layer — OCR is out of scope).
"""
from __future__ import annotations

import io


class PDFTextExtractionError(ValueError):
    """Raised when no usable text could be extracted from the PDF."""


def extract_text_from_pdf(file_bytes: bytes) -> str:
    text = _try_pypdf(file_bytes)
    if _is_usable(text):
        return text.strip()

    text = _try_pdfplumber(file_bytes)
    if _is_usable(text):
        return text.strip()

    raise PDFTextExtractionError(
        "Could not extract text from this PDF. It may be a scanned image "
        "with no embedded text layer (OCR is not supported yet)."
    )


def _is_usable(text: str) -> bool:
    return bool(text) and len(text.strip()) >= 40


def _try_pypdf(file_bytes: bytes) -> str:
    try:
        from pypdf import PdfReader

        reader = PdfReader(io.BytesIO(file_bytes))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    except Exception:
        return ""


def _try_pdfplumber(file_bytes: bytes) -> str:
    try:
        import pdfplumber

        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            return "\n".join(page.extract_text() or "" for page in pdf.pages)
    except Exception:
        return ""

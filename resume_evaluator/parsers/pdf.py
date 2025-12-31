"""PDF parsing utilities."""

from typing import Optional

from pypdf import PdfReader
from pypdf.errors import PdfReadError


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """
    Extract text from PDF bytes.

    Args:
        pdf_bytes: PDF file content as bytes.

    Returns:
        Extracted text from the PDF.

    Raises:
        ValueError: If PDF parsing fails.
    """
    try:
        from io import BytesIO

        pdf_file = BytesIO(pdf_bytes)
        reader = PdfReader(pdf_file)
        text_parts = []

        for page in reader.pages:
            try:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
            except Exception as e:
                # Log but continue with other pages
                print(f"Warning: Failed to extract text from page: {e}")
                continue

        if not text_parts:
            raise ValueError("No text could be extracted from the PDF")

        return "\n\n".join(text_parts)

    except PdfReadError as e:
        raise ValueError(f"Failed to read PDF: {e}") from e
    except Exception as e:
        raise ValueError(f"Unexpected error parsing PDF: {e}") from e

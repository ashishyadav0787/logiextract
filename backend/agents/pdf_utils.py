import pdfplumber
import io
from typing import Tuple

def extract_text_from_pdf(file_bytes: bytes) -> Tuple[str, int]:
    """
    Extract all text from a PDF file.
    Returns (text, page_count)
    """
    text_parts = []
    page_count = 0

    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        page_count = len(pdf.pages)
        for i, page in enumerate(pdf.pages):
            page_text = page.extract_text()
            if page_text:
                text_parts.append(f"[PAGE {i+1}]\n{page_text}")

            # Also extract tables if present
            tables = page.extract_tables()
            for table in tables:
                if table:
                    table_text = "\n".join(
                        " | ".join(str(cell) if cell else "" for cell in row)
                        for row in table
                        if row
                    )
                    text_parts.append(f"[TABLE]\n{table_text}")

    return "\n\n".join(text_parts), page_count

def validate_pdf(file_bytes: bytes) -> bool:
    """Check if the file is a valid PDF."""
    return file_bytes[:4] == b'%PDF'

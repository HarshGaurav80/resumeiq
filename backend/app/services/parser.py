"""
Resume text extraction for PDF (pdfplumber) and DOCX (python-docx) files.
"""
import io
import re

import pdfplumber
from docx import Document


class ResumeParseError(Exception):
    """Raised when a resume file cannot be read or contains no text."""


def extract_text_from_pdf(data: bytes) -> str:
    try:
        pages = []
        with pdfplumber.open(io.BytesIO(data)) as pdf:
            for page in pdf.pages:
                pages.append(page.extract_text() or "")
        return "\n".join(pages)
    except Exception as exc:  # pdfplumber raises many different error types
        raise ResumeParseError("The PDF file appears to be corrupted or password-protected.") from exc


def extract_text_from_docx(data: bytes) -> str:
    try:
        doc = Document(io.BytesIO(data))
    except Exception as exc:
        raise ResumeParseError("The DOCX file could not be opened. Is it a valid Word document?") from exc

    lines = [p.text for p in doc.paragraphs]
    # Many resume templates put content inside tables
    for table in doc.tables:
        for row in table.rows:
            seen = set()
            for cell in row.cells:
                # merged cells repeat; skip duplicates
                if id(cell._tc) in seen:
                    continue
                seen.add(id(cell._tc))
                lines.append(cell.text)
    return "\n".join(lines)


def clean_text(text: str) -> str:
    """Normalise whitespace and odd characters produced by PDF extraction."""
    text = text.replace("\r", "\n").replace("\t", " ")
    text = re.sub(r"\(cid:\d+\)", "•", text)  # unmapped glyphs (usually bullet symbols) in some PDFs
    text = text.replace("•", "•").replace("", "•").replace("●", "•")
    text = re.sub(r"[  ]{2,}", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_text(filename: str, data: bytes) -> str:
    """Pick the right extractor from the file extension and return cleaned text."""
    name = filename.lower()
    if name.endswith(".pdf"):
        if not data.startswith(b"%PDF"):
            raise ResumeParseError("This file does not look like a real PDF.")
        text = extract_text_from_pdf(data)
    elif name.endswith(".docx"):
        if not data.startswith(b"PK"):  # DOCX files are zip archives
            raise ResumeParseError("This file does not look like a real DOCX document.")
        text = extract_text_from_docx(data)
    else:
        raise ResumeParseError("Unsupported file type. Please upload a PDF or DOCX file.")

    text = clean_text(text)
    if len(text) < 50:
        raise ResumeParseError(
            "Very little text could be extracted. If your resume is a scanned image, "
            "please export it as a text-based PDF or DOCX.")
    return text

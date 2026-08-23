"""
Text extraction from uploaded resumes.
(PPT requirement: "Input: PDF/Text resumes + job description")
"""
import pdfplumber
import io


def extract_text_from_pdf(file_bytes: bytes) -> str:
    text_parts = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    return "\n".join(text_parts).strip()


def extract_text(filename: str, file_bytes: bytes) -> str:
    """Dispatch based on file extension. Supports .pdf and .txt."""
    if filename.lower().endswith(".pdf"):
        return extract_text_from_pdf(file_bytes)
    elif filename.lower().endswith(".txt"):
        return file_bytes.decode("utf-8", errors="ignore").strip()
    else:
        raise ValueError("Unsupported file type. Please upload a .pdf or .txt resume.")

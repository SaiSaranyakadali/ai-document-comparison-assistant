from io import BytesIO
from pypdf import PdfReader
from pypdf.errors import PdfReadError as PypdfError

class PDFReadError(Exception):
    """Raised when a PDF cannot be read or contains no extractable text."""

def extract_pdf_text(data: bytes):
    if not data:
        raise PDFReadError("The uploaded file is empty.")
    if not data.startswith(b"%PDF"):
        raise PDFReadError("This file does not appear to be a valid PDF.")
    try:
        reader = PdfReader(BytesIO(data), strict=False)
        if reader.is_encrypted:
            try:
                reader.decrypt("")
            except Exception:
                raise PDFReadError("This PDF is encrypted or password-protected.")
        chunks = []
        for page_num, page in enumerate(reader.pages, start=1):
            try:
                page_text = (page.extract_text() or "").strip()
            except Exception:
                page_text = ""
            if page_text:
                chunks.append(f"[Page {page_num}]\n{page_text}")
        text = "\n\n".join(chunks).strip()
        if not text:
            raise PDFReadError("No readable text was found. This may be a scanned/image-only PDF; OCR is not included.")
        return text, len(reader.pages)
    except PDFReadError:
        raise
    except (PypdfError, Exception) as exc:
        raise PDFReadError(f"Could not read this PDF ({type(exc).__name__}). Please try another text-based PDF.")

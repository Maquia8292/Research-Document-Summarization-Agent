"""
Document Parser Module for Research & Document Summarization Agent.
Handles PDF, TXT, and Markdown file parsing, text extraction, and document analytics.
"""

import io
import math
from typing import Dict, Any, List, Optional, Union

import importlib

# Dynamic import to avoid static IDE linter warnings if pypdf is not indexed in the active workspace environment
PdfReader = None
PDF_READER_AVAILABLE = False

try:
    _pypdf_mod = importlib.import_module("pypdf")
    PdfReader = getattr(_pypdf_mod, "PdfReader", None)
    if PdfReader is not None:
        PDF_READER_AVAILABLE = True
except ImportError:
    try:
        _pypdf2_mod = importlib.import_module("PyPDF2")
        PdfReader = getattr(_pypdf2_mod, "PdfReader", None)
        if PdfReader is not None:
            PDF_READER_AVAILABLE = True
    except ImportError:
        PDF_READER_AVAILABLE = False



def extract_text_from_pdf(file_bytes: bytes) -> Dict[str, Any]:
    """
    Extract text and metadata from PDF bytes using pypdf/PyPDF2.
    
    Args:
        file_bytes: Raw bytes of the uploaded PDF file.
        
    Returns:
        Dict containing full text, clean text, page count, and status flags.
    """
    if not PDF_READER_AVAILABLE:
        raise ImportError(
            "PDF reading library missing. Please install pypdf by running: pip install pypdf"
        )

    if not file_bytes or len(file_bytes) == 0:
        raise ValueError("The uploaded PDF file is empty (0 bytes).")

    pdf_stream = io.BytesIO(file_bytes)
    try:
        reader = PdfReader(pdf_stream)
    except Exception as e:
        raise ValueError(f"Could not open or parse PDF file: {str(e)}")

    if getattr(reader, "is_encrypted", False):
        try:
            # Try decrypting with empty password for unencrypted-protected PDFs
            reader.decrypt("")
        except Exception as e:
            raise ValueError(f"PDF is password-encrypted and could not be unlocked: {str(e)}")

    total_pages = len(reader.pages) if hasattr(reader, "pages") else 0
    if total_pages == 0:
        raise ValueError("The uploaded PDF file contains 0 pages.")

    formatted_pages: List[str] = []
    actual_text_pieces: List[str] = []

    for i, page in enumerate(reader.pages):
        page_num = i + 1
        try:
            page_text = page.extract_text() or ""
            cleaned = page_text.strip()
            if cleaned:
                formatted_pages.append(f"--- Page {page_num} ---\n{cleaned}")
                actual_text_pieces.append(cleaned)
            else:
                formatted_pages.append(f"--- Page {page_num} ---\n[No extractable text found on this page]")
        except Exception as e:
            formatted_pages.append(f"--- Page {page_num} ---\n[Error reading page {page_num}: {str(e)}]")

    full_display_text = "\n\n".join(formatted_pages)
    clean_extracted_text = "\n\n".join(actual_text_pieces)
    has_extractable_text = len(actual_text_pieces) > 0

    if not has_extractable_text:
        full_display_text += "\n\n⚠️ Note: No selectable text could be extracted from this PDF. It may be a scanned image-only PDF."

    return {
        "text": full_display_text,
        "clean_text": clean_extracted_text,
        "page_count": total_pages,
        "pages": formatted_pages,
        "has_extractable_text": has_extractable_text
    }


def extract_text_from_txt(file_bytes: bytes) -> str:
    """
    Extract text from plain text or markdown file bytes with encoding fallbacks.
    
    Args:
        file_bytes: Raw bytes of the text file.
        
    Returns:
        Decoded text string.
    """
    if not file_bytes or len(file_bytes) == 0:
        raise ValueError("The uploaded text file is empty (0 bytes).")

    encodings = ["utf-8", "utf-8-sig", "latin-1", "cp1252"]
    for enc in encodings:
        try:
            return file_bytes.decode(enc)
        except (UnicodeDecodeError, AttributeError):
            continue
    return file_bytes.decode("utf-8", errors="ignore")


def calculate_document_stats(raw_text: str, clean_text: str = "", page_count: int = 1) -> Dict[str, Any]:
    """
    Calculate word count, character count, estimated reading time, and token approximation
    based on actual extracted content rather than structural page wrappers.
    
    Args:
        raw_text: Full formatted text display string.
        clean_text: Clean extracted content without structural page wrappers.
        page_count: Number of document pages.
        
    Returns:
        Dict with document analytics metadata.
    """
    target_text = clean_text.strip() if clean_text.strip() else raw_text.strip()
    words = target_text.split()
    word_count = len(words)
    char_count = len(target_text)
    
    # Average adult reading speed: ~220 wpm
    read_time_minutes = math.ceil(word_count / 220) if word_count > 0 else 0
    # Approximate tokens (~1.3 tokens per word)
    approx_tokens = math.ceil(word_count * 1.3)

    return {
        "word_count": word_count,
        "char_count": char_count,
        "page_count": page_count,
        "read_time_minutes": read_time_minutes,
        "approx_tokens": approx_tokens
    }


def parse_uploaded_document(file_name: str, file_data: Union[bytes, Any]) -> Dict[str, Any]:
    """
    Main parsing controller that inspects file extension and extracts content & stats.
    Flexibly accepts raw bytes or Streamlit UploadedFile objects.
    
    Args:
        file_name: Name of the uploaded file.
        file_data: Raw file content in bytes or file-like object.
        
    Returns:
        Dict containing filename, file_type, text, clean_text, stats, and metadata.
    """
    if not file_name:
        raise ValueError("Invalid file upload: Missing filename.")

    # Convert file_data to bytes if file-like object passed
    if isinstance(file_data, bytes):
        file_bytes = file_data
    elif hasattr(file_data, "getvalue"):
        file_bytes = file_data.getvalue()
    elif hasattr(file_data, "read"):
        file_bytes = file_data.read()
    else:
        file_bytes = bytes(file_data)

    lower_name = file_name.lower()
    
    if lower_name.endswith(".pdf"):
        file_type = "PDF Document"
        pdf_res = extract_text_from_pdf(file_bytes)
        text = pdf_res["text"]
        clean_text = pdf_res["clean_text"]
        page_count = pdf_res["page_count"]
    elif lower_name.endswith((".txt", ".md")):
        file_type = "Text / Markdown"
        text = extract_text_from_txt(file_bytes)
        clean_text = text
        page_count = 1
    else:
        raise ValueError(f"Unsupported file format for '{file_name}'. Please upload PDF, TXT, or MD files.")

    stats = calculate_document_stats(text, clean_text=clean_text, page_count=page_count)

    return {
        "file_name": file_name,
        "file_type": file_type,
        "file_size_bytes": len(file_bytes),
        "text": text,
        "clean_text": clean_text if clean_text else text,
        "stats": stats
    }


def chunk_text(text: str, max_chunk_chars: int = 12000, overlap_chars: int = 500) -> List[str]:
    """
    Splits extra long text into overlapping chunks for chunked processing if needed.
    
    Args:
        text: Input text string.
        max_chunk_chars: Maximum characters per chunk.
        overlap_chars: Number of overlapping characters between adjacent chunks.
        
    Returns:
        List of text chunk strings.
    """
    if not text or len(text) <= max_chunk_chars:
        return [text] if text else []

    chunks = []
    start = 0
    while start < len(text):
        end = start + max_chunk_chars
        chunks.append(text[start:end])
        start += max_chunk_chars - overlap_chars
    return chunks

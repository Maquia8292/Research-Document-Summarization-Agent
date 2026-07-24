"""
Document Parser Module for Research & Document Summarization Agent.
Handles PDF, TXT, and Markdown file parsing, text extraction, and document analytics.
"""

import io
import math
from typing import Dict, Any, List, Optional

try:
    from pypdf import PdfReader
    PDF_READER_AVAILABLE = True
except ImportError:
    try:
        from PyPDF2 import PdfReader
        PDF_READER_AVAILABLE = True
    except ImportError:
        PDF_READER_AVAILABLE = False



def extract_text_from_pdf(file_bytes: bytes) -> Dict[str, Any]:
    """
    Extract text and metadata from PDF bytes using pypdf.
    
    Args:
        file_bytes: Raw bytes of the uploaded PDF file.
        
    Returns:
        Dict containing raw text, page count, and status.
    """
    if not PDF_READER_AVAILABLE:
        raise ImportError(
            "PDF reading library missing. Please install pypdf by running: pip install pypdf"
        )

    pdf_stream = io.BytesIO(file_bytes)
    reader = PdfReader(pdf_stream)

    
    if reader.is_encrypted:
        try:
            # Try decrypting with empty password for unencrypted-protected PDFs
            reader.decrypt("")
        except Exception as e:
            raise ValueError(f"PDF is encrypted and could not be unlocked: {str(e)}")

    extracted_pages: List[str] = []
    total_pages = len(reader.pages)

    for i, page in enumerate(reader.pages):
        page_text = page.extract_text()
        if page_text:
            extracted_pages.append(f"--- Page {i + 1} ---\n{page_text.strip()}")
        else:
            extracted_pages.append(f"--- Page {i + 1} ---\n[No extractable text found on this page]")

    full_text = "\n\n".join(extracted_pages)
    return {
        "text": full_text,
        "page_count": total_pages,
        "pages": extracted_pages
    }


def extract_text_from_txt(file_bytes: bytes) -> str:
    """
    Extract text from plain text or markdown file bytes with encoding fallbacks.
    
    Args:
        file_bytes: Raw bytes of the text file.
        
    Returns:
        Decoded text string.
    """
    encodings = ["utf-8", "utf-8-sig", "latin-1", "cp1252"]
    for enc in encodings:
        try:
            return file_bytes.decode(enc)
        except (UnicodeDecodeError, AttributeError):
            continue
    return file_bytes.decode("utf-8", errors="ignore")


def calculate_document_stats(text: str, page_count: int = 1) -> Dict[str, Any]:
    """
    Calculate word count, character count, estimated reading time, and token approximation.
    
    Args:
        text: Extracted full text string.
        page_count: Number of document pages.
        
    Returns:
        Dict with document analytics metadata.
    """
    cleaned_text = text.strip()
    words = cleaned_text.split()
    word_count = len(words)
    char_count = len(cleaned_text)
    
    # Average adult reading speed: ~200-250 wpm
    read_time_minutes = math.ceil(word_count / 220) if word_count > 0 else 0
    # Approximate tokens (~4 characters or 0.75 words per token)
    approx_tokens = math.ceil(word_count * 1.3)

    return {
        "word_count": word_count,
        "char_count": char_count,
        "page_count": page_count,
        "read_time_minutes": read_time_minutes,
        "approx_tokens": approx_tokens
    }


def parse_uploaded_document(file_name: str, file_bytes: bytes) -> Dict[str, Any]:
    """
    Main parsing controller that inspects file extension and extracts content & stats.
    
    Args:
        file_name: Name of the uploaded file.
        file_bytes: Raw file content in bytes.
        
    Returns:
        Dict containing filename, file_type, text, stats, and metadata.
    """
    lower_name = file_name.lower()
    
    if lower_name.endswith(".pdf"):
        file_type = "PDF Document"
        pdf_res = extract_text_from_pdf(file_bytes)
        text = pdf_res["text"]
        page_count = pdf_res["page_count"]
    elif lower_name.endswith((".txt", ".md")):
        file_type = "Text / Markdown"
        text = extract_text_from_txt(file_bytes)
        page_count = 1
    else:
        raise ValueError(f"Unsupported file format for '{file_name}'. Please upload PDF, TXT, or MD files.")

    stats = calculate_document_stats(text, page_count=page_count)

    return {
        "file_name": file_name,
        "file_type": file_type,
        "file_size_bytes": len(file_bytes),
        "text": text,
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
    if len(text) <= max_chunk_chars:
        return [text]

    chunks = []
    start = 0
    while start < len(text):
        end = start + max_chunk_chars
        chunks.append(text[start:end])
        start += max_chunk_chars - overlap_chars
    return chunks

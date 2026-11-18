import os
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from axion.core.types import BoundingBox, TrustTier
from axion.ingestion.chunker import SemanticChunker, ChunkResult

class ExtractedBlock(BaseModel):
    page_number: int
    text: str
    bbox: Optional[BoundingBox] = None
    block_type: int = 0 # 0 = text, 1 = image

class ExtractedDocument(BaseModel):
    file_path: str
    file_hash_sha256: str
    title: str
    page_count: int
    chunks: List[ChunkResult]
    bounding_boxes: List[Dict[str, Any]]
    metadata: Dict[str, Any]

class UniversalReader:
    """
    Component 1: Universal Knowledge Reader
    Ingests and parses research PDFs with bounding-box coordinate provenance.
    """
    def __init__(self, target_chunk_tokens: int = 400):
        self.chunker = SemanticChunker(target_chunk_tokens=target_chunk_tokens)

    @staticmethod
    def calculate_file_hash(file_bytes: bytes) -> str:
        """Computes SHA-256 checksum of document bytes."""
        return hashlib.sha256(file_bytes).hexdigest()

    def parse_pdf(self, file_path: str, title: Optional[str] = None) -> ExtractedDocument:
        """
        Parses a PDF file using PyMuPDF (fitz), extracting text blocks,
        column-aware reading order, and exact bounding box coordinates.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"PDF file not found at: {file_path}")

        file_bytes = path.read_bytes()
        file_hash = self.calculate_file_hash(file_bytes)
        doc_title = title or path.stem.replace("_", " ").title()

        pages_content: List[Dict[str, Any]] = []
        all_bboxes: List[Dict[str, Any]] = []

        try:
            import pymupdf as fitz
            doc = fitz.open(file_path)
            page_count = len(doc)
            meta = doc.metadata or {}
            if not title and meta.get("title"):
                doc_title = meta["title"]

            for page_idx in range(page_count):
                page = doc[page_idx]
                page_no = page_idx + 1
                
                # Extract blocks with coordinates: (x0, y0, x1, y1, text, block_no, block_type)
                blocks = page.get_text("blocks")
                
                # Column-aware sorting: group into columns by x0 threshold
                # For standard 2-column papers, x0 < page.rect.width / 2 is left column
                page_width = page.rect.width
                left_col = []
                right_col = []

                for b in blocks:
                    x0, y0, x1, y1, text, block_no, block_type = b
                    if not text.strip():
                        continue
                    if x0 < page_width * 0.48:
                        left_col.append(b)
                    else:
                        right_col.append(b)

                # Sort each column vertically by y0
                left_col.sort(key=lambda b: b[1])
                right_col.sort(key=lambda b: b[1])
                sorted_blocks = left_col + right_col

                page_text_blocks = []
                for b in sorted_blocks:
                    x0, y0, x1, y1, text, block_no, block_type = b
                    page_text_blocks.append(text)
                    all_bboxes.append({
                        "page_number": page_no,
                        "x0": round(float(x0), 2),
                        "y0": round(float(y0), 2),
                        "x1": round(float(x1), 2),
                        "y1": round(float(y1), 2),
                        "snippet": text.strip()[:100]
                    })

                full_page_text = "\n\n".join(page_text_blocks)
                pages_content.append({
                    "page_number": page_no,
                    "text": full_page_text
                })

            doc.close()

        except ImportError:
            # Fallback if PyMuPDF C-extension is not yet ready: read as raw text
            page_count = 1
            pages_content = [{
                "page_number": 1,
                "text": path.read_text(errors="replace")
            }]
            meta = {}

        # Chunk the parsed document using semantic heading-aware chunker
        chunks = self.chunker.chunk_document_pages(pages_content)

        return ExtractedDocument(
            file_path=str(path.resolve()),
            file_hash_sha256=file_hash,
            title=doc_title,
            page_count=page_count,
            chunks=chunks,
            bounding_boxes=all_bboxes,
            metadata={
                "parser": "UniversalReader:PyMuPDF",
                "original_filename": path.name,
                "file_size_bytes": len(file_bytes)
            }
        )

    def parse_text(self, text_content: str, title: str, source_uri: str = "manual://input") -> ExtractedDocument:
        """Parses raw text or Markdown string."""
        file_bytes = text_content.encode("utf-8")
        file_hash = self.calculate_file_hash(file_bytes)
        
        pages_content = [{"page_number": 1, "text": text_content}]
        chunks = self.chunker.chunk_document_pages(pages_content)

        return ExtractedDocument(
            file_path=source_uri,
            file_hash_sha256=file_hash,
            title=title,
            page_count=1,
            chunks=chunks,
            bounding_boxes=[],
            metadata={"parser": "UniversalReader:Text", "source_uri": source_uri}
        )

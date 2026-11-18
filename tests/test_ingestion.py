import pytest
import tempfile
from pathlib import Path
from axion.ingestion.chunker import SemanticChunker
from axion.ingestion.reader import UniversalReader
from axion.ingestion.source_manager import SourceManager
from axion.database.models import Document, DocumentChunk

def test_semantic_chunker_basic():
    chunker = SemanticChunker(target_chunk_tokens=50)
    pages = [
        {
            "page_number": 1,
            "text": """# 1. INTRODUCTION
This is the first sentence about solar vehicles.
Energy conversion efficiency is critical for long-range cruising.

# 2. THERMODYNAMICS
Heat dissipation in battery cells is governed by Fourier conduction.
$$ q = -k \\nabla T $$
This equation defines the thermal boundary."""
        }
    ]
    chunks = chunker.chunk_document_pages(pages)
    assert len(chunks) >= 2
    assert chunks[0].page_number == 1
    assert any(c.is_equation_block for c in chunks)
    assert any("THERMODYNAMICS" in (c.structural_header or "") for c in chunks)

def test_universal_reader_text_parsing():
    reader = UniversalReader()
    text = "Solid state batteries replace liquid electrolytes with solid ceramics."
    parsed = reader.parse_text(text, title="Battery Review")
    
    assert parsed.title == "Battery Review"
    assert parsed.page_count == 1
    assert len(parsed.chunks) >= 1
    assert len(parsed.file_hash_sha256) == 64

def test_universal_reader_pdf_generation_and_parsing():
    import pymupdf as fitz
    
    # Create an ephemeral test PDF with two pages and coordinates
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        doc = fitz.open()
        p1 = doc.new_page(width=595, height=842)
        p1.insert_text((50, 72), "1. Introduction to Quantum Transport", fontsize=14)
        p1.insert_text((50, 100), "Electron mobility in graphene exceeds traditional semiconductors.", fontsize=11)
        
        p2 = doc.new_page(width=595, height=842)
        p2.insert_text((50, 72), "2. Governing Equations", fontsize=14)
        p2.insert_text((50, 100), "Conductance is quantized as G = 2 * e^2 / h.", fontsize=11)
        doc.save(tmp_path)
        doc.close()

        reader = UniversalReader()
        extracted = reader.parse_pdf(tmp_path)

        assert extracted.page_count == 2
        assert len(extracted.bounding_boxes) >= 2
        assert any(b["page_number"] == 1 for b in extracted.bounding_boxes)
        assert any(b["page_number"] == 2 for b in extracted.bounding_boxes)
        assert len(extracted.chunks) >= 2
    finally:
        Path(tmp_path).unlink(missing_ok=True)

@pytest.mark.asyncio
async def test_source_manager_ingest_and_deduplication(test_db_session, mock_provider):
    manager = SourceManager(test_db_session, mock_provider)
    sample_text = "Thermoelectric generators convert temperature differences directly into electrical energy."
    
    # First ingestion
    doc1 = await manager.ingest_text(sample_text, title="Thermoelectric Basics")
    assert doc1.id is not None
    assert doc1.title == "Thermoelectric Basics"

    # Second ingestion with identical text (deduplication test)
    doc2 = await manager.ingest_text(sample_text, title="Duplicate Document")
    assert doc1.id == doc2.id
    assert doc1.file_hash_sha256 == doc2.file_hash_sha256

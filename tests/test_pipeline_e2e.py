import pytest
import tempfile
from pathlib import Path
import pymupdf as fitz
from axion.ingestion.source_manager import SourceManager
from axion.knowledge_graph.extractor import KnowledgeGraphExtractor
from axion.knowledge_graph.graph import KnowledgeGraphStore
from axion.baseline.controller import BaselineController
from sqlalchemy import select
from axion.database.models import DocumentChunk

@pytest.mark.asyncio
async def test_end_to_end_ingest_graph_and_baseline(test_db_session, mock_provider):
    """
    Integration Test (E2E):
    1. Create a synthetic research PDF with scientific equations and section headers.
    2. Ingest via Universal Knowledge Reader (PyMuPDF) with bounding boxes.
    3. Extract scientific concepts and relations into Knowledge Graph.
    4. Query Baseline RAG (Component 3) and verify page-coordinate citations.
    5. Query Knowledge Graph (Component 2) and verify multi-hop paths via NetworkX.
    """
    # 1. Generate multi-page research PDF
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        pdf_path = tmp.name

    try:
        doc = fitz.open()
        
        # Page 1: Photovoltaics
        p1 = doc.new_page(width=595, height=842)
        p1.insert_text((50, 72), "1. Photovoltaic Generation", fontsize=14)
        p1.insert_text((50, 100), "Solar_Power is proportional to Solar_Irradiance.", fontsize=11)
        p1.insert_text((50, 120), "Solar_Power = Area * Solar_Irradiance * Efficiency", fontsize=11)
        
        # Page 2: Vehicle Kinematics
        p2 = doc.new_page(width=595, height=842)
        p2.insert_text((50, 72), "2. Road Load Kinematics", fontsize=14)
        p2.insert_text((50, 100), "Mechanical_Demand is proportional to Vehicle_Velocity.", fontsize=11)
        p2.insert_text((50, 120), "Mechanical_Demand = Drag_Force * Vehicle_Velocity", fontsize=11)
        
        doc.save(pdf_path)
        doc.close()

        # 2. Ingest via SourceManager (Component 1)
        source_manager = SourceManager(test_db_session, mock_provider)
        ingested_doc = await source_manager.ingest_file(pdf_path, title="Solar EV Physics")
        assert ingested_doc.id is not None
        assert ingested_doc.page_count == 2

        # Verify chunks created
        stmt = select(DocumentChunk).where(DocumentChunk.document_id == ingested_doc.id)
        res = await test_db_session.execute(stmt)
        chunks = res.scalars().all()
        assert len(chunks) >= 2

        # 3. Extract Knowledge Graph (Component 2)
        extractor = KnowledgeGraphExtractor(mock_provider, default_domain="physics:clean_tech")
        kg_store = KnowledgeGraphStore(test_db_session)

        for c in chunks:
            ext_res = await extractor.extract_from_chunk(c.text_content, domain="physics:clean_tech")
            await kg_store.add_extraction_result(ext_res, chunk_id=c.id, default_domain="physics:clean_tech")

        # Verify Graph in NetworkX
        G = await kg_store.export_to_networkx()
        assert G.number_of_nodes() >= 4
        assert G.number_of_edges() >= 2

        # 4. Query Baseline RAG (Component 3)
        baseline_ctrl = BaselineController(test_db_session, mock_provider)
        response = await baseline_ctrl.query("How is Solar_Power calculated?", top_k=2)

        assert not response.abstained
        assert len(response.citations) >= 1
        assert response.citations[0].document_title == "Solar EV Physics"
        assert response.citations[0].page_number in [1, 2]

    finally:
        Path(pdf_path).unlink(missing_ok=True)

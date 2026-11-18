import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from axion.acquisition.types import (
    SourceDocument, DocumentType, AccessStatus, AcquisitionMode,
    SearchRequest, IngestAcquiredRequest
)
from axion.acquisition.engine import InformationAcquisitionEngine
from axion.acquisition.continuous import ContinuousAcquisitionManager
from axion.core.types import EpistemicTier, TrustTier

@pytest.fixture
def sample_documents():
    return [
        SourceDocument(
            id="doc-1",
            title="Electric Motor Torque Analysis",
            content="Lorentz force induces rotational torque in armature windings.",
            authors=["Nikola Tesla"],
            source_name="arxiv",
            doi="10.1000/182",
            source_url="https://arxiv.org/abs/1000.0182",
            document_type=DocumentType.ABSTRACT,
            access_status=AccessStatus.OPEN_ACCESS,
            license="CC-BY",
            trust_tier=TrustTier.PEER_REVIEWED
        ),
        SourceDocument(
            id="doc-2",
            title="Electric Motor Torque Analysis",  # Duplicate title & DOI
            content="Lorentz force induces rotational torque in armature windings with complete equations.",
            authors=["N. Tesla"],
            source_name="crossref",
            doi="10.1000/182",
            source_url="https://doi.org/10.1000/182",
            document_type=DocumentType.PAPER,
            access_status=AccessStatus.OPEN_ACCESS,
            license="CC-BY",
            trust_tier=TrustTier.PEER_REVIEWED
        ),
        SourceDocument(
            id="doc-3",
            title="Hydraulic Flow in Elastic Tubing",
            content="Poiseuille continuum pressure drop in flexible vessels.",
            authors=["Jean Poiseuille"],
            source_name="pubmed",
            doi="10.1001/555",
            source_url="https://pubmed.ncbi.nlm.nih.gov/555/",
            document_type=DocumentType.ABSTRACT,
            access_status=AccessStatus.ABSTRACT_ONLY,
            license="Proprietary",
            trust_tier=TrustTier.PEER_REVIEWED
        )
    ]

@pytest.mark.asyncio
async def test_engine_identify_terms():
    engine = InformationAcquisitionEngine()
    terms = engine.identify_subjects_and_terms("How does an electric motor produce torque under magnetic fields?")
    assert len(terms) >= 2
    assert any("electric motor" in t for t in terms) or any("motor" in t for t in terms)

@pytest.mark.asyncio
async def test_engine_connector_selection():
    engine = InformationAcquisitionEngine()
    
    # Biomedical query selects PubMed
    bio_connectors = engine.select_connectors("photosynthesis enzyme in chloroplast cells")
    bio_names = [c.source_name for c in bio_connectors]
    assert "pubmed" in bio_names

    # Dataset query selects Hugging Face & Kaggle
    ds_connectors = engine.select_connectors("machine learning benchmark dataset for classification")
    ds_names = [c.source_name for c in ds_connectors]
    assert "huggingface" in ds_names or "kaggle" in ds_names

    # Explicit source selection
    custom_connectors = engine.select_connectors("physics", requested_sources=["arxiv", "crossref"])
    assert len(custom_connectors) == 2
    assert set(c.source_name for c in custom_connectors) == {"arxiv", "crossref"}

@pytest.mark.asyncio
async def test_engine_deduplication(sample_documents):
    engine = InformationAcquisitionEngine()
    assert len(sample_documents) == 3

    deduped = engine.deduplicate(sample_documents)
    # doc-1 and doc-2 share the exact DOI 10.1000/182 and title
    assert len(deduped) == 2
    merged = next(d for d in deduped if d.doi == "10.1000/182")
    assert "complete equations" in merged.content
    assert merged.license == "CC-BY"

@pytest.mark.asyncio
async def test_engine_relevance_ranking(sample_documents):
    engine = InformationAcquisitionEngine()
    query = "electric motor torque"
    ranked = engine.rank_relevance(query, sample_documents)

    # First result should be the electric motor document
    assert "Electric Motor" in ranked[0].title
    assert ranked[0].relevance_score > ranked[-1].relevance_score

@pytest.mark.asyncio
async def test_engine_search_multi_source():
    engine = InformationAcquisitionEngine()
    mock_c1 = MagicMock()
    mock_c1.source_name = "src1"
    mock_c1.source_type = "papers"
    mock_c1.search = AsyncMock(return_value=[
        SourceDocument(
            title="Paper A on Thermodynamics",
            content="Heat conduction laws and entropy.",
            source_name="src1"
        )
    ])

    mock_c2 = MagicMock()
    mock_c2.source_name = "src2"
    mock_c2.source_type = "datasets"
    mock_c2.search = AsyncMock(return_value=[
        SourceDocument(
            title="Dataset B on Thermal Transport",
            content="Measurements of heat flux in watts.",
            source_name="src2",
            document_type=DocumentType.DATASET
        )
    ])

    engine.connectors = {"src1": mock_c1, "src2": mock_c2}

    req = SearchRequest(query="thermal heat conduction", max_results_per_source=5)
    resp = await engine.search(req)

    assert resp.total_discovered == 2
    assert resp.total_deduplicated == 2
    assert len(resp.documents) == 2
    assert set(resp.sources_queried) == {"src1", "src2"}

@pytest.mark.asyncio
async def test_engine_failure_resilience():
    engine = InformationAcquisitionEngine()
    # Connector 1 throws an unhandled network error
    failing_c = MagicMock()
    failing_c.source_name = "failing"
    failing_c.source_type = "papers"
    failing_c.search = AsyncMock(side_effect=Exception("API Connection Timeout 504"))

    # Connector 2 succeeds
    working_c = MagicMock()
    working_c.source_name = "working"
    working_c.source_type = "papers"
    working_c.search = AsyncMock(return_value=[
        SourceDocument(
            title="Robust Scientific Finding",
            content="Verified experimental evidence.",
            source_name="working"
        )
    ])

    engine.connectors = {"failing": failing_c, "working": working_c}

    req = SearchRequest(query="scientific finding", max_results_per_source=5)
    resp = await engine.search(req)

    # Failing connector was gracefully caught; working connector results returned
    assert resp.total_discovered == 1
    assert len(resp.documents) == 1
    assert resp.documents[0].source_name == "working"

@pytest.mark.asyncio
async def test_engine_ingest_into_knowledge_system(test_db_session, sample_documents):
    engine = InformationAcquisitionEngine(db_session=test_db_session)
    ingest_res = await engine.ingest_documents(
        documents=[sample_documents[0]],
        session=test_db_session,
        extract_knowledge_graph=True
    )

    assert ingest_res.ingested_count == 1
    assert len(ingest_res.document_ids) == 1
    assert ingest_res.total_chunks_created >= 1

    # Verify that the document was persisted and has Fact Documented tier (not validated finding)
    from axion.database.models import Document
    from sqlalchemy import select
    stmt = select(Document).where(Document.id == ingest_res.document_ids[0])
    res = await test_db_session.execute(stmt)
    doc = res.scalars().first()
    assert doc is not None
    assert doc.title == "Electric Motor Torque Analysis"
    assert doc.doc_metadata.get("epistemic_tier") == EpistemicTier.FACT_DOCUMENTED.value

@pytest.mark.asyncio
async def test_continuous_acquisition_manager(tmp_path):
    state_file = tmp_path / "test_continuous_state.json"
    mgr = ContinuousAcquisitionManager(persistence_file=str(state_file))

    # Add subscription
    cfg = mgr.add_subscription(
        source_name="mock_source",
        search_query="quantum tunneling",
        poll_interval_seconds=1800
    )
    assert cfg.config_id in mgr.configs
    assert cfg.search_query == "quantum tunneling"

    # Mock engine search
    engine = InformationAcquisitionEngine()
    mock_c = MagicMock()
    mock_c.source_name = "mock_source"
    mock_c.source_type = "papers"
    mock_c.search = AsyncMock(return_value=[
        SourceDocument(
            id="doc-new-1",
            title="Discovery of Resonant Tunneling",
            content="Evidence for resonant quantum tunneling.",
            source_name="mock_source",
            doi="10.1000/tunnel.1"
        )
    ])
    engine.connectors = {"mock_source": mock_c}

    # First poll: discovers 1 new document
    poll_1 = await mgr.poll_subscription(cfg.config_id, engine=engine, auto_ingest=False)
    assert poll_1["new_documents_count"] == 1

    # Second poll with same results: 0 new documents (duplicate prevention works!)
    poll_2 = await mgr.poll_subscription(cfg.config_id, engine=engine, auto_ingest=False)
    assert poll_2["new_documents_count"] == 0

    # Persistence verification
    mgr2 = ContinuousAcquisitionManager(persistence_file=str(state_file))
    assert cfg.config_id in mgr2.configs
    assert len(mgr2.configs[cfg.config_id].seen_identifiers) == 1

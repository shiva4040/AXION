import pytest
import os
from typing import List
from httpx import AsyncClient, ASGITransport
from axion.api.main import app
from axion.acquisition.engine import InformationAcquisitionEngine
from axion.acquisition.types import (
    SearchRequest, SourceDocument, DocumentType, AccessStatus
)
from axion.acquisition.accumulation import KnowledgeAccumulator
from axion.acquisition.connectors import (
    ArxivConnector, CrossrefConnector, PubMedConnector, OpenAlexConnector,
    GoogleScholarConnector, NASAADSConnector, InspireHEPConnector,
    WebOfScienceConnector, InspecConnector, AmericanJournalOfPhysicsConnector,
    ProQuestConnector, SmithsonianConnector
)
from axion.pipeline.stage01_question import ScientificQuestionProcessor
from axion.pipeline.stage02_acquisition import KnowledgeAcquisitionCoordinator
from axion.core.provider import MockProvider

@pytest.mark.asyncio
async def test_stage02_all_connectors_registered():
    """Verifies that all 16 target scholarly connectors are properly initialized."""
    engine = InformationAcquisitionEngine()
    sources = engine.list_sources()

    required_sources = [
        "arxiv", "crossref", "pubmed", "openalex", "huggingface", "kaggle",
        "web_search", "local_upload", "google_scholar", "nasa_ads",
        "inspire_hep", "web_of_science", "inspec", "ajp", "proquest", "smithsonian"
    ]
    for s in required_sources:
        assert s in sources, f"Missing required connector '{s}' in InformationAcquisitionEngine"
    assert len(sources) >= 16

@pytest.mark.asyncio
async def test_stage02_sources_health_and_auth_status():
    """Verifies operational health check and authentic licensing/auth inspection across connectors."""
    engine = InformationAcquisitionEngine()
    health_statuses = await engine.get_all_sources_health()
    assert len(health_statuses) >= 16

    status_map = {s.source_name: s for s in health_statuses}

    # Open Access connectors must be available
    assert status_map["crossref"].is_available is True
    assert status_map["openalex"].is_available is True
    assert status_map["inspire_hep"].is_available is True
    assert status_map["ajp"].is_available is True

    # Credential-gated connectors must report requires_auth=True
    assert status_map["nasa_ads"].requires_auth is True
    assert status_map["web_of_science"].requires_auth is True
    assert status_map["inspec"].requires_auth is True
    assert status_map["proquest"].requires_auth is True
    assert status_map["google_scholar"].requires_auth is True

@pytest.mark.asyncio
async def test_stage02_inspire_hep_live_search():
    """Tests live retrieval from CERN / DESY / SLAC INSPIRE-HEP open access API."""
    connector = InspireHEPConnector()
    results = await connector.search(query="higgs boson mass", limit=3)
    assert len(results) > 0, "INSPIRE-HEP live query returned 0 results"
    doc = results[0]
    assert doc.title is not None and len(doc.title) > 0
    assert doc.source_name == "inspire_hep"
    assert doc.access_status in [AccessStatus.OPEN_ACCESS, AccessStatus.ABSTRACT_ONLY]
    assert len(doc.authors) > 0 or doc.metadata.get("arxiv_id") is not None

@pytest.mark.asyncio
async def test_stage02_american_journal_of_physics_live_search():
    """Tests live retrieval from American Journal of Physics (AIP) via Crossref federation."""
    connector = AmericanJournalOfPhysicsConnector()
    results = await connector.search(query="mechanics pendulum", limit=3)
    assert len(results) > 0, "AJP live query returned 0 results"
    doc = results[0]
    assert doc.source_name == "ajp"
    assert "American Journal of Physics" in doc.metadata.get("journal", "")
    assert doc.doi is not None and "10.1119" in doc.doi

@pytest.mark.asyncio
async def test_stage02_deduplication_and_ranking():
    """Verifies multi-source deduplication and relevance scoring."""
    engine = InformationAcquisitionEngine()

    docs = [
        SourceDocument(
            title="Fluid Dynamics of Hagen-Poiseuille Transport",
            content="Detailed flow characteristics in circular pipes with laminar flow.",
            source_name="arxiv",
            doi="10.1000/182",
            relevance_score=0.5
        ),
        SourceDocument(
            title="Fluid Dynamics of Hagen-Poiseuille Transport",
            content="Detailed flow characteristics in circular pipes with laminar flow and full text proofs.",
            source_name="crossref",
            doi="10.1000/182", # Same DOI -> should be merged
            relevance_score=0.4,
            is_full_text=True
        ),
        SourceDocument(
            title="Photovoltaic Solar Cell Bandgap Limits",
            content="Shockley-Queisser limit of silicon solar cells.",
            source_name="openalex",
            doi="10.1000/183",
            relevance_score=0.7
        )
    ]

    deduped = engine.deduplicate(docs)
    assert len(deduped) == 2
    merged_poiseuille = [d for d in deduped if d.doi == "10.1000/182"][0]
    assert merged_poiseuille.is_full_text is True

    ranked = engine.rank_relevance("Hagen-Poiseuille fluid", deduped)
    assert ranked[0].doi == "10.1000/182"
    assert ranked[0].relevance_score > ranked[1].relevance_score

@pytest.mark.asyncio
async def test_stage02_knowledge_accumulator_equations_and_claims():
    """Verifies structured extraction of equations, variables, claims, and limits."""
    accumulator = KnowledgeAccumulator()

    doc = SourceDocument(
        title="Vehicle Aerodynamics and Surface Solar Radiation",
        content=(
            "The aerodynamic drag force is governed by F_drag = 0.5 * rho * v^2 * C_d * A, "
            "assuming steady-state conditions and incompressible flow. "
            "Under the condition that Reynolds number Re < 2300, laminar airflow is maintained. "
            "We find that aerodynamic drag power loss increases with velocity cubed. "
            "Conversely, electrical power dissipated in internal wiring follows P = I^2 * R."
        ),
        source_name="arxiv",
        doi="10.1103/PhysRev.Vehicle.01"
    )

    items = await accumulator.accumulate_document(doc)
    assert len(items) >= 4

    types_found = {it.item_type for it in items}
    assert "equation" in types_found
    assert "claim" in types_found
    assert "assumption" in types_found
    assert "boundary_condition" in types_found

    # Check equation and variable extraction
    eq_items = [it for it in items if it.item_type == "equation"]
    assert any("F_drag" in eq.content or "P = I^2 * R" in eq.content for eq in eq_items)
    drag_eq = [it for it in eq_items if "F_drag" in it.content][0]
    assert "rho" in drag_eq.variables or "v" in drag_eq.variables or "A" in drag_eq.variables

    # Check assumption and boundary condition
    asm_items = [it for it in items if it.item_type == "assumption"]
    assert any("steady-state" in a.content.lower() or "incompressible" in a.content.lower() for a in asm_items)

    bc_items = [it for it in items if it.item_type == "boundary_condition"]
    assert any("re" in b.content.lower() or "<" in b.content for b in bc_items)

@pytest.mark.asyncio
async def test_stage02_contradiction_detection():
    """Verifies that opposing empirical assertions on identical variables are flagged."""
    accumulator = KnowledgeAccumulator()

    doc1 = SourceDocument(
        title="Thermal Conduction Study A",
        content="We find that thermal conductivity increases with temperature T in silicon semiconductors.",
        source_name="crossref"
    )
    doc2 = SourceDocument(
        title="Thermal Conduction Study B",
        content="Experimental results show that thermal conductivity decreases with temperature T in silicon semiconductors.",
        source_name="ajp"
    )

    await accumulator.accumulate_document(doc1)
    await accumulator.accumulate_document(doc2)

    stats = await accumulator.get_statistics()
    assert stats["total_contradictions_detected"] >= 1

    all_items = await accumulator.get_items()
    contradicted = [it for it in all_items if it["is_contradicted"]]
    assert len(contradicted) >= 2
    assert "Directional contradiction" in contradicted[0]["contradiction_notes"]

@pytest.mark.asyncio
async def test_stage02_cross_domain_connection_bridges():
    """Verifies automatic construction of interdisciplinary bridge links."""
    accumulator = KnowledgeAccumulator()

    # Document 1: Aerodynamics / Fluid dynamics
    doc1 = SourceDocument(
        title="High-Speed Rail Vehicle Aerodynamics",
        content="Aerodynamic drag force F_drag = 0.5 * rho * v^2 * C_d * A causes vehicle power dissipation to increase.",
        source_name="arxiv"
    )

    # Document 2: Solar Photovoltaics
    doc2 = SourceDocument(
        title="Rooftop Photovoltaic Cell Efficiency",
        content="Solar array power generation P = Area * G * eta provides electric energy for auxiliary propulsion.",
        source_name="openalex"
    )

    await accumulator.accumulate_document(doc1)
    await accumulator.accumulate_document(doc2)

    bridges = await accumulator.get_connections()
    assert len(bridges) >= 1
    br = bridges[0]
    assert br["source_domain"] != br["target_domain"]
    assert "power" in br["shared_concept"].lower() or "energy" in br["shared_concept"].lower()

@pytest.mark.asyncio
async def test_stage02_api_dashboard_endpoints():
    """Tests the FastAPI routes for Sources, Statistics, Collection, and Accumulation."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Sources endpoint
        res_sources = await client.get("/api/v1/acquisition/sources")
        assert res_sources.status_code == 200
        sources_data = res_sources.json()
        assert len(sources_data) >= 16

        # 2. Statistics endpoint
        res_stats = await client.get("/api/v1/acquisition/statistics")
        assert res_stats.status_code == 200
        stats_data = res_stats.json()
        assert "total_documents_retrieved" in stats_data
        assert "total_equations" in stats_data
        assert "total_claims" in stats_data
        assert "domain_distribution" in stats_data

        # 3. Collection endpoint
        res_coll = await client.get("/api/v1/acquisition/collection")
        assert res_coll.status_code == 200
        assert isinstance(res_coll.json(), list)

        # 4. Accumulation endpoint
        res_accum = await client.get("/api/v1/acquisition/accumulation")
        assert res_accum.status_code == 200
        accum_data = res_accum.json()
        assert "items" in accum_data
        assert "bridges" in accum_data

        # 5. History endpoint
        res_hist = await client.get("/api/v1/acquisition/history")
        assert res_hist.status_code == 200
        assert isinstance(res_hist.json(), list)

@pytest.mark.asyncio
async def test_stage01_to_stage02_pipeline_coordination():
    """Verifies that Stage 01 QuestionSpec flows smoothly into Stage 02 Coordinator."""
    q_proc = ScientificQuestionProcessor(provider=MockProvider())
    question = "How does aerodynamic drag counteract the electrical power generated by a rooftop photovoltaic array at cruising velocity v = 120 km/h?"
    q_spec = await q_proc.process_question(question)

    engine = InformationAcquisitionEngine()
    coordinator = KnowledgeAcquisitionCoordinator(acquisition_engine=engine)

    payload = await coordinator.acquire_knowledge(
        question_spec=q_spec,
        top_k=3,
        enable_external=True
    )

    assert payload.query_id == q_spec.query_id
    assert "external_acquisition_engine" in payload.sources_queried
    assert len(payload.retrieved_chunks) > 0
    first_chunk = payload.retrieved_chunks[0]
    assert first_chunk.provenance is not None
    assert first_chunk.provenance.document_id is not None
    assert first_chunk.text_content is not None
    assert "accumulated_knowledge_count" in payload.metadata

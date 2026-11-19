import pytest
from unittest.mock import AsyncMock, MagicMock
from axion.core.types import BoundingBox, EpistemicTier, ProvenancePointer
from axion.pipeline.stage01_question import MinimalQuestionProcessor
from axion.pipeline.stage02_acquisition import KnowledgeAcquisitionCoordinator
from axion.pipeline.types import QuestionIntent, QuestionSpec
from axion.knowledge_memory.memory import ValidatedKnowledgeMemory
from axion.knowledge_memory.types import KnowledgeStatus, ValidatedFinding


@pytest.mark.asyncio
async def test_stage01_intent_and_domain_classification():
    """Verify Stage 01 correctly detects domain tags and intent."""
    processor = MinimalQuestionProcessor()

    # 1. Calculation query with parameters
    q1 = "Calculate the electrical voltage when current I = 5 A and resistance R = 10 Ohm in laminar flow"
    spec1 = await processor.process_question(q1)
    assert spec1.intent == QuestionIntent.QUANTITATIVE_CALCULATION
    assert "physics:electromagnetism" in spec1.domain_tags
    assert "flow_regime" in spec1.identified_constraints
    assert spec1.identified_constraints["flow_regime"] == "laminar"
    assert "I" in spec1.declared_parameters or "R" in spec1.declared_parameters

    # 2. Cross-domain transfer query
    q2 = "Is there an analog of electrical resistance in fluid pipe flow?"
    spec2 = await processor.process_question(q2)
    assert spec2.intent == QuestionIntent.ANALOGICAL_TRANSFER
    assert "physics:electromagnetism" in spec2.domain_tags
    assert "fluid_mechanics:pipe_flow" in spec2.domain_tags

    # 3. Feasibility / explanation query
    q3 = "What is the Carnot efficiency limit of a heat engine in thermodynamics?"
    spec3 = await processor.process_question(q3)
    assert spec3.intent in [QuestionIntent.FEASIBILITY_CHECK, QuestionIntent.EXPLANATION, QuestionIntent.QUANTITATIVE_CALCULATION]
    assert "physics:thermodynamics" in spec3.domain_tags
    assert "efficiency" in spec3.extracted_concepts or "carnot" in spec3.extracted_concepts


@pytest.mark.asyncio
async def test_stage02_acquisition_with_attached_document(test_db_session):
    """Verify Stage 02 retrieves attached document chunks with provenance."""
    import tempfile
    from pathlib import Path
    import pymupdf as fitz
    from axion.ingestion.source_manager import SourceManager
    from axion.core.provider import MockProvider

    # Create dummy PDF
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        pdf_path = tmp.name

    try:
        doc = fitz.open()
        p1 = doc.new_page(width=595, height=842)
        p1.insert_text((50, 72), "1. Aerodynamic Drag Forces", fontsize=14)
        p1.insert_text((50, 100), "Drag_Force is proportional to Drag_Coefficient.", fontsize=11)
        doc.save(pdf_path)
        doc.close()

        # Ingest document
        provider = MockProvider()
        source_manager = SourceManager(test_db_session, provider)
        ingested = await source_manager.ingest_file(pdf_path, title="Aerodynamics Paper")

        coordinator = KnowledgeAcquisitionCoordinator(
            db_session=test_db_session,
            provider=provider,
        )

        spec = QuestionSpec(
            raw_query="How is Drag_Force determined?",
            document_id=ingested.id,
            extracted_concepts=["drag_force", "aerodynamics"],
        )

        payload = await coordinator.acquire_knowledge(spec, top_k=5)
        assert payload.total_retrieved >= 1
        assert len(payload.retrieved_chunks) >= 1
        first_chunk = payload.retrieved_chunks[0]
        assert first_chunk.document_id == ingested.id
        assert first_chunk.provenance.page_number == 1
        assert "Drag_Force" in first_chunk.text_content
        assert "local_attached_document" in payload.sources_queried
        assert payload.acquisition_latency_ms >= 0.0

    finally:
        Path(pdf_path).unlink(missing_ok=True)


@pytest.mark.asyncio
async def test_stage02_acquisition_with_memory_findings():
    """Verify Stage 02 retrieves candidate findings from ValidatedKnowledgeMemory."""
    memory = ValidatedKnowledgeMemory()
    finding = ValidatedFinding(
        finding_id="FIND-TEST-001",
        version=1,
        title="Thermal Conduction in Silicon",
        statement="Thermal conductivity of monocrystalline silicon degrades at elevated temperature.",
        status=KnowledgeStatus.VALID,
        hypothesis_id="hypo-1",
        epistemic_tier=EpistemicTier.FINDING_VALIDATED,
        supporting_experiment_ids=["exp-1"],
        source_provenance=[
            ProvenancePointer(
                document_id="doc-silicon",
                chunk_id="chunk-1",
                page_number=3,
                extracted_snippet="Silicon thermal conductivity is temperature dependent.",
            )
        ],
        active_assumptions=["crystal_purity >= 99.9%"],
        applicable_conditions=["T in [300K, 600K]"],
        created_at="2026-11-19T00:00:00Z",
        updated_at="2026-11-19T00:00:00Z",
    )
    memory._findings[finding.finding_id] = finding

    coordinator = KnowledgeAcquisitionCoordinator(memory=memory)
    spec = QuestionSpec(
        raw_query="How does silicon behave under thermal conduction?",
        domain_tags=["physics:thermodynamics"],
        extracted_concepts=["silicon", "thermal", "conduction"],
    )

    payload = await coordinator.acquire_knowledge(spec, top_k=5)
    assert len(payload.candidate_memory_items) == 1
    assert payload.candidate_memory_items[0]["finding_id"] == "FIND-TEST-001"
    assert "validated_knowledge_memory" in payload.sources_queried

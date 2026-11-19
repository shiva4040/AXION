import pytest
from axion.core.provider import MockProvider
from axion.core.types import BoundingBox, EpistemicTier, ProvenancePointer
from axion.knowledge_memory.memory import ValidatedKnowledgeMemory
from axion.pipeline.coordinator import PipelineCoordinator
from axion.pipeline.types import (
    AcquiredChunk,
    AcquisitionPayload,
    ExtractedClaim,
    PipelineAnswerResponse,
    QuestionSpec,
)


@pytest.mark.asyncio
async def test_wp3_full_pipeline_answerable_case():
    """
    End-to-End Test (Answerable Case):
    Query with valid primary evidence -> Stage 01 through 08 ->
    VERIFIED -> Stored in Validated Memory -> Emits structured answer.
    """
    memory = ValidatedKnowledgeMemory()
    coordinator = PipelineCoordinator(provider=MockProvider(), memory=memory)

    raw_query = "Calculate electrical power given V = 10 V and I = 2 A"
    spec = await coordinator.run_stage_01(raw_query)

    # Simulate acquired chunk with exact equation and text
    chunk_text = "Power in DC Circuits: electrical power is P = V * I for resistive components."
    bbox = BoundingBox(page_number=1, x0=10.0, y0=20.0, x1=120.0, y1=40.0)
    prov = ProvenancePointer(
        document_id="doc-elec-1",
        chunk_id="chk-1",
        page_number=1,
        bounding_box=bbox,
        extracted_snippet=chunk_text,
    )
    chunk = AcquiredChunk(
        chunk_id="chk-1",
        document_id="doc-elec-1",
        page_number=1,
        text_content=chunk_text,
        provenance=prov,
        bounding_box=bbox,
    )
    payload = AcquisitionPayload(
        query_id=spec.query_id,
        retrieved_chunks=[chunk],
        sources_queried=["local_db"],
        total_retrieved=1,
    )

    # Run through full coordinator pipeline
    claims = await coordinator.run_stage_03(payload)
    spec.declared_parameters["V"] = "10 V"
    spec.declared_parameters["I"] = "2 A"
    spec.target_variables = ["P"]
    composed = await coordinator.run_stage_04(claims, spec)
    trace = await coordinator.run_stage_05(composed)
    audit = await coordinator.run_stage_06(trace, composed, payload, spec)
    assert audit.verdict == "VERIFIED"

    # Stage 07 write-back
    stored = coordinator.run_stage_07_store(audit, trace, composed, spec)
    assert stored is not None
    assert len(memory.list_findings()) == 1

    # Stage 08 answer
    resp = await coordinator.run_stage_08(audit, trace, composed, spec, [], 12.0)
    assert not resp.is_abstained
    assert resp.verdict == "ANSWERABLE"
    assert "20 W" in resp.direct_answer
    assert len(resp.supporting_evidence) >= 1
    assert resp.supporting_evidence[0].provenance.document_id == "doc-elec-1"


@pytest.mark.asyncio
async def test_wp3_full_pipeline_unanswerable_abstention():
    """
    End-to-End Test (Unanswerable Case):
    Query with zero evidence -> Stage 06 rejects with ABSTAIN_INSUFFICIENT_EVIDENCE ->
    Stage 07 does NOT store in memory -> Stage 08 emits standardized refusal.
    """
    memory = ValidatedKnowledgeMemory()
    coordinator = PipelineCoordinator(provider=MockProvider(), memory=memory)

    resp = await coordinator.execute(
        raw_query="What is the magnetic permeability of liquid xenon at high temperature?"
    )

    assert resp.is_abstained is True
    assert "ABSTAIN" in resp.verdict
    assert "cannot answer" in resp.direct_answer.lower()
    # Memory must remain empty!
    assert len(memory.list_findings()) == 0


@pytest.mark.asyncio
async def test_wp3_full_pipeline_contradiction_rejection():
    """
    End-to-End Test (Contradiction Case):
    Competing documents assert conflicting flow regimes ->
    Stage 06 rejects with ABSTAIN_CONTRADICTORY_EVIDENCE ->
    Memory rejects write -> Stage 08 refuses with contradiction explanation.
    """
    memory = ValidatedKnowledgeMemory()
    coordinator = PipelineCoordinator(provider=MockProvider(), memory=memory)

    prov = ProvenancePointer(document_id="d1", chunk_id="c1", page_number=1, extracted_snippet="Fluid text")
    chunk = AcquiredChunk(chunk_id="c1", document_id="d1", page_number=1, text_content="Fluid text", provenance=prov)
    payload = AcquisitionPayload(query_id="q-conf", retrieved_chunks=[chunk], total_retrieved=1)

    c1 = ExtractedClaim(statement="Flow in pipe is laminar", provenance=prov)
    c2 = ExtractedClaim(statement="Flow in pipe is turbulent", provenance=prov)
    spec = QuestionSpec(raw_query="Determine flow regime")

    composed = coordinator.stage04.compose_system([c1, c2], spec)
    trace = coordinator.stage05.execute_reasoning(composed)
    audit = await coordinator.run_stage_06(trace, composed, payload, spec)

    assert audit.verdict == "ABSTAIN_CONTRADICTORY_EVIDENCE"
    stored = coordinator.run_stage_07_store(audit, trace, composed, spec)
    assert stored is None
    assert len(memory.list_findings()) == 0

    resp = await coordinator.run_stage_08(audit, trace, composed, spec, [], 10.0)
    assert resp.is_abstained is True
    assert "CONTRADICTORY" in resp.verdict
    assert "contradictory" in resp.direct_answer.lower()

import pytest
from datetime import datetime
from axion.core.types import BoundingBox, EpistemicTier, ProvenancePointer
from axion.pipeline.types import (
    AcquiredChunk,
    AcquisitionPayload,
    ComposedSystem,
    ExtractedClaim,
    PipelineAnswerResponse,
    QuestionIntent,
    QuestionSpec,
    ReasoningTrace,
    StageExecutionLog,
    SupportingEvidenceItem,
    VerificationAuditReport,
)


def test_question_spec_model():
    """Verify QuestionSpec instantiation, default values, and serialization."""
    spec = QuestionSpec(
        raw_query="What is the relationship between voltage, current, and resistance in a circuit?",
        intent=QuestionIntent.EXPLANATION,
        target_variables=["voltage", "current", "resistance"],
        domain_tags=["physics:electromagnetism"],
        extracted_concepts=["voltage", "current", "resistance", "circuit"],
    )
    assert spec.query_id.startswith("q-")
    assert spec.raw_query.startswith("What is")
    assert spec.intent == QuestionIntent.EXPLANATION
    assert len(spec.target_variables) == 3
    assert "physics:electromagnetism" in spec.domain_tags
    d = spec.model_dump()
    assert d["query_id"] == spec.query_id
    assert d["intent"] == "EXPLANATION"


def test_provenance_pointer_and_acquired_chunk():
    """Verify ProvenancePointer and AcquiredChunk models with bounding box."""
    bbox = BoundingBox(page_number=1, x0=50.0, y0=100.0, x1=200.0, y1=150.0)
    prov = ProvenancePointer(
        document_id="doc-123",
        chunk_id="chunk-456",
        page_number=1,
        bounding_box=bbox,
        extracted_snippet="V = I * R is Ohm's Law.",
    )
    chunk = AcquiredChunk(
        chunk_id="chunk-456",
        document_id="doc-123",
        page_number=1,
        text_content="V = I * R is Ohm's Law in steady-state circuits.",
        similarity_score=0.95,
        source_title="Principles of Physics",
        provenance=prov,
        bounding_box=bbox,
    )
    assert chunk.provenance.document_id == "doc-123"
    assert chunk.provenance.bounding_box is not None
    assert chunk.provenance.bounding_box.x0 == 50.0
    assert chunk.similarity_score == 0.95


def test_acquisition_payload_model():
    """Verify AcquisitionPayload model aggregation."""
    prov = ProvenancePointer(
        document_id="doc-1",
        chunk_id="c-1",
        page_number=1,
        extracted_snippet="Sample snippet",
    )
    chunk = AcquiredChunk(
        chunk_id="c-1",
        document_id="doc-1",
        page_number=1,
        text_content="Sample text",
        provenance=prov,
    )
    payload = AcquisitionPayload(
        query_id="q-test",
        retrieved_chunks=[chunk],
        candidate_memory_items=[{"finding_id": "FIND-001", "statement": "Energy is conserved."}],
        sources_queried=["local_db", "memory"],
        total_retrieved=2,
        acquisition_latency_ms=12.5,
    )
    assert payload.query_id == "q-test"
    assert len(payload.retrieved_chunks) == 1
    assert len(payload.candidate_memory_items) == 1
    assert payload.total_retrieved == 2
    assert payload.acquisition_latency_ms == 12.5


def test_extracted_claim_and_composed_system():
    """Verify ExtractedClaim and ComposedSystem data models."""
    prov = ProvenancePointer(
        document_id="doc-1",
        chunk_id="c-1",
        page_number=2,
        extracted_snippet="P = V * I for DC circuits.",
    )
    claim = ExtractedClaim(
        statement="Power equals voltage multiplied by current.",
        epistemic_tier=EpistemicTier.FACT_DOCUMENTED,
        conditions=["DC circuit", "steady state"],
        equations=["P = V * I"],
        variables=["P", "V", "I"],
        provenance=prov,
    )
    composed = ComposedSystem(
        unified_variables={"P": "power", "V": "voltage", "I": "current"},
        active_assumptions=["DC circuit"],
        coupled_equations=["P = V * I"],
        claims=[claim],
        boundary_limits={"V": "10 V"},
        participating_domains=["physics:electromagnetism"],
    )
    assert composed.system_id.startswith("sys-")
    assert len(composed.claims) == 1
    assert composed.claims[0].epistemic_tier == EpistemicTier.FACT_DOCUMENTED
    assert "DC circuit" in composed.active_assumptions


def test_reasoning_trace_and_verification_report():
    """Verify ReasoningTrace and VerificationAuditReport models."""
    trace = ReasoningTrace(
        steps=["Step 1: Substitute V = 10 and I = 2 into P = V * I", "Step 2: P = 20 W"],
        calculated_values={"P": "20 W"},
        inferred_premises=["V = 10 V", "I = 2 A"],
    )
    assert trace.trace_id.startswith("trc-")
    assert len(trace.steps) == 2
    assert trace.calculated_values["P"] == "20 W"

    audit = VerificationAuditReport(
        verdict="VERIFIED",
        quotation_checks_passed=True,
        contradiction_detected=False,
        applicability_checks_passed=True,
        audit_details={"tolerance": 1e-4},
    )
    assert audit.report_id.startswith("aud-")
    assert audit.verdict == "VERIFIED"
    assert audit.quotation_checks_passed is True


def test_pipeline_answer_response_model():
    """Verify PipelineAnswerResponse model serialization and defaults."""
    prov = ProvenancePointer(
        document_id="doc-1",
        chunk_id="c-1",
        page_number=1,
        extracted_snippet="P = 20 W was confirmed.",
    )
    log = StageExecutionLog(
        stage_number=1,
        stage_name="Question Processing",
        status="SUCCESS",
        started_at=datetime.now().isoformat(),
        duration_ms=4.2,
    )
    response = PipelineAnswerResponse(
        query_id="q-001",
        query="Calculate power when V=10V and I=2A",
        verdict="ANSWERABLE",
        direct_answer="The calculated power is 20 W.",
        supporting_evidence=[
            SupportingEvidenceItem(
                claim="P = 20 W",
                citation="Doc doc-1, Page 1",
                verbatim_quote="P = 20 W was confirmed.",
                provenance=prov,
            )
        ],
        active_assumptions=["DC circuit"],
        calculation_steps=["P = V * I = 10 * 2 = 20 W"],
        is_abstained=False,
        execution_logs=[log],
        total_latency_ms=18.4,
    )
    assert not response.is_abstained
    assert response.verdict == "ANSWERABLE"
    assert len(response.supporting_evidence) == 1
    assert len(response.execution_logs) == 1
    assert response.execution_logs[0].duration_ms == 4.2

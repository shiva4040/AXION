import pytest
from axion.core.types import ProvenancePointer
from axion.pipeline.stage08_answer import MinimalAnswerGenerator
from axion.pipeline.types import (
    ComposedSystem,
    ExtractedClaim,
    PipelineAnswerResponse,
    QuestionSpec,
    ReasoningTrace,
    StageExecutionLog,
    VerificationAuditReport,
    VerificationVerdict,
)


def test_stage08_generates_verified_answer():
    """Verify structured answer formulation with supporting citations when verified."""
    generator = MinimalAnswerGenerator()

    prov = ProvenancePointer(
        document_id="doc-physics",
        chunk_id="chk-1",
        page_number=3,
        extracted_snippet="V = I * R is Ohm's Law.",
    )
    claim = ExtractedClaim(
        statement="V = I * R is Ohm's Law.",
        provenance=prov,
    )
    system = ComposedSystem(
        claims=[claim],
        active_assumptions=["DC circuit"],
    )
    trace = ReasoningTrace(
        steps=["V = 2 A * 5 Ohm = 10 V"],
        calculated_values={"V": "10 V"},
    )
    spec = QuestionSpec(raw_query="Calculate voltage V", domain_tags=["physics:electromagnetism"])
    audit = VerificationAuditReport(verdict=VerificationVerdict.VERIFIED.value)

    resp = generator.generate_answer(
        audit_report=audit,
        reasoning_trace=trace,
        composed_system=system,
        question_spec=spec,
        execution_logs=[],
        total_latency_ms=15.0,
    )

    assert isinstance(resp, PipelineAnswerResponse)
    assert not resp.is_abstained
    assert resp.verdict == "ANSWERABLE"
    assert "10 V" in resp.direct_answer
    assert len(resp.supporting_evidence) == 1
    assert "doc-physics" in resp.supporting_evidence[0].citation
    assert resp.supporting_evidence[0].verbatim_quote == "V = I * R is Ohm's Law."
    assert "DC circuit" in resp.active_assumptions
    assert len(resp.calculation_steps) == 1


def test_stage08_generates_explicit_abstention():
    """Verify clear refusal notice when verification rejects the response."""
    generator = MinimalAnswerGenerator()

    system = ComposedSystem(active_assumptions=["laminar flow"])
    trace = ReasoningTrace()
    spec = QuestionSpec(raw_query="What is the fluid viscosity?")
    audit = VerificationAuditReport(
        verdict=VerificationVerdict.ABSTAIN_INSUFFICIENT_EVIDENCE.value,
        abstention_reason="ABSTAIN_INSUFFICIENT_EVIDENCE: Viscosity parameter not found in documents",
    )

    resp = generator.generate_answer(
        audit_report=audit,
        reasoning_trace=trace,
        composed_system=system,
        question_spec=spec,
        execution_logs=[],
        total_latency_ms=8.0,
    )

    assert isinstance(resp, PipelineAnswerResponse)
    assert resp.is_abstained is True
    assert "ABSTAIN" in resp.verdict
    assert "cannot answer" in resp.direct_answer.lower()
    assert len(resp.supporting_evidence) == 0
    assert len(resp.calculation_steps) == 0

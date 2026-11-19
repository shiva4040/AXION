import pytest
from axion.core.types import EpistemicTier, ProvenancePointer
from axion.pipeline.stage06_verification import IndependentVerificationGuard
from axion.pipeline.types import (
    AcquiredChunk,
    AcquisitionPayload,
    ComposedSystem,
    ExtractedClaim,
    QuestionSpec,
    ReasoningTrace,
    VerificationAuditReport,
    VerificationVerdict,
)


@pytest.mark.asyncio
async def test_stage06_verbatim_quotation_pass():
    """Verify that when snippet is an exact substring, quotation verification passes."""
    guard = IndependentVerificationGuard()

    chunk_text = "Ohm's Law states that V = I * R for ideal conductors."
    prov = ProvenancePointer(
        document_id="doc-1",
        chunk_id="chk-1",
        page_number=1,
        extracted_snippet="V = I * R",
    )
    claim = ExtractedClaim(
        statement="V = I * R",
        equations=["V = I * R"],
        variables=["V", "I", "R"],
        provenance=prov,
    )
    chunk = AcquiredChunk(
        chunk_id="chk-1",
        document_id="doc-1",
        page_number=1,
        text_content=chunk_text,
        provenance=prov,
    )
    payload = AcquisitionPayload(
        query_id="q1",
        retrieved_chunks=[chunk],
        total_retrieved=1,
    )
    system = ComposedSystem(
        unified_variables={"V": "voltage", "I": "current", "R": "resistance"},
        coupled_equations=["V = I * R"],
        claims=[claim],
        boundary_limits={"I": "2 A", "R": "5 Ohm"},
    )
    trace = ReasoningTrace(
        steps=["V = 2 * 5 = 10 V"],
        calculated_values={"V": "10 V"},
    )
    spec = QuestionSpec(raw_query="Calculate voltage", target_variables=["V"])

    report = await guard.verify(trace, system, payload, spec)
    assert report.verdict == VerificationVerdict.VERIFIED.value
    assert report.quotation_checks_passed is True
    assert report.contradiction_detected is False


@pytest.mark.asyncio
async def test_stage06_verbatim_quotation_mismatch_fails():
    """Verify that a hallucinated or modified quotation is rejected with INVALID_PROVENANCE."""
    guard = IndependentVerificationGuard()

    chunk_text = "Ohm's Law states that V = I * R for ideal conductors."
    # Fabricated quotation that does not exist in chunk_text
    prov = ProvenancePointer(
        document_id="doc-1",
        chunk_id="chk-1",
        page_number=1,
        extracted_snippet="V = I * R * 1000 with infinite power",
    )
    claim = ExtractedClaim(
        statement="Modified statement",
        provenance=prov,
    )
    chunk = AcquiredChunk(
        chunk_id="chk-1",
        document_id="doc-1",
        page_number=1,
        text_content=chunk_text,
        provenance=prov,
    )
    payload = AcquisitionPayload(
        query_id="q2",
        retrieved_chunks=[chunk],
        total_retrieved=1,
    )
    system = ComposedSystem(claims=[claim])
    trace = ReasoningTrace()
    spec = QuestionSpec(raw_query="Test query")

    report = await guard.verify(trace, system, payload, spec)
    assert report.verdict == VerificationVerdict.INVALID_PROVENANCE.value
    assert report.quotation_checks_passed is False
    assert "INVALID_PROVENANCE" in report.abstention_reason


@pytest.mark.asyncio
async def test_stage06_contradiction_detection():
    """Verify that contradictory regimes trigger ABSTAIN_CONTRADICTORY_EVIDENCE."""
    guard = IndependentVerificationGuard()

    prov = ProvenancePointer(document_id="d", chunk_id="c", page_number=1, extracted_snippet="Flow text")
    c1 = ExtractedClaim(statement="Fluid flow is laminar in pipe section A", provenance=prov)
    c2 = ExtractedClaim(statement="Fluid flow is turbulent in pipe section A", provenance=prov)
    chunk = AcquiredChunk(chunk_id="c", document_id="d", page_number=1, text_content="Flow text", provenance=prov)

    payload = AcquisitionPayload(query_id="q3", retrieved_chunks=[chunk], total_retrieved=1)
    system = ComposedSystem(
        claims=[c1, c2],
        boundary_limits={"_conflicts": ["Conflicting regimes: laminar vs turbulent"]},
    )
    trace = ReasoningTrace()
    spec = QuestionSpec(raw_query="Analyze fluid regime")

    report = await guard.verify(trace, system, payload, spec)
    assert report.verdict == VerificationVerdict.ABSTAIN_CONTRADICTORY_EVIDENCE.value
    assert report.contradiction_detected is True
    assert report.abstention_reason == "ABSTAIN_CONTRADICTORY_EVIDENCE"


@pytest.mark.asyncio
async def test_stage06_insufficient_evidence_abstention():
    """Verify that empty retrieval triggers ABSTAIN_INSUFFICIENT_EVIDENCE."""
    guard = IndependentVerificationGuard()

    payload = AcquisitionPayload(query_id="q4", retrieved_chunks=[], total_retrieved=0)
    system = ComposedSystem()
    trace = ReasoningTrace()
    spec = QuestionSpec(raw_query="What is dark matter?")

    report = await guard.verify(trace, system, payload, spec)
    assert report.verdict == VerificationVerdict.ABSTAIN_INSUFFICIENT_EVIDENCE.value
    assert report.abstention_reason == "ABSTAIN_INSUFFICIENT_EVIDENCE"

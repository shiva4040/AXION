import pytest
from axion.core.types import EpistemicTier, ProvenancePointer
from axion.knowledge_memory.memory import ValidatedKnowledgeMemory
from axion.knowledge_memory.types import KnowledgeStatus
from axion.pipeline.stage07_memory import VerifiedMemoryManager
from axion.pipeline.types import (
    ComposedSystem,
    ExtractedClaim,
    QuestionSpec,
    ReasoningTrace,
    VerificationAuditReport,
    VerificationVerdict,
)


def test_stage07_stores_only_verified_findings():
    """Verify that unverified, abstained, or rejected conclusions are rejected from memory."""
    memory = ValidatedKnowledgeMemory()
    manager = VerifiedMemoryManager(memory=memory)

    prov = ProvenancePointer(document_id="d1", chunk_id="c1", page_number=1, extracted_snippet="E = mc^2")
    claim = ExtractedClaim(statement="E = mc^2", provenance=prov)
    system = ComposedSystem(claims=[claim])
    trace = ReasoningTrace(steps=["E = 100 J"], calculated_values={"E": "100 J"})
    spec = QuestionSpec(raw_query="Calculate energy", target_variables=["E"])

    # 1. Unverified audit report -> MUST return None and store nothing
    bad_audit = VerificationAuditReport(
        verdict=VerificationVerdict.ABSTAIN_INSUFFICIENT_EVIDENCE.value,
        abstention_reason="Missing mass parameter",
    )
    result1 = manager.store_verified_finding(bad_audit, trace, system, spec)
    assert result1 is None
    assert len(memory.list_findings()) == 0

    # 2. Verified audit report -> MUST store and return ValidatedFinding
    good_audit = VerificationAuditReport(
        verdict=VerificationVerdict.VERIFIED.value,
    )
    result2 = manager.store_verified_finding(good_audit, trace, system, spec)
    assert result2 is not None
    assert result2.finding_id.startswith("FIND-AUTOGEN-")
    assert result2.epistemic_tier == EpistemicTier.FINDING_VALIDATED
    assert len(memory.list_findings()) == 1


def test_stage07_duplicate_detection():
    """Verify that duplicate verified findings are detected and not duplicated in memory."""
    memory = ValidatedKnowledgeMemory()
    manager = VerifiedMemoryManager(memory=memory)

    prov = ProvenancePointer(document_id="d1", chunk_id="c1", page_number=1, extracted_snippet="V = I * R")
    claim = ExtractedClaim(statement="V = I * R", provenance=prov)
    system = ComposedSystem(claims=[claim])
    trace = ReasoningTrace(calculated_values={"V": "10 V"})
    spec = QuestionSpec(raw_query="Calculate voltage", target_variables=["V"])
    audit = VerificationAuditReport(verdict=VerificationVerdict.VERIFIED.value)

    res1 = manager.store_verified_finding(audit, trace, system, spec)
    res2 = manager.store_verified_finding(audit, trace, system, spec)

    assert res1.finding_id == res2.finding_id
    assert len(memory.list_findings()) == 1


def test_stage07_candidate_memory_reading():
    """Verify that candidate findings matching query concepts/domains are retrieved."""
    memory = ValidatedKnowledgeMemory()
    manager = VerifiedMemoryManager(memory=memory)

    prov = ProvenancePointer(document_id="d1", chunk_id="c1", page_number=1, extracted_snippet="P = V * I")
    claim = ExtractedClaim(statement="P = V * I", provenance=prov)
    system = ComposedSystem(claims=[claim])
    trace = ReasoningTrace(calculated_values={"P": "50 W"})
    spec = QuestionSpec(raw_query="Calculate electrical power", domain_tags=["physics:electromagnetism"], target_variables=["P"])
    audit = VerificationAuditReport(verdict=VerificationVerdict.VERIFIED.value)

    manager.store_verified_finding(audit, trace, system, spec)

    # Now read candidate findings
    read_spec = QuestionSpec(
        raw_query="What is the electrical power?",
        domain_tags=["physics:electromagnetism"],
        extracted_concepts=["electrical", "power"],
    )
    candidates = manager.read_candidate_findings(read_spec)
    assert len(candidates) == 1
    assert candidates[0]["epistemic_tier"] == EpistemicTier.FINDING_VALIDATED.value

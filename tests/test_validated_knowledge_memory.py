import pytest
from axion.core.types import EpistemicTier, ProvenancePointer
from axion.hypothesis_tester.types import (
    ExecutionMetadata,
    ExperimentRecord,
    ExperimentType,
    ExperimentVerdict,
)
from axion.knowledge_memory.types import (
    KnowledgeStatus,
    ValidatedFinding,
)
from axion.knowledge_memory.memory import (
    FindingNotFoundError,
    InvalidPromotionError,
    ValidatedKnowledgeMemory,
)

@pytest.fixture
def memory():
    return ValidatedKnowledgeMemory()

@pytest.fixture
def supported_experiment():
    return ExperimentRecord(
        experiment_id="exp-supp-001",
        hypothesis_id="hyp-001",
        method=ExperimentType.STATISTICAL_TEST,
        input_data_summary="Passed regression test",
        expected_prediction="V = I * R",
        verdict=ExperimentVerdict.SUPPORTED,
        confidence=0.95,
        execution_metadata=ExecutionMetadata(runtime_ms=1.5),
    )

@pytest.fixture
def unsupported_experiment():
    return ExperimentRecord(
        experiment_id="exp-fail-001",
        hypothesis_id="hyp-002",
        method=ExperimentType.STATISTICAL_TEST,
        input_data_summary="Failed regression test",
        expected_prediction="V = I * R",
        verdict=ExperimentVerdict.NOT_SUPPORTED,
        confidence=0.95,
        failure_analysis="R^2 < 0.50",
        execution_metadata=ExecutionMetadata(runtime_ms=1.2),
    )

def test_store_validated_finding_success(memory, supported_experiment):
    finding = ValidatedFinding(
        finding_id="fnd-001",
        title="Ohmic Linear Transport",
        statement="Electric potential drops linearly with current.",
        hypothesis_id="hyp-001",
        source_provenance=[ProvenancePointer(document_id="doc1", chunk_id="chk1", page_number=1, extracted_snippet="V = I * R")],
        created_at="",
        updated_at="",
    )

    stored = memory.store_validated_finding(finding, supported_experiment)
    assert stored.status == KnowledgeStatus.VALID
    assert stored.epistemic_tier == EpistemicTier.FINDING_VALIDATED
    assert "exp-supp-001" in stored.supporting_experiment_ids

    # Verify audit history created
    history = memory.get_finding_history("fnd-001")
    assert len(history) == 1
    assert history[0].change_type == "CREATED"
    assert history[0].new_status == KnowledgeStatus.VALID

def test_promotion_gate_blocks_unsupported_hypothesis(memory, unsupported_experiment):
    finding = ValidatedFinding(
        finding_id="fnd-unverified",
        title="Bogus Claim",
        statement="Unsupported conjecture.",
        hypothesis_id="hyp-002",
        created_at="",
        updated_at="",
    )

    # Attempting to store with non-supported experiment MUST raise InvalidPromotionError
    with pytest.raises(InvalidPromotionError):
        memory.store_validated_finding(finding, unsupported_experiment)

    assert memory.get_finding("fnd-unverified") is None

def test_invalidation_and_audit_trail(memory, supported_experiment):
    finding = ValidatedFinding(
        finding_id="fnd-retract",
        title="Initial Finding",
        statement="Statement to be retracted.",
        hypothesis_id="hyp-001",
        created_at="",
        updated_at="",
    )
    memory.store_validated_finding(finding, supported_experiment)

    invalidated, impact = memory.invalidate_finding("fnd-retract", reason="Counterevidence showed non-linearity at high current.")
    assert invalidated.status == KnowledgeStatus.INVALIDATED
    assert invalidated.version == 2
    assert "Counterevidence" in invalidated.invalidation_reason

    # Audit history should contain CREATED and INVALIDATED records
    history = memory.get_finding_history("fnd-retract")
    assert len(history) == 2
    assert history[1].change_type == "INVALIDATED"
    assert history[1].new_status == KnowledgeStatus.INVALIDATED

def test_superseding_finding(memory, supported_experiment):
    old_finding = ValidatedFinding(
        finding_id="fnd-v1",
        title="Ohm's Law (Scalar)",
        statement="Scalar resistance model V = I * R.",
        hypothesis_id="hyp-001",
        created_at="",
        updated_at="",
    )
    memory.store_validated_finding(old_finding, supported_experiment)

    new_finding = ValidatedFinding(
        finding_id="fnd-v2",
        title="Ohm's Law (Tensor)",
        statement="Full tensor conductivity J = sigma * E.",
        hypothesis_id="hyp-001-tensor",
        created_at="",
        updated_at="",
    )

    old_res, new_res, impact = memory.supersede_finding(
        old_finding_id="fnd-v1",
        new_finding=new_finding,
        reason="Upgraded from scalar to full 3D tensor representation.",
        new_experiment_record=supported_experiment,
    )

    assert old_res.status == KnowledgeStatus.SUPERSEDED
    assert old_res.superseded_by_id == "fnd-v2"
    assert new_res.status == KnowledgeStatus.VALID
    assert new_res.finding_id == "fnd-v2"

def test_cascading_dependency_invalidation(memory, supported_experiment):
    # Setup 3-tier dependency DAG: F1 (Base) -> F2 (Derived) -> F3 (Composite)
    f1 = ValidatedFinding(
        finding_id="fnd-base",
        title="Base Law",
        statement="Base physical relation.",
        hypothesis_id="hyp-base",
        created_at="",
        updated_at="",
    )
    f2 = ValidatedFinding(
        finding_id="fnd-derived",
        title="Derived Law",
        statement="Derived from base law.",
        hypothesis_id="hyp-derived",
        derived_from_finding_ids=["fnd-base"],
        created_at="",
        updated_at="",
    )
    f3 = ValidatedFinding(
        finding_id="fnd-composite",
        title="Composite Application",
        statement="Depends on derived law.",
        hypothesis_id="hyp-composite",
        derived_from_finding_ids=["fnd-derived"],
        created_at="",
        updated_at="",
    )

    memory.store_validated_finding(f1, supported_experiment)
    memory.store_validated_finding(f2, supported_experiment)
    memory.store_validated_finding(f3, supported_experiment)

    # Invalidate F1 (Base Law)
    _, impact = memory.invalidate_finding("fnd-base", reason="Upstream experimental error discovered.")

    # Both F2 (direct) and F3 (transitive) MUST be identified in the impact report!
    assert "fnd-derived" in impact.directly_affected_finding_ids
    assert "fnd-composite" in impact.transitively_affected_finding_ids
    assert impact.total_affected_count == 2

    # Check integrity of F2 and F3
    f2_sound, f2_issues = memory.check_finding_integrity("fnd-derived")
    assert f2_sound is False
    assert any("fnd-base" in issue for issue in f2_issues)
    assert any("INVALIDATED" in issue for issue in f2_issues)

    f3_sound, f3_issues = memory.check_finding_integrity("fnd-composite")
    # F3 derives from F2, which is still marked VALID but whose prerequisite is invalidated
    # If F2 is subsequently invalidated, F3 integrity reports F2 invalidation


def test_persistent_memory_storage_across_restarts(tmp_path, supported_experiment):
    persist_file = str(tmp_path / "test_memory.json")

    # Instance 1: Store findings, relationships, and invalidations
    mem1 = ValidatedKnowledgeMemory(persistence_path=persist_file)

    f1 = ValidatedFinding(
        finding_id="fnd-p1",
        title="Persistent Finding 1",
        statement="Statement 1",
        hypothesis_id="hyp-p1",
        created_at="",
        updated_at="",
    )
    f2 = ValidatedFinding(
        finding_id="fnd-p2",
        title="Persistent Finding 2",
        statement="Statement 2 derived from 1",
        hypothesis_id="hyp-p2",
        derived_from_finding_ids=["fnd-p1"],
        created_at="",
        updated_at="",
    )
    mem1.store_validated_finding(f1, supported_experiment)
    mem1.store_validated_finding(f2, supported_experiment)

    # Invalidate F1 in Instance 1
    mem1.invalidate_finding("fnd-p1", reason="Experimental discrepancy found.")

    # Instance 2 (Simulated Application Restart): loads from same file
    mem2 = ValidatedKnowledgeMemory(persistence_path=persist_file)

    # Verify findings are restored
    restored_f1 = mem2.get_finding("fnd-p1")
    assert restored_f1 is not None
    assert restored_f1.status == KnowledgeStatus.INVALIDATED
    assert restored_f1.version == 2
    assert "discrepancy" in restored_f1.invalidation_reason

    restored_f2 = mem2.get_finding("fnd-p2")
    assert restored_f2 is not None
    assert restored_f2.derived_from_finding_ids == ["fnd-p1"]

    # Verify audit history is restored
    history_f1 = mem2.get_finding_history("fnd-p1")
    assert len(history_f1) == 2
    assert history_f1[1].change_type == "INVALIDATED"

    # Verify cascading dependency DAG is restored
    impact = mem2.get_affected_dependents("fnd-p1")
    assert "fnd-p2" in impact.directly_affected_finding_ids

    # Verify integrity check is restored
    f2_sound, f2_issues = mem2.check_finding_integrity("fnd-p2")
    assert f2_sound is False
    assert any("fnd-p1" in issue for issue in f2_issues)

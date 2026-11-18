import pytest
from axion.transfer.types import (
    AlignmentMethod,
    ApplicabilityEvaluation,
    ApplicabilityVerdict,
    CandidateTransfer,
    DomainConcept,
    DomainKnowledgeBundle,
    DomainRelation,
    StructuralAlignmentResult,
    TransferRecord,
)
from axion.core.types import EpistemicTier, RelationType, ProvenancePointer
from axion.hypothesis.generator import HypothesisGenerator
from axion.hypothesis.types import ExperimentType

def test_hypothesis_generator_synthesizes_demarcated_hypotheses():
    generator = HypothesisGenerator()

    candidate = CandidateTransfer(
        transfer_id="cand-001",
        source_domain="fluid_mechanics",
        target_domain="electrical_circuits",
        source_relation=DomainRelation(
            source_concept="Pressure Drop",
            target_concept="Volumetric Flow",
            relation_type=RelationType.PROPORTIONAL_TO,
            equation="dP = Q * R_h",
            provenance=ProvenancePointer(document_id="doc_pipe", chunk_id="chk1", page_number=5, extracted_snippet="dP = Q * R_h"),
        ),
        proposed_source_concept="Electric Voltage",
        proposed_target_concept="Electric Current",
        proposed_relation_type=RelationType.PROPORTIONAL_TO,
        proposed_equation="V = I * R",
        mapped_concept_names={"Pressure Drop": "Electric Voltage", "Volumetric Flow": "Electric Current"},
        mapped_symbols={"dP": "V", "Q": "I", "R_h": "R"},
        epistemic_tier=EpistemicTier.HYPOTHESIS_CONJECTURED,
        rationale="Pipe flow maps to circuit current.",
    )

    evaluation = ApplicabilityEvaluation(
        transfer_id="cand-001",
        verdict=ApplicabilityVerdict.ACCEPTED,
        confidence=0.95,
        passed_stages=["structural_compatibility", "dimensional_homogeneity"],
        failed_stages=[],
        stage_results=[],
        conditions_required=["steady_state"],
        violations=[],
        rationale="Passed all tests.",
    )

    record = TransferRecord(
        record_id="rec-001",
        source_domain="fluid_mechanics",
        target_domain="electrical_circuits",
        alignment=StructuralAlignmentResult(
            source_domain="fluid_mechanics",
            target_domain="electrical_circuits",
            method=AlignmentMethod.STRUCTURE_MAPPING,
            structural_similarity_score=0.9,
            systematicity_score=0.85,
        ),
        candidate_transfers=[candidate],
        evaluations=[evaluation],
        accepted_transfers=[candidate],
        conditional_transfers=[],
        rejected_transfers=[],
    )

    hypotheses = generator.generate_hypotheses_from_transfer_record(record)
    assert len(hypotheses) == 1
    hyp = hypotheses[0]

    # Verify epistemic demarcation
    assert hyp.epistemic_tier == EpistemicTier.HYPOTHESIS_CONJECTURED
    assert "EPISTEMIC DEMARCATION" in hyp.epistemic_disclaimer
    assert hyp.applicability_verdict == ApplicabilityVerdict.ACCEPTED

    # Verify structured fields
    assert len(hyp.premise) >= 2
    assert "Electric Voltage" in hyp.mechanism
    assert "V = I * R" in hyp.prediction
    assert len(hyp.counterevidence_conditions) >= 2

    # Verify proposed experiments
    exp_types = [e.experiment_type for e in hyp.suggested_experiments]
    assert ExperimentType.SYMBOLIC_DERIVATION in exp_types
    assert ExperimentType.NUMERICAL_SIMULATION in exp_types
    assert ExperimentType.LABORATORY_MEASUREMENT in exp_types

    # Verify provenance preserved
    assert len(hyp.provenance_links) == 1
    assert hyp.provenance_links[0].document_id == "doc_pipe"

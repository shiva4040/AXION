import pytest
from axion.transfer.types import (
    ApplicabilityVerdict,
    CandidateTransfer,
    DomainConcept,
    DomainKnowledgeBundle,
    DomainRelation,
)
from axion.core.types import EntityCategory, EpistemicTier, RelationType
from axion.transfer.guard import ApplicabilityGuard, parse_si_formula

def test_parse_si_formula():
    dim1 = parse_si_formula("[M][L]2[T]-3[I]-1")
    assert dim1 is not None
    assert dim1.mass == 1
    assert dim1.length == 2
    assert dim1.time == -3
    assert dim1.current == -1
    assert dim1.temperature == 0

    dim2 = parse_si_formula("[M] [L]^2 [T]^-2")
    assert dim2 is not None
    assert dim2.mass == 1
    assert dim2.length == 2
    assert dim2.time == -2

def test_guard_accepts_dimensionally_consistent_transfer():
    guard = ApplicabilityGuard()

    # Target bundle: Electrical Conduction
    target = DomainKnowledgeBundle(
        domain_name="target:electrical",
        concepts=[
            DomainConcept(name="Electric Voltage", domain="target:electrical", symbol="V", si_dimension="[M][L]2[T]-3[I]-1"),
            DomainConcept(name="Electric Current", domain="target:electrical", symbol="I", si_dimension="[I]"),
            DomainConcept(name="Electric Resistance", domain="target:electrical", symbol="R", si_dimension="[M][L]2[T]-3[I]-2"),
        ],
        relations=[],
        assumptions=["linear", "steady_state"],
    )

    candidate = CandidateTransfer(
        transfer_id="cand-001",
        source_domain="source:hydraulic",
        target_domain="target:electrical",
        source_relation=DomainRelation(
            source_concept="Pressure Drop",
            target_concept="Volumetric Flow",
            relation_type=RelationType.PROPORTIONAL_TO,
            equation="dP = Q * R_h",
            assumptions_required=["linear"],
        ),
        proposed_source_concept="Electric Voltage",
        proposed_target_concept="Electric Current",
        proposed_relation_type=RelationType.PROPORTIONAL_TO,
        proposed_equation="V = I * R",
        mapped_concept_names={"Pressure Drop": "Electric Voltage", "Volumetric Flow": "Electric Current"},
        mapped_symbols={"dP": "V", "Q": "I", "R_h": "R"},
        epistemic_tier=EpistemicTier.HYPOTHESIS_CONJECTURED,
        rationale="Hydraulic to electrical analogy.",
    )

    eval_res = guard.evaluate_transfer(candidate, target)
    assert eval_res.verdict == ApplicabilityVerdict.ACCEPTED
    assert "structural_compatibility" in eval_res.passed_stages
    assert "dimensional_homogeneity" in eval_res.passed_stages
    assert "physical_assumptions" in eval_res.passed_stages

def test_guard_rejects_dimensional_mismatch():
    guard = ApplicabilityGuard()

    target = DomainKnowledgeBundle(
        domain_name="target:physics",
        concepts=[
            DomainConcept(name="Energy", domain="target:physics", symbol="E", si_dimension="[M][L]2[T]-2"),
            DomainConcept(name="Velocity", domain="target:physics", symbol="v", si_dimension="[L][T]-1"),
        ],
        relations=[],
    )

    # Intentionally illegal dimensional transfer: Energy = Velocity
    candidate = CandidateTransfer(
        transfer_id="cand-dim-err",
        source_domain="source:mechanics",
        target_domain="target:physics",
        source_relation=DomainRelation(
            source_concept="Work",
            target_concept="Speed",
            relation_type=RelationType.PROPORTIONAL_TO,
        ),
        proposed_source_concept="Energy",
        proposed_target_concept="Velocity",
        proposed_relation_type=RelationType.PROPORTIONAL_TO,
        proposed_equation="E = v",
        mapped_concept_names={"Work": "Energy", "Speed": "Velocity"},
        mapped_symbols={"W": "E", "u": "v"},
        epistemic_tier=EpistemicTier.HYPOTHESIS_CONJECTURED,
        rationale="Bogus dimensional transfer.",
    )

    eval_res = guard.evaluate_transfer(candidate, target)
    assert eval_res.verdict == ApplicabilityVerdict.REJECTED
    assert "dimensional_homogeneity" in eval_res.failed_stages
    assert any("Dimensional violation" in v for v in eval_res.violations)

def test_guard_rejects_assumption_contradiction():
    guard = ApplicabilityGuard()

    # Target explicitly assumes turbulent flow
    target = DomainKnowledgeBundle(
        domain_name="target:aero",
        concepts=[
            DomainConcept(name="Velocity", domain="target:aero", symbol="v"),
            DomainConcept(name="Drag", domain="target:aero", symbol="D"),
        ],
        relations=[],
        assumptions=["turbulent_flow"],
    )

    # Candidate transfer requires laminar flow
    candidate = CandidateTransfer(
        transfer_id="cand-assump-err",
        source_domain="source:fluid",
        target_domain="target:aero",
        source_relation=DomainRelation(
            source_concept="Potential",
            target_concept="Flux",
            relation_type=RelationType.PROPORTIONAL_TO,
            assumptions_required=["laminar_flow"],
        ),
        proposed_source_concept="Velocity",
        proposed_target_concept="Drag",
        proposed_relation_type=RelationType.PROPORTIONAL_TO,
        mapped_concept_names={"Potential": "Velocity", "Flux": "Drag"},
        epistemic_tier=EpistemicTier.HYPOTHESIS_CONJECTURED,
        rationale="Transfer requiring laminar flow into turbulent target.",
    )

    eval_res = guard.evaluate_transfer(candidate, target)
    assert eval_res.verdict == ApplicabilityVerdict.REJECTED
    assert "physical_assumptions" in eval_res.failed_stages
    assert any("turbulent_flow" in v for v in eval_res.violations)

def test_guard_rejects_target_empirical_contradiction():
    guard = ApplicabilityGuard()

    # Target already contains empirical fact: Drug inhibits TargetProtein
    target = DomainKnowledgeBundle(
        domain_name="target:pharmacology",
        concepts=[
            DomainConcept(name="Compound_X", domain="target:pharmacology"),
            DomainConcept(name="Enzyme_Y", domain="target:pharmacology"),
        ],
        relations=[
            DomainRelation(
                source_concept="Compound_X",
                target_concept="Enzyme_Y",
                relation_type=RelationType.INHIBITS,
                epistemic_tier=EpistemicTier.FACT_DOCUMENTED,
                evidence_snippet="Assay proves Compound_X strongly inhibits Enzyme_Y with IC50=12nM.",
            )
        ],
    )

    # Candidate transfer proposes Compound_X REQUIRES Enzyme_Y (opposing relation!)
    candidate = CandidateTransfer(
        transfer_id="cand-contra-err",
        source_domain="source:metabolism",
        target_domain="target:pharmacology",
        source_relation=DomainRelation(
            source_concept="Substrate_A",
            target_concept="CoFactor_B",
            relation_type=RelationType.REQUIRES,
        ),
        proposed_source_concept="Compound_X",
        proposed_target_concept="Enzyme_Y",
        proposed_relation_type=RelationType.REQUIRES,
        mapped_concept_names={"Substrate_A": "Compound_X", "CoFactor_B": "Enzyme_Y"},
        epistemic_tier=EpistemicTier.HYPOTHESIS_CONJECTURED,
        rationale="Contradictory transfer.",
    )

    eval_res = guard.evaluate_transfer(candidate, target)
    assert eval_res.verdict == ApplicabilityVerdict.REJECTED
    assert "contradiction_check" in eval_res.failed_stages
    assert any("inhibits" in v.lower() for v in eval_res.violations)

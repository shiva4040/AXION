import pytest
from axion.core.types import EpistemicTier, ProvenancePointer
from axion.pipeline.stage04_composition import MinimalKnowledgeComposer
from axion.pipeline.types import ComposedSystem, ExtractedClaim, QuestionIntent, QuestionSpec


def test_stage04_variable_harmonization():
    """Verify variable tokens are mapped to canonical concepts."""
    composer = MinimalKnowledgeComposer()

    prov = ProvenancePointer(
        document_id="doc-1",
        chunk_id="c-1",
        page_number=1,
        extracted_snippet="V = I * R",
    )
    claim = ExtractedClaim(
        statement="V = I * R",
        epistemic_tier=EpistemicTier.FACT_DOCUMENTED,
        equations=["V = I * R"],
        variables=["V", "I", "R"],
        provenance=prov,
    )

    spec = QuestionSpec(
        raw_query="Calculate voltage given current and resistance",
        target_variables=["voltage"],
        declared_parameters={"current": "2 A", "resistance": "10 Ohm"},
    )

    unified = composer.harmonize_variables([claim], spec)
    assert unified["voltage"] == "voltage"
    assert unified["current"] == "current"
    assert unified["V"] == "voltage"
    assert unified["I"] == "current"
    assert unified["R"] == "resistance"


def test_stage04_conflict_detection():
    """Verify composer flags mutually exclusive regimes."""
    composer = MinimalKnowledgeComposer()
    conflicts = composer.detect_conflicts(["assuming laminar flow", "for turbulent flow"])
    assert len(conflicts) >= 1
    assert "laminar" in conflicts[0] and "turbulent" in conflicts[0]


def test_stage04_compose_system():
    """Verify full ComposedSystem assembly with equations, conditions, and boundaries."""
    composer = MinimalKnowledgeComposer()

    prov1 = ProvenancePointer(document_id="d1", chunk_id="c1", page_number=1, extracted_snippet="P = V * I")
    prov2 = ProvenancePointer(document_id="d2", chunk_id="c2", page_number=2, extracted_snippet="V = I * R")

    c1 = ExtractedClaim(
        statement="Power P = V * I in DC circuits",
        conditions=["DC circuit"],
        equations=["P = V * I"],
        variables=["P", "V", "I"],
        provenance=prov1,
    )
    c2 = ExtractedClaim(
        statement="Voltage V = I * R across a resistor",
        conditions=["Ohmic conductor"],
        equations=["V = I * R"],
        variables=["V", "I", "R"],
        provenance=prov2,
    )

    spec = QuestionSpec(
        raw_query="What is the total power dissipation?",
        target_variables=["P"],
        domain_tags=["physics:electromagnetism"],
        identified_constraints={"flow_regime": "steady"},
        declared_parameters={"I": "2 A", "R": "5 Ohm"},
    )

    system = composer.compose_system([c1, c2], spec)
    assert isinstance(system, ComposedSystem)
    assert len(system.coupled_equations) == 2
    assert "P = V * I" in system.coupled_equations
    assert "V = I * R" in system.coupled_equations
    assert "DC circuit" in system.active_assumptions
    assert "Ohmic conductor" in system.active_assumptions
    assert "flow_regime: steady" in system.active_assumptions
    assert system.boundary_limits["I"] == "2 A"
    assert system.boundary_limits["R"] == "5 Ohm"
    assert "physics:electromagnetism" in system.participating_domains

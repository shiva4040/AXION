import pytest
from axion.core.types import EpistemicTier, ProvenancePointer
from axion.pipeline.stage05_reasoning import MinimalReasoner
from axion.pipeline.types import ComposedSystem, ExtractedClaim, ReasoningTrace


def test_stage05_numeric_parameter_parsing():
    """Verify parser extracts magnitudes and units."""
    reasoner = MinimalReasoner()
    val, unit = reasoner.parse_numeric_parameter("10.5 V")
    assert val == 10.5
    assert unit == "V"

    val2, unit2 = reasoner.parse_numeric_parameter("-42 m/s")
    assert val2 == -42.0
    assert unit2 == "m/s"


def test_stage05_single_equation_calculation():
    """Verify single equation algebraic evaluation."""
    reasoner = MinimalReasoner()

    prov = ProvenancePointer(document_id="d1", chunk_id="c1", page_number=1, extracted_snippet="P = V * I")
    claim = ExtractedClaim(
        statement="P = V * I",
        equations=["P = V * I"],
        variables=["P", "V", "I"],
        provenance=prov,
    )
    system = ComposedSystem(
        unified_variables={"P": "power", "V": "voltage", "I": "current"},
        coupled_equations=["P = V * I"],
        claims=[claim],
        boundary_limits={"V": "10 V", "I": "2 A"},
        participating_domains=["physics:electromagnetism"],
    )

    trace = reasoner.execute_reasoning(system)
    assert isinstance(trace, ReasoningTrace)
    assert "P" in trace.calculated_values
    assert "20 W" in trace.calculated_values["P"]
    assert "P" in trace.dependency_dag
    assert "V" in trace.dependency_dag["P"] or "I" in trace.dependency_dag["P"]
    assert any("20" in step for step in trace.steps)


def test_stage05_multi_step_chained_substitution():
    """Verify chained multi-step reasoning: V = I * R -> P = V * I."""
    reasoner = MinimalReasoner()

    prov1 = ProvenancePointer(document_id="d1", chunk_id="c1", page_number=1, extracted_snippet="V = I * R")
    prov2 = ProvenancePointer(document_id="d2", chunk_id="c2", page_number=2, extracted_snippet="P = V * I")

    c1 = ExtractedClaim(statement="V = I * R", equations=["V = I * R"], variables=["V", "I", "R"], provenance=prov1)
    c2 = ExtractedClaim(statement="P = V * I", equations=["P = V * I"], variables=["P", "V", "I"], provenance=prov2)

    system = ComposedSystem(
        unified_variables={"P": "power", "V": "voltage", "I": "current", "R": "resistance"},
        coupled_equations=["V = I * R", "P = V * I"],
        claims=[c1, c2],
        boundary_limits={"I": "2 A", "R": "5 Ohm"},
        participating_domains=["physics:electromagnetism"],
    )

    trace = reasoner.execute_reasoning(system)
    assert "V" in trace.calculated_values
    assert "10 V" in trace.calculated_values["V"]
    assert "P" in trace.calculated_values
    assert "20 W" in trace.calculated_values["P"]
    # Check DAG causality
    assert "V" in trace.dependency_dag["P"]


def test_stage05_missing_variable_handling():
    """Verify reasoner does not invent missing constants or variables."""
    reasoner = MinimalReasoner()

    prov = ProvenancePointer(document_id="d1", chunk_id="c1", page_number=1, extracted_snippet="P = V * I")
    claim = ExtractedClaim(
        statement="P = V * I",
        equations=["P = V * I"],
        variables=["P", "V", "I"],
        provenance=prov,
    )
    # Only V is supplied, I is missing
    system = ComposedSystem(
        unified_variables={"P": "power"},
        coupled_equations=["P = V * I"],
        claims=[claim],
        boundary_limits={"V": "10 V"},
    )

    trace = reasoner.execute_reasoning(system)
    # Must NOT invent P
    assert "P" not in trace.calculated_values
    assert any("No quantitative equation path resolved" in step for step in trace.steps)

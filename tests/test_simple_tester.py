import pytest
from axion.simple_tester import (
    SimpleHypothesisTester,
    ValidationVerdict,
    SIDimension,
    PhysicalConstraint,
    SymbolicVerifier,
    SI_FORCE,
    SI_VELOCITY,
    SI_POWER,
    SI_ENERGY
)

def test_symbolic_equivalence_valid():
    # E = m * c^2 with substitution of c^2
    is_valid, msg = SymbolicVerifier.check_equivalence(
        equation_str="E = m * c**2",
        substitutions={"c": "299792458", "m": "1.0", "E": "299792458**2"}
    )
    assert is_valid is True
    assert "identity confirmed" in msg.lower()

def test_symbolic_equivalence_invalid():
    # Intentionally false equation
    is_valid, msg = SymbolicVerifier.check_equivalence(
        equation_str="x**2 + y**2 = (x + y)**2"
    )
    assert is_valid is False
    assert "contradiction" in msg.lower()

def test_dimensional_analysis_valid_equations():
    tester = SimpleHypothesisTester()
    
    # 1. Power = Force * Velocity: P = F * v
    res1 = tester.validate_equation("p = f * v")
    assert res1.verdict == ValidationVerdict.VALID
    assert res1.is_dimensionally_valid is True
    assert "[M] [L]^2 [T]^-3" in res1.lhs_dimension

    # 2. Ohm's Law: Voltage = Current * Resistance: V = I * R
    res2 = tester.validate_equation("voltage = current * r")
    assert res2.verdict == ValidationVerdict.VALID
    assert res2.is_dimensionally_valid is True

    # 3. Kinetic energy: E = 0.5 * m * v^2
    res3 = tester.validate_equation("e = 0.5 * mass * v**2")
    assert res3.verdict == ValidationVerdict.VALID
    assert "[M] [L]^2 [T]^-2" in res3.lhs_dimension

def test_dimensional_analysis_invalid_mismatch():
    tester = SimpleHypothesisTester()

    # Invalid: Equating Power to Energy: P = E
    res_mismatch = tester.validate_equation("p = e")
    assert res_mismatch.verdict == ValidationVerdict.INVALID
    assert res_mismatch.is_dimensionally_valid is False
    assert "Dimensional mismatch" in res_mismatch.explanation

    # Invalid addition of different dimensions: Force + Velocity: P = F + v
    res_add_err = tester.validate_equation("p = f + v")
    assert res_add_err.verdict == ValidationVerdict.INVALID
    assert "Dimensional inconsistency in addition" in res_add_err.explanation

def test_missing_variable_insufficient_information():
    tester = SimpleHypothesisTester()
    # 'exotic_flux' and 'zephyrian_k' have no defined dimensions
    res = tester.validate_equation("exotic_flux = zephyrian_k * t_kelvin")
    assert res.verdict == ValidationVerdict.INSUFFICIENT_INFORMATION
    assert "Missing unit definition" in res.explanation

def test_physical_boundary_constraints():
    tester = SimpleHypothesisTester()

    # Valid values: efficiency = 21%, temperature = 300 K
    res_valid = tester.validate_equation(
        "p = f * v",
        variable_values={"eta": 0.21, "t_kelvin": 300.0, "v": 6.94}
    )
    assert res_valid.verdict == ValidationVerdict.VALID
    assert res_valid.constraints_evaluated == 3

    # Invalid values: efficiency = 140% (> 1.0) and temperature = -5 K (< 0 K)
    res_invalid = tester.validate_equation(
        "p = f * v",
        variable_values={"eta": 1.40, "t_kelvin": -5.0}
    )
    assert res_invalid.verdict == ValidationVerdict.INVALID
    assert len(res_invalid.failed_conditions) >= 2
    assert any("eta" in c for c in res_invalid.failed_conditions)
    assert any("t_kelvin" in c for c in res_invalid.failed_conditions)

def test_custom_configurable_constraints():
    # User adds custom constraint: Maximum vehicle payload mass <= 150 kg
    custom_c = PhysicalConstraint(
        variable_symbol="m_payload",
        description="Commuter vehicle payload mass must be <= 150 kg",
        min_value=0.0,
        max_value=150.0
    )
    tester = SimpleHypothesisTester(custom_constraints=[custom_c])

    # Test within bound
    r_pass = tester.validate_equation(
        "f = m_payload * a",
        variable_values={"m_payload": 75.0}
    )
    assert r_pass.verdict == ValidationVerdict.VALID

    # Test exceeding bound (200 kg)
    r_fail = tester.validate_equation(
        "f = m_payload * a",
        variable_values={"m_payload": 200.0}
    )
    assert r_fail.verdict == ValidationVerdict.INVALID
    assert any("exceeds maximum 150" in c for c in r_fail.failed_conditions)

def test_epistemic_disclaimer_presence():
    tester = SimpleHypothesisTester()
    res = tester.validate_equation("p = f * v")
    assert "Notice: Validation confirms symbolic" in res.epistemic_disclaimer
    assert "does NOT constitute experimental" in res.epistemic_disclaimer

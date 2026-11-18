import pytest
from axion.hypothesis_tester.types import (
    ExperimentRequest,
    ExperimentType,
    ExperimentVerdict,
)
from axion.hypothesis_tester.tester import FullHypothesisTester

@pytest.fixture
def tester():
    return FullHypothesisTester()

def test_symbolic_hypothesis_testing(tester):
    # Supported algebraic identity
    req_pass = ExperimentRequest(
        hypothesis_id="hyp-sym-01",
        hypothesis_title="Ohm's Voltage Law",
        prediction_model="V = I * R",
        experiment_type=ExperimentType.SYMBOLIC_TEST,
        parameters={"V": 10.0, "I": 2.0, "R": 5.0},
    )
    rec_pass = tester.run_experiment(req_pass)
    assert rec_pass.verdict == ExperimentVerdict.SUPPORTED
    assert rec_pass.confidence >= 0.90
    assert "EPISTEMIC NOTICE" in rec_pass.scientific_disclaimer

    # Unsupported algebraic contradiction
    req_fail = ExperimentRequest(
        hypothesis_id="hyp-sym-02",
        hypothesis_title="Contradictory Identity",
        prediction_model="V = I * R + 5",
        experiment_type=ExperimentType.SYMBOLIC_TEST,
        parameters={"V": 10.0, "I": 2.0, "R": 5.0},
    )
    rec_fail = tester.run_experiment(req_fail)
    assert rec_fail.verdict == ExperimentVerdict.NOT_SUPPORTED
    assert rec_fail.failure_analysis is not None

def test_statistical_hypothesis_testing_success(tester):
    # Synthetic empirical dataset with strong linear fit: V = 5.0 * I + small noise
    dataset = [
        {"I": 1.0, "V": 5.05},
        {"I": 2.0, "V": 10.02},
        {"I": 3.0, "V": 14.95},
        {"I": 4.0, "V": 20.08},
        {"I": 5.0, "V": 24.98},
    ]

    req = ExperimentRequest(
        hypothesis_id="hyp-stat-01",
        hypothesis_title="Empirical Ohm Voltage",
        prediction_model="V = 5.0 * I",
        experiment_type=ExperimentType.STATISTICAL_TEST,
        parameters={"independent_var": "I", "dependent_var": "V", "expected_slope_sign": 1.0},
        dataset=dataset,
        r_squared_threshold=0.85,
    )
    rec = tester.run_experiment(req)
    assert rec.verdict == ExperimentVerdict.SUPPORTED
    assert rec.statistical_evidence is not None
    assert rec.statistical_evidence.r_squared > 0.95
    assert rec.statistical_evidence.p_value < 0.05

def test_statistical_hypothesis_testing_rejection(tester):
    # Dataset with opposite slope (negative correlation when positive was expected)
    dataset = [
        {"I": 1.0, "V": 25.0},
        {"I": 2.0, "V": 20.0},
        {"I": 3.0, "V": 15.0},
        {"I": 4.0, "V": 10.0},
        {"I": 5.0, "V": 5.0},
    ]

    req = ExperimentRequest(
        hypothesis_id="hyp-stat-fail",
        hypothesis_title="Opposite Slope Trend",
        prediction_model="V = 5.0 * I",
        experiment_type=ExperimentType.STATISTICAL_TEST,
        parameters={"independent_var": "I", "dependent_var": "V", "expected_slope_sign": 1.0},
        dataset=dataset,
    )
    rec = tester.run_experiment(req)
    assert rec.verdict == ExperimentVerdict.NOT_SUPPORTED
    assert "Slope sign contradiction" in rec.failure_analysis

def test_statistical_insufficient_data(tester):
    req = ExperimentRequest(
        hypothesis_id="hyp-stat-few",
        hypothesis_title="Too Few Data Points",
        prediction_model="V = I * R",
        experiment_type=ExperimentType.STATISTICAL_TEST,
        parameters={"independent_var": "I", "dependent_var": "V"},
        dataset=[{"I": 1.0, "V": 5.0}], # N=1
    )
    rec = tester.run_experiment(req)
    assert rec.verdict == ExperimentVerdict.INSUFFICIENT_DATA

def test_dynamical_simulation_decay(tester):
    # Newton's law of cooling: dx/dt = -0.5 * (x - 20)
    req = ExperimentRequest(
        hypothesis_id="hyp-sim-cooling",
        hypothesis_title="Thermal Cooling Simulation",
        prediction_model="dx/dt = -0.5 * (x - 20)",
        experiment_type=ExperimentType.NUMERICAL_SIMULATION,
        parameters={
            "system_type": "first_order_decay",
            "k": 0.5,
            "x_env": 20.0,
            "expected_steady_state": {"x": 20.0},
        },
        initial_conditions={"x": 100.0},
        time_span=(0.0, 15.0),
        tolerance=0.05,
    )
    rec = tester.run_experiment(req)
    assert rec.verdict == ExperimentVerdict.SUPPORTED
    assert rec.simulation_result is not None
    assert rec.simulation_result.converged is True
    assert abs(rec.simulation_result.steady_state_values["x"] - 20.0) < 0.1

def test_dynamical_simulation_oscillator(tester):
    # Damped harmonic oscillator
    req = ExperimentRequest(
        hypothesis_id="hyp-sim-osc",
        hypothesis_title="Damped Harmonic Oscillator",
        prediction_model="d2x/dt2 + 2*zeta*w0*dx/dt + w0^2*x = 0",
        experiment_type=ExperimentType.NUMERICAL_SIMULATION,
        parameters={"system_type": "second_order_oscillator", "w0": 2.0, "zeta": 0.2},
        initial_conditions={"x": 1.0, "v": 0.0},
        time_span=(0.0, 10.0),
    )
    rec = tester.run_experiment(req)
    assert rec.verdict == ExperimentVerdict.SUPPORTED
    assert rec.simulation_result is not None
    assert len(rec.simulation_result.state_trajectories["x"]) > 10

def test_dataset_evaluation_residuals(tester):
    dataset = [
        {"I": 1.0, "R": 10.0, "V": 10.05},
        {"I": 2.0, "R": 10.0, "V": 19.95},
        {"I": 3.0, "R": 10.0, "V": 30.10},
    ]

    req = ExperimentRequest(
        hypothesis_id="hyp-ds-01",
        hypothesis_title="Tabular Ohm Residual Evaluation",
        prediction_model="V = I * R",
        experiment_type=ExperimentType.DATASET_EVALUATION,
        parameters={"target_variable": "V"},
        dataset=dataset,
        tolerance=0.05,
    )
    rec = tester.run_experiment(req)
    assert rec.verdict == ExperimentVerdict.SUPPORTED
    assert rec.statistical_evidence.mean_relative_error < 0.05

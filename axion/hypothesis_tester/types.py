from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
from pydantic import BaseModel, Field

class ExperimentType(str, Enum):
    """Supported scientific experimental validation methods."""
    SYMBOLIC_TEST = "SYMBOLIC_TEST"
    NUMERICAL_CALCULATION = "NUMERICAL_CALCULATION"
    STATISTICAL_TEST = "STATISTICAL_TEST"
    DATASET_EVALUATION = "DATASET_EVALUATION"
    NUMERICAL_SIMULATION = "NUMERICAL_SIMULATION"

class ExperimentVerdict(str, Enum):
    """Structured outcome of empirical/numerical hypothesis testing."""
    SUPPORTED = "SUPPORTED"                 # Empirical observation or simulation strictly corroborates prediction
    NOT_SUPPORTED = "NOT_SUPPORTED"         # Observation contradicts or falsifies prediction
    INCONCLUSIVE = "INCONCLUSIVE"           # Borderline effect size, ambiguous residuals, or non-convergent simulation
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA" # Sample size too small, missing parameters, or missing observation fields

class StatisticalEvidence(BaseModel):
    """Statistical summary metrics quantifying empirical support."""
    test_name: str
    sample_size: int
    r_squared: Optional[float] = None
    p_value: Optional[float] = None
    effect_size: Optional[float] = None
    rmse: Optional[float] = None
    mean_relative_error: Optional[float] = None
    confidence_interval: Optional[Tuple[float, float]] = None
    alpha_threshold: float = Field(default=0.05)

class SimulationResult(BaseModel):
    """Time-series trajectory and steady-state outcome of an ODE/dynamical simulation."""
    time_points: List[float] = Field(default_factory=list)
    state_trajectories: Dict[str, List[float]] = Field(default_factory=dict)
    steady_state_values: Dict[str, float] = Field(default_factory=dict)
    converged: bool = True
    step_count: int = 0
    divergence_detected: bool = False

class ExecutionMetadata(BaseModel):
    """Reproducibility metadata capturing execution conditions."""
    runtime_ms: float
    random_seed: Optional[int] = 42
    environment: str = "sandboxed_python_worker"
    memory_bytes: Optional[int] = None
    timestamp: Optional[str] = None

class ExperimentRecord(BaseModel):
    """
    Component 8 Output:
    Complete, reproducible audit record of a hypothesis testing experiment.
    """
    experiment_id: str
    hypothesis_id: str
    method: ExperimentType
    input_data_summary: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    assumptions: List[str] = Field(default_factory=list)
    expected_prediction: str
    actual_result: Dict[str, Any] = Field(default_factory=dict)
    statistical_evidence: Optional[StatisticalEvidence] = None
    simulation_result: Optional[SimulationResult] = None
    limitations: List[str] = Field(default_factory=list)
    verdict: ExperimentVerdict
    confidence: float = Field(ge=0.0, le=1.0)
    failure_analysis: Optional[str] = None
    execution_metadata: ExecutionMetadata
    scientific_disclaimer: str = (
        "EPISTEMIC NOTICE: Mathematical and numerical consistency within a model does NOT "
        "constitute physical empirical laboratory proof. Correlation does not imply causation."
    )

class ExperimentRequest(BaseModel):
    """Input payload to trigger a hypothesis validation experiment."""
    hypothesis_id: str
    hypothesis_title: str
    prediction_model: str = Field(description="Equation, ODE specification, or regression hypothesis (e.g., 'V = I * R')")
    experiment_type: ExperimentType
    parameters: Dict[str, Any] = Field(default_factory=dict)
    dataset: Optional[List[Dict[str, float]]] = Field(default=None, description="Observational data rows")
    time_span: Optional[Tuple[float, float]] = Field(default=None, description="Time span for ODE numerical simulation, e.g. (0.0, 10.0)")
    initial_conditions: Optional[Dict[str, float]] = Field(default=None)
    tolerance: float = Field(default=0.10, description="Acceptable relative error tolerance (default 10%)")
    r_squared_threshold: float = Field(default=0.85, description="Minimum R^2 for statistical regression support")
    assumptions: List[str] = Field(default_factory=list)

import uuid
import time
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from axion.hypothesis_tester.types import (
    ExecutionMetadata,
    ExperimentRecord,
    ExperimentRequest,
    ExperimentType,
    ExperimentVerdict,
)
from axion.hypothesis_tester.sandbox import SandboxExecutionWorker
from axion.hypothesis_tester.evaluators.symbolic_evaluator import SymbolicEvaluator
from axion.hypothesis_tester.evaluators.statistical_evaluator import StatisticalEvaluator
from axion.hypothesis_tester.evaluators.simulation_evaluator import SimulationEvaluator
from axion.hypothesis_tester.evaluators.dataset_evaluator import DatasetEvaluator

class FullHypothesisTester:
    """
    Component 8: Full Hypothesis Tester.
    Unified scientific experimentation subsystem executing symbolic calculations,
    statistical hypothesis tests, dynamical ODE simulations, and observational dataset evaluations.
    Enforces strict reproducible logging, failure analysis, and safety sandboxing.
    """

    def __init__(
        self,
        sandbox: Optional[SandboxExecutionWorker] = None,
        symbolic_eval: Optional[SymbolicEvaluator] = None,
        statistical_eval: Optional[StatisticalEvaluator] = None,
        simulation_eval: Optional[SimulationEvaluator] = None,
        dataset_eval: Optional[DatasetEvaluator] = None,
    ):
        self.sandbox = sandbox or SandboxExecutionWorker(timeout_seconds=5.0)
        self.symbolic_eval = symbolic_eval or SymbolicEvaluator()
        self.statistical_eval = statistical_eval or StatisticalEvaluator()
        self.simulation_eval = simulation_eval or SimulationEvaluator()
        self.dataset_eval = dataset_eval or DatasetEvaluator()

    def run_experiment(self, req: ExperimentRequest) -> ExperimentRecord:
        exp_id = f"exp-{uuid.uuid4().hex[:8]}"
        start_t = time.perf_counter()
        timestamp = datetime.now(timezone.utc).isoformat()

        limitations: List[str] = [
            "Computational validation in sandbox environment.",
            "Subject to finite floating-point precision and measurement error tolerance bounds.",
        ]

        stat_evidence = None
        sim_result = None
        verdict = ExperimentVerdict.INCONCLUSIVE
        failure_analysis = None
        actual_result: Dict[str, Any] = {}

        try:
            if req.experiment_type == ExperimentType.SYMBOLIC_TEST:
                verdict, actual_result, failure_analysis = self.symbolic_eval.evaluate_symbolic_hypothesis(
                    predicted_equation=req.prediction_model,
                    parameters=req.parameters,
                    boundary_limits=req.parameters.get("boundary_limits"),
                )

            elif req.experiment_type == ExperimentType.STATISTICAL_TEST:
                indep = req.parameters.get("independent_var", "x")
                dep = req.parameters.get("dependent_var", "y")
                expected_slope = req.parameters.get("expected_slope_sign")

                verdict, stat_evidence, actual_result, failure_analysis = self.statistical_eval.evaluate_dataset_statistics(
                    dataset=req.dataset or [],
                    independent_var=indep,
                    dependent_var=dep,
                    expected_slope_sign=expected_slope,
                    r_squared_threshold=req.r_squared_threshold,
                    tolerance=req.tolerance,
                )

            elif req.experiment_type == ExperimentType.NUMERICAL_SIMULATION:
                sys_type = req.parameters.get("system_type", "first_order_decay")
                time_span = req.time_span or (0.0, 10.0)
                init_conds = req.initial_conditions or {"x": 1.0}
                exp_ss = req.parameters.get("expected_steady_state")

                verdict, sim_result, actual_result, failure_analysis = self.simulation_eval.simulate_dynamical_hypothesis(
                    system_type=sys_type,
                    parameters=req.parameters,
                    initial_conditions=init_conds,
                    time_span=time_span,
                    expected_steady_state=exp_ss,
                    tolerance=req.tolerance,
                )

            elif req.experiment_type == ExperimentType.DATASET_EVALUATION:
                target_var = req.parameters.get("target_variable", "y")
                verdict, stat_evidence, actual_result, failure_analysis = self.dataset_eval.evaluate_equation_on_dataset(
                    equation_str=req.prediction_model,
                    dataset=req.dataset or [],
                    target_variable=target_var,
                    tolerance=req.tolerance,
                )

            elif req.experiment_type == ExperimentType.NUMERICAL_CALCULATION:
                # Basic algebraic formula calculation over point parameters
                verdict, actual_result, failure_analysis = self.symbolic_eval.evaluate_symbolic_hypothesis(
                    predicted_equation=req.prediction_model,
                    parameters=req.parameters,
                )

            else:
                verdict = ExperimentVerdict.INSUFFICIENT_DATA
                failure_analysis = f"Unknown or unsupported experiment type: {req.experiment_type}"

        except Exception as e:
            verdict = ExperimentVerdict.NOT_SUPPORTED
            failure_analysis = f"Experiment execution encountered runtime error: {e}"
            actual_result = {"error": str(e)}

        elapsed_ms = (time.perf_counter() - start_t) * 1000.0

        # Confidence assessment based on verdict and statistical strength
        if verdict == ExperimentVerdict.SUPPORTED:
            conf = 0.95 if (stat_evidence and stat_evidence.r_squared and stat_evidence.r_squared > 0.95) else 0.90
        elif verdict == ExperimentVerdict.NOT_SUPPORTED:
            conf = 0.95
        elif verdict == ExperimentVerdict.INCONCLUSIVE:
            conf = 0.50
        else:
            conf = 0.30

        metadata = ExecutionMetadata(
            runtime_ms=round(elapsed_ms, 2),
            random_seed=req.parameters.get("random_seed", 42),
            environment="sandboxed_python_worker",
            timestamp=timestamp,
        )

        input_summary = (
            f"Evaluated {req.experiment_type.value} on model '{req.prediction_model}' with "
            f"{len(req.dataset) if req.dataset else 0} dataset observations and {len(req.parameters)} parameters."
        )

        return ExperimentRecord(
            experiment_id=exp_id,
            hypothesis_id=req.hypothesis_id,
            method=req.experiment_type,
            input_data_summary=input_summary,
            parameters=req.parameters,
            assumptions=req.assumptions,
            expected_prediction=f"Expected model '{req.prediction_model}' to satisfy empirical observations within tolerance {req.tolerance:.1%}.",
            actual_result=actual_result,
            statistical_evidence=stat_evidence,
            simulation_result=sim_result,
            limitations=limitations,
            verdict=verdict,
            confidence=conf,
            failure_analysis=failure_analysis,
            execution_metadata=metadata,
        )

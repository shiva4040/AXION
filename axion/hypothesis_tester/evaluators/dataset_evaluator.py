from typing import Dict, List, Optional, Tuple, Any
import numpy as np
import sympy as sp
from axion.simple_tester.symbolic import SymbolicVerifier
from axion.hypothesis_tester.types import ExperimentVerdict, StatisticalEvidence

class DatasetEvaluator:
    """
    Directly tests quantitative equation hypotheses against tabular observational datasets,
    computing point-by-point residuals, relative errors, and tolerance boundaries.
    """

    def evaluate_equation_on_dataset(
        self,
        equation_str: str,
        dataset: List[Dict[str, float]],
        target_variable: str,
        tolerance: float = 0.10,
    ) -> Tuple[ExperimentVerdict, StatisticalEvidence, Dict[str, Any], Optional[str]]:
        if not dataset or len(dataset) < 1:
            evidence = StatisticalEvidence(test_name="Tabular Residual Evaluation", sample_size=0)
            return (
                ExperimentVerdict.INSUFFICIENT_DATA,
                evidence,
                {},
                "Observational dataset is empty."
            )

        lhs, rhs, parse_err = SymbolicVerifier.parse_equation(equation_str)
        if parse_err:
            evidence = StatisticalEvidence(test_name="Tabular Residual Evaluation", sample_size=len(dataset))
            return (
                ExperimentVerdict.NOT_SUPPORTED,
                evidence,
                {},
                f"Equation failed symbolic parsing: {parse_err}"
            )

        # Solve for target_variable expression if needed
        target_sym = sp.Symbol(target_variable)
        try:
            solutions = sp.solve(lhs - rhs, target_sym)
            if not solutions:
                pred_expr = rhs if str(lhs) == target_variable else lhs
            else:
                pred_expr = solutions[0]
        except Exception:
            pred_expr = rhs

        actual_vals = []
        pred_vals = []
        errors = []

        for row in dataset:
            if target_variable not in row:
                continue
            act_y = float(row[target_variable])
            # Substitute row values into pred_expr
            subs_map = {sp.Symbol(k): float(v) for k, v in row.items() if k != target_variable}
            try:
                calc_y = float(pred_expr.subs(subs_map))
            except Exception:
                continue

            actual_vals.append(act_y)
            pred_vals.append(calc_y)
            rel_err = abs(act_y - calc_y) / max(abs(act_y), 1e-6)
            errors.append(rel_err)

        n = len(actual_vals)
        if n == 0:
            evidence = StatisticalEvidence(test_name="Tabular Residual Evaluation", sample_size=0)
            return (
                ExperimentVerdict.INSUFFICIENT_DATA,
                evidence,
                {},
                f"Target variable '{target_variable}' could not be evaluated on dataset."
            )

        mean_err = float(np.mean(errors))
        max_err = float(np.max(errors))
        residuals = np.array(actual_vals) - np.array(pred_vals)
        rmse = float(np.sqrt(np.mean(residuals ** 2)))

        # R^2 calculation
        ss_tot = np.sum((np.array(actual_vals) - np.mean(actual_vals)) ** 2)
        ss_res = np.sum(residuals ** 2)
        r_sq = 1.0 - (ss_res / ss_tot) if ss_tot > 0 else (1.0 if rmse < 1e-6 else 0.0)
        r_sq = max(0.0, min(1.0, float(r_sq)))

        evidence = StatisticalEvidence(
            test_name="Tabular Residual Evaluation",
            sample_size=n,
            r_squared=round(r_sq, 4),
            rmse=round(rmse, 4),
            mean_relative_error=round(mean_err, 4),
        )

        actual_result = {
            "mean_relative_error": round(mean_err, 4),
            "max_relative_error": round(max_err, 4),
            "rmse": round(rmse, 4),
            "r_squared": round(r_sq, 4),
            "rows_evaluated": n,
        }

        if mean_err <= tolerance:
            return (
                ExperimentVerdict.SUPPORTED,
                evidence,
                actual_result,
                None
            )
        else:
            return (
                ExperimentVerdict.NOT_SUPPORTED,
                evidence,
                actual_result,
                f"Observation contradicts hypothesis: mean relative error {mean_err:.2%} exceeds tolerance {tolerance:.2%}."
            )

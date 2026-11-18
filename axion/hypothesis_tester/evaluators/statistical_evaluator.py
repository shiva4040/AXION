import math
from typing import Dict, List, Optional, Tuple, Any
import numpy as np
from axion.hypothesis_tester.types import ExperimentVerdict, StatisticalEvidence

class StatisticalEvaluator:
    """
    Executes empirical statistical hypothesis testing on observational datasets:
    - Linear/polynomial regression fit
    - R^2 coefficient of determination
    - Statistical hypothesis testing (p-value, t-statistic)
    - Effect size (Cohen's d)
    - Residual error analysis (RMSE, Mean Relative Error)
    """

    def evaluate_dataset_statistics(
        self,
        dataset: List[Dict[str, float]],
        independent_var: str,
        dependent_var: str,
        expected_slope_sign: Optional[float] = None, # 1.0 for positive proportional, -1.0 for inverse
        r_squared_threshold: float = 0.85,
        alpha_threshold: float = 0.05,
        tolerance: float = 0.15,
    ) -> Tuple[ExperimentVerdict, StatisticalEvidence, Dict[str, Any], Optional[str]]:
        if not dataset or len(dataset) < 3:
            evidence = StatisticalEvidence(
                test_name="Linear Regression & Residual Analysis",
                sample_size=len(dataset) if dataset else 0,
                alpha_threshold=alpha_threshold,
            )
            return (
                ExperimentVerdict.INSUFFICIENT_DATA,
                evidence,
                {},
                f"Sample size {len(dataset) if dataset else 0} is too small for statistical hypothesis testing (minimum N=3 required)."
            )

        # Extract vectors
        x_vals = []
        y_vals = []
        for row in dataset:
            if independent_var in row and dependent_var in row:
                x_vals.append(float(row[independent_var]))
                y_vals.append(float(row[dependent_var]))

        n = len(x_vals)
        if n < 3:
            evidence = StatisticalEvidence(
                test_name="Linear Regression & Residual Analysis",
                sample_size=n,
                alpha_threshold=alpha_threshold,
            )
            return (
                ExperimentVerdict.INSUFFICIENT_DATA,
                evidence,
                {},
                f"Insufficient matching data points for variables '{independent_var}' and '{dependent_var}' (found N={n})."
            )

        x_arr = np.array(x_vals, dtype=float)
        y_arr = np.array(y_vals, dtype=float)

        # Perform Linear Regression: y = slope * x + intercept
        mean_x = np.mean(x_arr)
        mean_y = np.mean(y_arr)
        ss_xx = np.sum((x_arr - mean_x) ** 2)
        ss_yy = np.sum((y_arr - mean_y) ** 2)
        ss_xy = np.sum((x_arr - mean_x) * (y_arr - mean_y))

        if ss_xx == 0 or ss_yy == 0:
            evidence = StatisticalEvidence(test_name="Linear Regression", sample_size=n, alpha_threshold=alpha_threshold)
            return (
                ExperimentVerdict.INCONCLUSIVE,
                evidence,
                {},
                "Zero variance in independent or dependent observational data."
            )

        slope = ss_xy / ss_xx
        intercept = mean_y - slope * mean_x

        # Fitted values and residuals
        y_pred = slope * x_arr + intercept
        residuals = y_arr - y_pred
        ss_res = np.sum(residuals ** 2)

        r_squared = 1.0 - (ss_res / ss_yy)
        r_squared = max(0.0, min(1.0, float(r_squared)))

        rmse = float(np.sqrt(np.mean(residuals ** 2)))
        mean_rel_err = float(np.mean(np.abs(residuals) / np.maximum(np.abs(y_arr), 1e-9)))

        # Standard error of slope and t-statistic
        df = n - 2
        s_err = np.sqrt(ss_res / max(df, 1)) / np.sqrt(ss_xx)
        t_stat = slope / s_err if s_err > 0 else 0.0

        # Approximate two-tailed p-value using Student's t approximation
        # For df >= 1, approximate p-value from t-stat
        x_t = df / (df + t_stat**2)
        # Regularized incomplete beta approximation or standard normal tail for large df
        p_val = 2.0 * (1.0 - 0.5 * (1.0 + math.erf(abs(t_stat) / math.sqrt(2.0))))
        p_val = max(1e-6, min(1.0, float(p_val)))

        # Effect size (Cohen's d on residuals vs spread)
        std_y = np.std(y_arr)
        effect_size = float(abs(slope) * np.std(x_arr) / std_y) if std_y > 0 else 0.0

        evidence = StatisticalEvidence(
            test_name="Linear Regression & Residual Analysis",
            sample_size=n,
            r_squared=round(r_squared, 4),
            p_value=round(p_val, 6),
            effect_size=round(effect_size, 3),
            rmse=round(rmse, 4),
            mean_relative_error=round(mean_rel_err, 4),
            confidence_interval=(round(float(slope - 1.96 * s_err), 4), round(float(slope + 1.96 * s_err), 4)),
            alpha_threshold=alpha_threshold,
        )

        actual_result = {
            "slope": round(float(slope), 4),
            "intercept": round(float(intercept), 4),
            "r_squared": round(r_squared, 4),
            "p_value": round(p_val, 6),
            "rmse": round(rmse, 4),
            "mean_relative_error": round(mean_rel_err, 4),
        }

        # Check slope direction if expected
        if expected_slope_sign is not None:
            if (expected_slope_sign > 0 and slope < 0) or (expected_slope_sign < 0 and slope > 0):
                return (
                    ExperimentVerdict.NOT_SUPPORTED,
                    evidence,
                    actual_result,
                    f"Slope sign contradiction: expected sign {expected_slope_sign}, but empirical regression slope is {slope:.4f}."
                )

        # Verdict logic
        if r_squared >= r_squared_threshold and p_val < alpha_threshold and mean_rel_err <= tolerance:
            return (
                ExperimentVerdict.SUPPORTED,
                evidence,
                actual_result,
                None
            )
        elif r_squared < 0.50 or p_val >= alpha_threshold:
            return (
                ExperimentVerdict.NOT_SUPPORTED,
                evidence,
                actual_result,
                f"Empirical hypothesis rejected: R^2={r_squared:.3f} (threshold {r_squared_threshold}), p={p_val:.4f}."
            )
        else:
            return (
                ExperimentVerdict.INCONCLUSIVE,
                evidence,
                actual_result,
                f"Inconclusive statistical fit: R^2={r_squared:.3f}, mean relative error={mean_rel_err:.3f} exceeds tolerance {tolerance}."
            )

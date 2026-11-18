import sympy as sp
from typing import Dict, List, Optional, Tuple, Any
from axion.simple_tester.symbolic import SymbolicVerifier
from axion.hypothesis_tester.types import ExperimentVerdict

class SymbolicEvaluator:
    """
    Evaluates symbolic equations, algebraic identity equivalence,
    and asymptotic boundary limit conditions.
    """

    def evaluate_symbolic_hypothesis(
        self,
        predicted_equation: str,
        parameters: Dict[str, Any],
        boundary_limits: Optional[Dict[str, float]] = None,
    ) -> Tuple[ExperimentVerdict, Dict[str, Any], Optional[str]]:
        lhs, rhs, parse_err = SymbolicVerifier.parse_equation(predicted_equation)
        if parse_err:
            return (
                ExperimentVerdict.NOT_SUPPORTED,
                {"parse_error": parse_err},
                f"Equation failed symbolic parsing: {parse_err}"
            )

        # Step 1: Check algebraic identity / consistency
        # Difference expression: expr = lhs - rhs
        diff_expr = sp.simplify(lhs - rhs)
        is_exact_identity = (diff_expr == 0)

        # Substitute known parameter constants if provided
        subs_dict = {}
        for k, v in parameters.items():
            sym = sp.Symbol(k)
            subs_dict[sym] = v

        diff_substituted = sp.simplify(diff_expr.subs(subs_dict)) if subs_dict else diff_expr
        is_consistent_with_parameters = (diff_substituted == 0)

        # Step 2: Check boundary asymptotic behavior if specified
        limit_checks = {}
        divergence_detected = False
        if boundary_limits:
            for var_name, limit_val in boundary_limits.items():
                v_sym = sp.Symbol(var_name)
                try:
                    lim = sp.limit(rhs, v_sym, limit_val)
                    limit_checks[f"limit_{var_name}_to_{limit_val}"] = str(lim)
                    if lim.is_infinite:
                        divergence_detected = True
                except Exception as e:
                    limit_checks[f"limit_{var_name}_to_{limit_val}"] = f"error: {e}"

        actual_result = {
            "simplified_expression": str(diff_expr),
            "is_exact_identity": is_exact_identity,
            "is_consistent": is_consistent_with_parameters,
            "boundary_limits": limit_checks,
        }

        if divergence_detected:
            return (
                ExperimentVerdict.NOT_SUPPORTED,
                actual_result,
                "Symbolic evaluation revealed unphysical singular divergence at boundary limits."
            )

        # If identity or parameters reduce difference to 0
        if is_exact_identity or is_consistent_with_parameters:
            return (
                ExperimentVerdict.SUPPORTED,
                actual_result,
                None
            )
        else:
            return (
                ExperimentVerdict.NOT_SUPPORTED,
                actual_result,
                f"Algebraic contradiction: LHS - RHS simplifies to {diff_substituted} != 0."
            )

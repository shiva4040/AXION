import re
import uuid
import logging
from typing import Any, Dict, List, Optional, Set, Tuple
import sympy as sp

from axion.simple_tester.symbolic import SymbolicVerifier
from axion.simple_tester.dimensional import DimensionalAnalyzer
from axion.pipeline.types import (
    ComposedSystem,
    ReasoningTrace,
)

logger = logging.getLogger(__name__)

# Pattern to extract numeric value and optional unit
NUMERIC_UNIT_PATTERN = re.compile(
    r"^\s*([+-]?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)\s*([a-zA-Z/Ω°%]*)\s*$"
)

# Pattern for variable tokens in equations
VAR_TOKEN_PATTERN = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*)\b")

# Standard unit multipliers & product rules
UNIT_PRODUCTS = {
    ("v", "a"): "W",
    ("a", "v"): "W",
    ("a", "ohm"): "V",
    ("ohm", "a"): "V",
    ("n", "m/s"): "W",
    ("m/s", "n"): "W",
    ("m", "m"): "m^2",
    ("w/m^2", "m^2"): "W",
    ("m^2", "w/m^2"): "W",
}


class MinimalReasoner:
    """
    Stage 05: Minimal Reasoner and Calculator.
    Performs deterministic algebraic substitutions, numerical calculations,
    SI dimensional verification, and causal dependency DAG construction.
    """

    def __init__(self):
        self.dimensional_analyzer = DimensionalAnalyzer()

    def parse_numeric_parameter(self, raw_val: str) -> Tuple[Optional[float], Optional[str]]:
        """Extracts float magnitude and unit string from raw value."""
        if isinstance(raw_val, (int, float)):
            return float(raw_val), ""
        match = NUMERIC_UNIT_PATTERN.match(str(raw_val).strip())
        if match:
            val_str, unit_str = match.groups()
            try:
                return float(val_str), unit_str
            except ValueError:
                return None, None
        return None, None

    def deduce_unit(self, op: str, u1: str, u2: str) -> str:
        """Determines product or quotient units."""
        u1_l = (u1 or "").lower()
        u2_l = (u2 or "").lower()
        if op == "*":
            pair = (u1_l, u2_l)
            if pair in UNIT_PRODUCTS:
                return UNIT_PRODUCTS[pair]
            if not u1:
                return u2
            if not u2:
                return u1
            return f"{u1}*{u2}"
        elif op == "/":
            if u1_l == u2_l and u1_l:
                return ""  # Dimensionless
            if not u2:
                return u1
            return f"{u1}/{u2}"
        return u1 or u2

    def solve_equation(
        self,
        eq_str: str,
        known_values: Dict[str, float],
        known_units: Dict[str, str],
    ) -> Tuple[Optional[str], Optional[float], Optional[str], Optional[str]]:
        """
        Attempts to solve an equation of the form LHS = RHS for an unknown variable.
        Returns (target_var, computed_value, computed_unit, explanation).
        """
        # Simple algebraic parsing
        if "=" not in eq_str:
            return None, None, None, None

        parts = eq_str.split("=")
        if len(parts) != 2:
            return None, None, None, None

        lhs_str = parts[0].strip()
        rhs_str = parts[1].strip()

        # Handle canonical LHS = expr, e.g. P = V * I or V = I * R or P = Area * Solar_Irradiance * Efficiency
        local_ns = SymbolicVerifier._get_symbol_namespace()
        try:
            lhs_expr = sp.parse_expr(lhs_str, local_dict=local_ns, evaluate=False)
            rhs_expr = sp.parse_expr(rhs_str, local_dict=local_ns, evaluate=False)
            if isinstance(lhs_expr, type):
                lhs_expr = sp.Symbol(lhs_str)
            if isinstance(rhs_expr, type):
                rhs_expr = sp.Symbol(rhs_str)
        except Exception as e:
            return None, None, None, f"Parse error in '{eq_str}': {e}"

        # Case 1: LHS is a single symbol and unknown, while all RHS symbols are known
        lhs_is_sym = isinstance(lhs_expr, sp.Symbol) or getattr(lhs_expr, "is_Symbol", False)
        if lhs_is_sym and str(lhs_expr) not in known_values:
            rhs_symbols = [str(s) for s in rhs_expr.free_symbols]
            # Check case-insensitive match for symbols in known_values
            resolved_sub = {}
            missing = []
            for s in rhs_symbols:
                matched_k = next((k for k in known_values if k.lower() == s.lower()), None)
                if matched_k is not None:
                    resolved_sub[s] = known_values[matched_k]
                else:
                    missing.append(s)

            if not missing:
                try:
                    num_val = float(rhs_expr.subs(resolved_sub).evalf())
                    target_var = str(lhs_expr)
                    
                    # Deduce unit from product
                    units_involved = [known_units.get(next(k for k in known_values if k.lower() == s.lower()), "") for s in rhs_symbols]
                    derived_unit = ""
                    for u in units_involved:
                        derived_unit = self.deduce_unit("*", derived_unit, u) if derived_unit else u

                    explanation = f"Evaluated {target_var} = {rhs_str} with {resolved_sub} -> {num_val} {derived_unit}".strip()
                    return target_var, num_val, derived_unit, explanation
                except ZeroDivisionError:
                    return None, None, None, f"Division by zero when evaluating {eq_str}"
                except Exception as e:
                    return None, None, None, f"Evaluation error in {eq_str}: {e}"

        # Case 2: RHS is single symbol, LHS is known
        rhs_is_sym = isinstance(rhs_expr, sp.Symbol) or getattr(rhs_expr, "is_Symbol", False)
        if rhs_is_sym and str(rhs_expr) not in known_values:
            lhs_symbols = [str(s) for s in lhs_expr.free_symbols]
            resolved_sub = {}
            missing = []
            for s in lhs_symbols:
                matched_k = next((k for k in known_values if k.lower() == s.lower()), None)
                if matched_k is not None:
                    resolved_sub[s] = known_values[matched_k]
                else:
                    missing.append(s)

            if not missing:
                try:
                    num_val = float(lhs_expr.subs(resolved_sub).evalf())
                    target_var = str(rhs_expr)
                    explanation = f"Evaluated {target_var} = {lhs_str} with {resolved_sub} -> {num_val}"
                    return target_var, num_val, "", explanation
                except Exception as e:
                    return None, None, None, f"Evaluation error in {eq_str}: {e}"

        return None, None, None, None

    def execute_reasoning(
        self,
        composed_system: ComposedSystem,
        trace_id: Optional[str] = None,
    ) -> ReasoningTrace:
        """
        Executes multi-step substitution, dimensional validation, and dependency tracing.
        """
        tid = trace_id or f"trc-{uuid.uuid4().hex[:8]}"
        steps: List[str] = []
        calculated_values: Dict[str, Any] = {}
        inferred_premises: List[str] = []
        dependency_dag: Dict[str, List[str]] = {}
        execution_error: Optional[str] = None

        # Check for upstream conflicts recorded by Composer
        if "_conflicts" in composed_system.boundary_limits:
            conflicts = composed_system.boundary_limits["_conflicts"]
            for conf in conflicts:
                steps.append(f"Constraint Warning: {conf}")

        # 1. Load known boundary parameters
        known_numeric: Dict[str, float] = {}
        known_units: Dict[str, str] = {}

        for k, v in composed_system.boundary_limits.items():
            if k.startswith("_"):
                continue
            val_f, unit = self.parse_numeric_parameter(v)
            if val_f is not None:
                known_numeric[k] = val_f
                known_units[k] = unit or ""
                calculated_values[k] = f"{val_f} {unit}".strip()
                steps.append(f"Loaded boundary parameter: {k} = {val_f} {unit}".strip())
                dependency_dag[k] = []

        # 2. Iteratively solve coupled equations
        max_passes = 4
        equations = list(composed_system.coupled_equations)
        for pass_num in range(max_passes):
            solved_any = False
            for eq in equations:
                var, val, unit, explanation = self.solve_equation(eq, known_numeric, known_units)
                if var and val is not None:
                    known_numeric[var] = val
                    known_units[var] = unit or ""
                    val_display = f"{val:.4g} {unit}".strip()
                    calculated_values[var] = val_display
                    steps.append(f"Derived: {explanation}")
                    inferred_premises.append(f"{var} = {val_display}")
                    
                    # Build DAG dependencies
                    rhs_part = eq.split("=")[1] if "=" in eq else eq
                    tokens = [tok for tok in VAR_TOKEN_PATTERN.findall(rhs_part) if tok in known_numeric and tok != var]
                    dependency_dag[var] = tokens
                    
                    solved_any = True

            if not solved_any:
                break

        # 3. Add premise statements from claims
        for claim in composed_system.claims:
            if claim.statement not in inferred_premises:
                inferred_premises.append(claim.statement)

        # 4. Check if expected target variables were resolved
        unresolved_targets = [k for k in composed_system.unified_variables.keys() if k not in known_numeric]
        if unresolved_targets:
            steps.append(f"No quantitative equation path resolved for target variables: {unresolved_targets}")

        return ReasoningTrace(
            trace_id=tid,
            steps=steps,
            calculated_values=calculated_values,
            inferred_premises=inferred_premises[:6],
            dependency_dag=dependency_dag,
            execution_error=execution_error,
        )

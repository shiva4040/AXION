from typing import Dict, Tuple, Optional, Set
import sympy as sp
from axion.simple_tester.types import (
    SIDimension, SI_DIMENSIONLESS, COMMON_DIMENSIONS_CATALOG
)

class DimensionalAnalyzer:
    """
    Component 4 Subsystem:
    Rigorous SI Base Dimensional Analysis for scientific equations and terms.
    Enforces dimensional homogeneity across addition, subtraction, and equality.
    """

    def __init__(self, variable_dimensions: Optional[Dict[str, SIDimension]] = None):
        self.var_dims: Dict[str, SIDimension] = dict(COMMON_DIMENSIONS_CATALOG)
        if variable_dimensions:
            self.var_dims.update(variable_dimensions)

    def register_dimension(self, symbol: str, dimension: SIDimension):
        self.var_dims[symbol.lower()] = dimension

    def get_expression_dimension(
        self,
        expr: sp.Expr
    ) -> Tuple[Optional[SIDimension], Optional[str]]:
        """
        Recursively derives the SI dimension vector for a SymPy expression.
        Returns (dimension, error_message).
        """
        # Case 1: Numeric constant -> Dimensionless
        if expr.is_Number:
            return SI_DIMENSIONLESS, None

        # Case 2: Atomic Symbol
        if expr.is_Symbol:
            sym_name = str(expr).lower()
            if sym_name in self.var_dims:
                return self.var_dims[sym_name], None
            return None, f"Unknown physical dimension for variable '{expr}'. Missing unit definition."

        # Case 3: Multiplication (Mul) -> Add dimensions
        if expr.is_Mul:
            total_dim = SI_DIMENSIONLESS
            for arg in expr.args:
                dim, err = self.get_expression_dimension(arg)
                if err or dim is None:
                    return None, err
                total_dim = total_dim.multiply(dim)
            return total_dim, None

        # Case 4: Addition / Subtraction (Add) -> All terms MUST have identical dimensions
        if expr.is_Add:
            first_dim = None
            first_arg = None
            for arg in expr.args:
                dim, err = self.get_expression_dimension(arg)
                if err or dim is None:
                    return None, err
                if first_dim is None:
                    first_dim = dim
                    first_arg = arg
                else:
                    if dim != first_dim:
                        return None, (
                            f"Dimensional inconsistency in addition: term '{first_arg}' has dimension "
                            f"{first_dim.to_formula_string()} but term '{arg}' has dimension {dim.to_formula_string()}."
                        )
            return first_dim, None

        # Case 5: Power (Pow) -> base^exponent
        if expr.is_Pow:
            base, exponent = expr.args
            base_dim, err = self.get_expression_dimension(base)
            if err or base_dim is None:
                return None, err
            
            # Exponent must be dimensionless and numeric integer
            if not exponent.is_Number:
                exp_dim, err = self.get_expression_dimension(exponent)
                if err or not exp_dim.is_dimensionless():
                    return None, f"Non-dimensionless exponent in power expression: {expr}"
            
            try:
                exp_val = float(exponent)
                if exp_val.is_integer():
                    return base_dim.power(int(exp_val)), None
                # Fractional power (e.g. square root)
                # Check if all base dimensions are divisible by the denominator
                frac = sp.Rational(exponent)
                num, denom = frac.p, frac.q
                if all(d % denom == 0 for d in [
                    base_dim.mass, base_dim.length, base_dim.time, base_dim.current,
                    base_dim.temperature, base_dim.amount, base_dim.luminosity
                ]):
                    return SIDimension(
                        mass=int(base_dim.mass * num / denom),
                        length=int(base_dim.length * num / denom),
                        time=int(base_dim.time * num / denom),
                        current=int(base_dim.current * num / denom),
                        temperature=int(base_dim.temperature * num / denom),
                        amount=int(base_dim.amount * num / denom),
                        luminosity=int(base_dim.luminosity * num / denom)
                    ), None
                return None, f"Fractional power yields non-integer SI dimensions: {expr}"
            except Exception as e:
                return None, f"Unable to compute power dimension for {expr}: {str(e)}"

        return None, f"Unsupported mathematical operator for dimensional analysis: {type(expr)}"

    def verify_equation_homogeneity(
        self,
        equation_str: str,
        custom_dimensions: Optional[Dict[str, SIDimension]] = None
    ) -> Tuple[bool, Optional[SIDimension], Optional[SIDimension], Optional[str]]:
        """
        Verifies that LHS and RHS of an equation have identical SI dimensions.
        Returns: (is_homogeneous, lhs_dimension, rhs_dimension, error_or_explanation)
        """
        if custom_dimensions:
            self.var_dims.update(custom_dimensions)

        from axion.simple_tester.symbolic import SymbolicVerifier
        lhs, rhs, parse_err = SymbolicVerifier.parse_equation(equation_str)
        if parse_err or lhs is None or rhs is None:
            return False, None, None, parse_err

        lhs_dim, err_lhs = self.get_expression_dimension(lhs)
        if err_lhs or lhs_dim is None:
            return False, None, None, f"LHS dimension error: {err_lhs}"

        rhs_dim, err_rhs = self.get_expression_dimension(rhs)
        if err_rhs or rhs_dim is None:
            return False, lhs_dim, None, f"RHS dimension error: {err_rhs}"

        if lhs_dim == rhs_dim:
            return True, lhs_dim, rhs_dim, f"Dimensionally consistent: both sides reduce to {lhs_dim.to_formula_string()}."
        else:
            return False, lhs_dim, rhs_dim, (
                f"Dimensional mismatch: LHS has dimension {lhs_dim.to_formula_string()} "
                f"while RHS has dimension {rhs_dim.to_formula_string()}."
            )

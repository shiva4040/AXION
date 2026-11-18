from typing import Tuple, Optional, Dict, Any
import sympy as sp

class SymbolicVerifier:
    """
    Component 4 Subsystem:
    Symbolic mathematical parsing, algebraic reduction, and equivalence checking via SymPy.
    """

    @classmethod
    def _get_symbol_namespace(cls) -> Dict[str, Any]:
        """
        Overrides SymPy built-in single-letter constants that conflict with
        standard physical parameters:
        - E (Energy vs. Euler's number)
        - I (Current vs. Imaginary unit sqrt(-1))
        - N (Normal force / turns vs. numeric eval)
        - O (Order vs. Big-O)
        """
        import string
        namespace: Dict[str, Any] = {}
        for char in string.ascii_letters:
            namespace[char] = sp.Symbol(char)
        # Also common multi-character subscripts
        for var in ["P_solar", "P_demand", "P_req", "V_oc", "F_drag", "F_roll", "T_kelvin"]:
            namespace[var] = sp.Symbol(var)
        return namespace

    @classmethod
    def parse_equation(cls, equation_str: str) -> Tuple[Optional[sp.Expr], Optional[sp.Expr], Optional[str]]:
        """
        Parses an equation string into (LHS, RHS, error_message).
        Accepts: "E = m * c**2", "P - F * v = 0", "V = I * R"
        """
        try:
            if "=" in equation_str:
                parts = equation_str.split("=")
                if len(parts) != 2:
                    return None, None, f"Equation has multiple '=' signs: {equation_str}"
                lhs_str, rhs_str = parts[0].strip(), parts[1].strip()
            else:
                lhs_str = equation_str.strip()
                rhs_str = "0"

            local_ns = cls._get_symbol_namespace()
            lhs = sp.parse_expr(lhs_str, local_dict=local_ns, evaluate=False)
            rhs = sp.parse_expr(rhs_str, local_dict=local_ns, evaluate=False)
            return lhs, rhs, None
        except Exception as e:
            return None, None, f"SymPy parsing error in '{equation_str}': {str(e)}"

    @classmethod
    def check_equivalence(
        cls,
        equation_str: str,
        substitutions: Optional[Dict[str, str]] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Checks whether LHS - RHS simplifies identically to zero.
        Optionally applies variable substitutions (e.g. {'F': 'm * a'}).
        """
        lhs, rhs, error = cls.parse_equation(equation_str)
        if error or lhs is None or rhs is None:
            return False, error

        try:
            diff = lhs - rhs

            # Apply substitutions if provided
            if substitutions:
                sub_dict = {}
                for k, v in substitutions.items():
                    sub_sym = sp.Symbol(k)
                    sub_val = sp.parse_expr(v)
                    sub_dict[sub_sym] = sub_val
                diff = diff.subs(sub_dict)

            simplified = sp.simplify(diff)
            is_zero = bool(simplified == 0)

            if is_zero:
                return True, "Algebraic identity confirmed: LHS - RHS simplifies identically to 0."
            else:
                return False, f"Algebraic contradiction: LHS - RHS simplifies to '{simplified}' != 0."
        except Exception as e:
            return False, f"Symbolic reduction failed: {str(e)}"

    @classmethod
    def check_expressions_equal(cls, expr_a_str: str, expr_b_str: str) -> Tuple[bool, str]:
        """Checks whether two mathematical expressions are algebraically identical."""
        try:
            ea = sp.parse_expr(expr_a_str)
            eb = sp.parse_expr(expr_b_str)
            diff = sp.simplify(ea - eb)
            if diff == 0:
                return True, "Expressions are algebraically identical."
            return False, f"Expressions differ by: {diff}"
        except Exception as e:
            return False, f"Parsing failure: {str(e)}"

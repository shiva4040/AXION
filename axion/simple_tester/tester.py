from typing import Optional, Dict, List
from axion.simple_tester.types import (
    ValidationVerdict, ValidationResult, SIDimension, PhysicalConstraint
)
from axion.simple_tester.symbolic import SymbolicVerifier
from axion.simple_tester.dimensional import DimensionalAnalyzer
from axion.simple_tester.constraints import PhysicalConstraintValidator

class SimpleHypothesisTester:
    """
    Component 4: Simple Hypothesis Tester
    Unified scientific validation engine for symbolic reduction,
    SI base dimensional analysis, and physical boundary constraints.
    """

    def __init__(
        self,
        variable_dimensions: Optional[Dict[str, SIDimension]] = None,
        custom_constraints: Optional[List[PhysicalConstraint]] = None
    ):
        self.dim_analyzer = DimensionalAnalyzer(variable_dimensions)
        self.constraint_validator = PhysicalConstraintValidator(custom_constraints)

    def validate_equation(
        self,
        equation_str: str,
        custom_dimensions: Optional[Dict[str, SIDimension]] = None,
        variable_values: Optional[Dict[str, float]] = None,
        substitutions: Optional[Dict[str, str]] = None,
        custom_constraints: Optional[List[PhysicalConstraint]] = None
    ) -> ValidationResult:
        """
        Executes complete scientific validation of an equation across:
        1. Parseability & Algebraic Simplification (SymPy)
        2. SI Base Dimensional Homogeneity
        3. Physical Boundary Constraints
        """
        failed_conditions: List[str] = []
        
        # Step 1: Symbolic Parsing
        lhs, rhs, parse_err = SymbolicVerifier.parse_equation(equation_str)
        if parse_err:
            return ValidationResult(
                verdict=ValidationVerdict.INVALID,
                equation_checked=equation_str,
                is_symbolically_valid=False,
                is_dimensionally_valid=False,
                failed_conditions=[parse_err],
                explanation=f"Mathematical parsing failed: {parse_err}"
            )

        # Step 2: Dimensional Analysis
        is_dim_valid, lhs_dim, rhs_dim, dim_msg = self.dim_analyzer.verify_equation_homogeneity(
            equation_str=equation_str,
            custom_dimensions=custom_dimensions
        )

        lhs_dim_str = lhs_dim.to_formula_string() if lhs_dim else "Unknown"
        rhs_dim_str = rhs_dim.to_formula_string() if rhs_dim else "Unknown"

        # Check for missing dimension info
        if dim_msg and "Unknown physical dimension" in dim_msg:
            return ValidationResult(
                verdict=ValidationVerdict.INSUFFICIENT_INFORMATION,
                equation_checked=equation_str,
                is_symbolically_valid=None,
                is_dimensionally_valid=False,
                lhs_dimension=lhs_dim_str,
                rhs_dimension=rhs_dim_str,
                failed_conditions=[dim_msg],
                explanation=f"Insufficient information to verify units: {dim_msg}"
            )

        if not is_dim_valid:
            failed_conditions.append(dim_msg or "Dimensional mismatch between LHS and RHS")

        # Step 3: Physical Boundary Constraints (if values provided)
        constraints_evaluated = 0
        if variable_values:
            if custom_constraints:
                for cc in custom_constraints:
                    self.constraint_validator.register_constraint(cc)
            
            c_passed, c_failed, c_msg = self.constraint_validator.evaluate_values(variable_values)
            constraints_evaluated = len(variable_values)
            if not c_passed:
                failed_conditions.extend(c_failed)

        # Step 4: Symbolic Equivalence (if identity test is requested with substitutions)
        is_sym_valid = True
        if substitutions:
            is_sym_valid, sym_msg = SymbolicVerifier.check_equivalence(equation_str, substitutions)
            if not is_sym_valid:
                failed_conditions.append(sym_msg)

        # Determine Verdict
        if failed_conditions:
            verdict = ValidationVerdict.INVALID
            explanation = f"Validation failed with {len(failed_conditions)} issue(s): " + "; ".join(failed_conditions)
        else:
            verdict = ValidationVerdict.VALID
            explanation = (
                f"Equation '{equation_str}' is dimensionally homogeneous ({lhs_dim_str}) "
                f"and satisfies all {constraints_evaluated} evaluated boundary constraints."
            )

        return ValidationResult(
            verdict=verdict,
            equation_checked=equation_str,
            is_symbolically_valid=is_sym_valid,
            is_dimensionally_valid=is_dim_valid,
            lhs_dimension=lhs_dim_str,
            rhs_dimension=rhs_dim_str,
            constraints_evaluated=constraints_evaluated,
            failed_conditions=failed_conditions,
            explanation=explanation
        )

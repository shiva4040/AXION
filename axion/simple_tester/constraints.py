from typing import List, Dict, Tuple, Optional, Any
from axion.simple_tester.types import PhysicalConstraint

class PhysicalConstraintValidator:
    """
    Component 4 Subsystem:
    Evaluates physical boundary limits and configurable constraints.
    Prevents unphysical states (efficiency > 1.0, negative absolute temperature, etc.).
    """

    def __init__(self, custom_constraints: Optional[List[PhysicalConstraint]] = None):
        self.constraints: List[PhysicalConstraint] = [
            # Standard Thermodynamic & Kinematic Default Constraints
            PhysicalConstraint(
                variable_symbol="efficiency",
                description="Thermodynamic conversion efficiency must be in [0, 1]",
                min_value=0.0,
                max_value=1.0
            ),
            PhysicalConstraint(
                variable_symbol="eta",
                description="Efficiency factor η must be in [0, 1]",
                min_value=0.0,
                max_value=1.0
            ),
            PhysicalConstraint(
                variable_symbol="eta_pv",
                description="Photovoltaic efficiency must be in [0, 1]",
                min_value=0.0,
                max_value=1.0
            ),
            PhysicalConstraint(
                variable_symbol="t_kelvin",
                description="Absolute temperature must be non-negative (T >= 0 K)",
                min_value=0.0,
                max_value=None
            ),
            PhysicalConstraint(
                variable_symbol="temperature",
                description="Thermodynamic temperature must be >= 0 K",
                min_value=0.0,
                max_value=None
            ),
            PhysicalConstraint(
                variable_symbol="mass",
                description="Physical mass must be strictly positive",
                min_value=0.0,
                max_value=None,
                allow_equal_min=False
            ),
            PhysicalConstraint(
                variable_symbol="velocity",
                description="Speed cannot exceed speed of light c (299,792,458 m/s)",
                min_value=0.0,
                max_value=299792458.0
            ),
            PhysicalConstraint(
                variable_symbol="v",
                description="Velocity magnitude cannot exceed speed of light",
                min_value=0.0,
                max_value=299792458.0
            )
        ]
        if custom_constraints:
            self.constraints.extend(custom_constraints)

    def register_constraint(self, constraint: PhysicalConstraint):
        self.constraints.append(constraint)

    def evaluate_values(
        self,
        variable_values: Dict[str, float]
    ) -> Tuple[bool, List[str], str]:
        """
        Validates a dictionary of variable values against active constraints.
        Returns (all_passed, list_of_failed_conditions, explanation).
        """
        failed: List[str] = []
        normalized_values = {k.lower(): v for k, v in variable_values.items()}

        for c in self.constraints:
            sym = c.variable_symbol.lower()
            if sym in normalized_values:
                val = normalized_values[sym]
                
                # Check minimum bound
                if c.min_value is not None:
                    if c.allow_equal_min:
                        if val < c.min_value:
                            failed.append(
                                f"Boundary violation: '{c.variable_symbol}' = {val} is below minimum {c.min_value}. ({c.description})"
                            )
                    else:
                        if val <= c.min_value:
                            failed.append(
                                f"Boundary violation: '{c.variable_symbol}' = {val} must be strictly greater than {c.min_value}. ({c.description})"
                            )

                # Check maximum bound
                if c.max_value is not None:
                    if c.allow_equal_max:
                        if val > c.max_value:
                            failed.append(
                                f"Boundary violation: '{c.variable_symbol}' = {val} exceeds maximum {c.max_value}. ({c.description})"
                            )
                    else:
                        if val >= c.max_value:
                            failed.append(
                                f"Boundary violation: '{c.variable_symbol}' = {val} must be strictly less than {c.max_value}. ({c.description})"
                            )

        if not failed:
            return True, [], f"All {len(normalized_values)} variable values satisfy active physical constraints."
        else:
            return False, failed, f"Physical constraint check failed with {len(failed)} violation(s)."

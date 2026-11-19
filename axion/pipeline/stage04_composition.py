import uuid
import logging
from typing import Any, Dict, List, Optional, Set, Tuple

from axion.pipeline.types import (
    ComposedSystem,
    ExtractedClaim,
    QuestionSpec,
)

logger = logging.getLogger(__name__)

# Canonical variable synonyms map (lower-cased -> canonical concept)
CANONICAL_VARIABLE_MAP: Dict[str, str] = {
    "v": "voltage",
    "voltage": "voltage",
    "potential": "voltage",
    "electric_potential": "voltage",
    "i": "current",
    "current": "current",
    "r": "resistance",
    "resistance": "resistance",
    "p": "power",
    "power": "power",
    "solar_power": "solar_power",
    "mechanical_demand": "mechanical_demand",
    "f": "force",
    "force": "force",
    "drag_force": "drag_force",
    "m": "mass",
    "mass": "mass",
    "a": "acceleration",
    "acceleration": "acceleration",
    "v_velocity": "velocity",
    "velocity": "velocity",
    "vehicle_velocity": "velocity",
    "speed": "velocity",
    "t": "temperature",
    "temperature": "temperature",
    "pressure": "pressure",
    "delta_p": "pressure_difference",
    "area": "area",
    "solar_irradiance": "solar_irradiance",
    "efficiency": "efficiency",
}

# Incompatible qualitative condition pairs
INCOMPATIBLE_CONDITION_PAIRS: List[Tuple[str, str]] = [
    ("laminar", "turbulent"),
    ("steady", "unsteady"),
    ("steady-state", "transient"),
    ("incompressible", "compressible"),
    ("ac", "dc"),
]


class MinimalKnowledgeComposer:
    """
    Stage 04: Minimal Knowledge Composer.
    Connects extracted claims into a unified, typed system of equations,
    harmonized variables, active assumptions, and boundary limits.
    """

    def __init__(self):
        pass

    def harmonize_variables(
        self,
        claims: List[ExtractedClaim],
        question_spec: QuestionSpec,
    ) -> Dict[str, str]:
        """
        Maps variable tokens across claims and query specifications
        to their canonical physical/scientific concepts.
        """
        unified: Dict[str, str] = {}

        # 1. Add target variables from question spec
        for var in question_spec.target_variables:
            var_key = var.strip()
            canonical = CANONICAL_VARIABLE_MAP.get(var_key.lower(), var_key)
            unified[var_key] = canonical

        # 2. Add variables from declared parameters
        for var in question_spec.declared_parameters.keys():
            var_key = var.strip()
            canonical = CANONICAL_VARIABLE_MAP.get(var_key.lower(), var_key)
            unified[var_key] = canonical

        # 3. Add variables extracted from claims
        for claim in claims:
            for v in claim.variables:
                v_clean = v.strip()
                if v_clean not in unified:
                    canonical = CANONICAL_VARIABLE_MAP.get(v_clean.lower(), v_clean)
                    unified[v_clean] = canonical

        return unified

    def detect_conflicts(
        self,
        assumptions: List[str],
    ) -> List[str]:
        """Scans active assumptions for mutually exclusive or conflicting physical regimes."""
        conflicts: List[str] = []
        assump_lower = [a.lower() for a in assumptions]

        for term_a, term_b in INCOMPATIBLE_CONDITION_PAIRS:
            has_a = any(term_a in a for a in assump_lower)
            has_b = any(term_b in a for a in assump_lower)
            if has_a and has_b:
                conflicts.append(
                    f"Conflicting assumptions detected: mutually exclusive regimes '{term_a}' and '{term_b}'"
                )

        return conflicts

    def compose_system(
        self,
        claims: List[ExtractedClaim],
        question_spec: QuestionSpec,
        system_id: Optional[str] = None,
    ) -> ComposedSystem:
        """
        Executes Stage 04 Knowledge Composition across extracted claims.
        """
        sid = system_id or f"sys-{uuid.uuid4().hex[:8]}"

        # 1. Variable harmonization
        unified_vars = self.harmonize_variables(claims, question_spec)

        # 2. Equation collection & deduplication
        equations: List[str] = []
        seen_eqs: Set[str] = set()
        for c in claims:
            for eq in c.equations:
                eq_clean = eq.strip()
                if eq_clean and eq_clean not in seen_eqs:
                    seen_eqs.add(eq_clean)
                    equations.append(eq_clean)

        # 3. Union of active assumptions and conditions
        assumptions: List[str] = []
        for c in claims:
            for cond in c.conditions:
                if cond not in assumptions:
                    assumptions.append(cond)

        if question_spec.identified_constraints:
            for k, v in question_spec.identified_constraints.items():
                constraint_str = f"{k}: {v}"
                if constraint_str not in assumptions:
                    assumptions.append(constraint_str)

        # 4. Conflict detection
        conflicts = self.detect_conflicts(assumptions)

        # 5. Boundary limits
        boundary_limits: Dict[str, Any] = dict(question_spec.declared_parameters)
        if conflicts:
            boundary_limits["_conflicts"] = conflicts

        # 6. Participating domains
        domains = list(dict.fromkeys(question_spec.domain_tags))

        return ComposedSystem(
            system_id=sid,
            unified_variables=unified_vars,
            active_assumptions=assumptions,
            coupled_equations=equations,
            claims=claims,
            boundary_limits=boundary_limits,
            participating_domains=domains,
        )

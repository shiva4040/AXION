import re
from typing import Dict, List, Optional, Tuple
from axion.transfer.types import (
    ApplicabilityCheckStage,
    ApplicabilityEvaluation,
    ApplicabilityVerdict,
    BoundaryConstraint,
    CandidateTransfer,
    DomainConcept,
    DomainKnowledgeBundle,
    DomainRelation,
)
from axion.core.types import EpistemicTier, RelationType
from axion.simple_tester.types import SIDimension, COMMON_DIMENSIONS_CATALOG
from axion.simple_tester.tester import SimpleHypothesisTester
from axion.reasoning.contradiction import OPPOSING_RELATIONS

MUTUALLY_EXCLUSIVE_ASSUMPTIONS = {
    "linear": ["non_linear", "nonlinear", "shock_discontinuity", "turbulent"],
    "laminar_flow": ["turbulent_flow", "turbulent", "shock_discontinuity"],
    "continuum_hypothesis": ["discrete_molecular", "rarefied_gas", "knudsen_regime", "wavefunction_collapse", "quantum"],
    "ideal_gas": ["real_gas", "van_der_waals", "incompressible_liquid"],
    "ohmic_conduction": ["non_ohmic", "space_charge_limited", "superconducting", "relativistic", "v_near_c"],
    "steady_state": ["transient", "unsteady", "time_dependent"],
    "reversibility": ["irreversible", "dissipative"],
    "isotropic": ["anisotropic"],
    "non_relativistic": ["relativistic", "v_near_c"],
    "wavefunction_collapse": ["continuum_hypothesis", "classical_continuum", "laminar_flow", "newtonian_fluid"],
    "macroscopic_quantum_coherence": ["classical", "newtonian_fluid", "viscous", "dissipative"],
    "conservative_flux": ["non_conservative_flux", "dissipative_divergence"],
}

def parse_si_formula(formula: str) -> Optional[SIDimension]:
    """
    Parses strings like '[M][L]2[T]-3[I]-1' or '[M] [L]^2 [T]^-2' into an SIDimension.
    """
    if not formula:
        return None
    formula = formula.strip()
    if formula == "[1]" or formula.lower() == "dimensionless":
        return SIDimension()

    dim_map = {"M": "mass", "L": "length", "T": "time", "I": "current", "Θ": "temperature", "N": "amount", "J": "luminosity"}
    res = SIDimension()
    # Pattern: [X] or [X]^k or [X]k or [X]^-k or [X]-k
    pattern = r'\[([MLTIΘNJ])\](?:\^?(-?\d+))?'
    matches = re.findall(pattern, formula)
    if not matches:
        return None

    for base, exp_str in matches:
        attr = dim_map.get(base)
        if attr:
            exp = int(exp_str) if exp_str else 1
            setattr(res, attr, getattr(res, attr) + exp)

    return res

class ApplicabilityGuard:
    """
    Component 6 Hard Validation Gate:
    Rigorously verifies candidate cross-domain transfers across 5 distinct stages:
    1. Structural Compatibility in target domain
    2. Variable Correspondence & Dimensional Homogeneity (SI units)
    3. Physical Foundations and Assumptions
    4. Boundary Operating Conditions
    5. Target Domain Empirical Contradiction Check
    """

    def __init__(self, tester: Optional[SimpleHypothesisTester] = None):
        self.tester = tester or SimpleHypothesisTester()

    def evaluate_transfer(
        self,
        candidate: CandidateTransfer,
        target_bundle: DomainKnowledgeBundle,
    ) -> ApplicabilityEvaluation:
        stage_results: List[ApplicabilityCheckStage] = []
        violations: List[str] = []
        conditions_required: List[str] = []
        is_insufficient_info = False

        # --- Stage 1: Structural Compatibility ---
        s1_passed, s1_details, s1_diag = self._check_structural_compatibility(candidate, target_bundle)
        stage_results.append(ApplicabilityCheckStage(stage_name="structural_compatibility", passed=s1_passed, details=s1_details, diagnostics=s1_diag))
        if not s1_passed:
            violations.append(f"Structural incompatibility: {s1_details}")

        # --- Stage 2: Variable Correspondence & Dimensional Homogeneity ---
        s2_passed, s2_details, s2_diag, s2_missing = self._check_dimensional_homogeneity(candidate, target_bundle)
        stage_results.append(ApplicabilityCheckStage(stage_name="dimensional_homogeneity", passed=s2_passed, details=s2_details, diagnostics=s2_diag))
        if not s2_passed:
            if s2_missing:
                is_insufficient_info = True
            else:
                violations.append(f"Dimensional violation: {s2_details}")

        # --- Stage 3: Physical Assumptions Check ---
        s3_passed, s3_details, s3_diag, s3_conds, s3_viols = self._check_physical_assumptions(candidate, target_bundle)
        stage_results.append(ApplicabilityCheckStage(stage_name="physical_assumptions", passed=s3_passed, details=s3_details, diagnostics=s3_diag))
        if not s3_passed:
            violations.extend(s3_viols)
        conditions_required.extend(s3_conds)

        # --- Stage 4: Boundary Conditions Check ---
        s4_passed, s4_details, s4_diag, s4_conds, s4_viols = self._check_boundary_conditions(candidate, target_bundle)
        stage_results.append(ApplicabilityCheckStage(stage_name="boundary_conditions", passed=s4_passed, details=s4_details, diagnostics=s4_diag))
        if not s4_passed:
            violations.extend(s4_viols)
        conditions_required.extend(s4_conds)

        # --- Stage 5: Target Empirical Contradiction Check ---
        s5_passed, s5_details, s5_diag = self._check_target_contradictions(candidate, target_bundle)
        stage_results.append(ApplicabilityCheckStage(stage_name="contradiction_check", passed=s5_passed, details=s5_details, diagnostics=s5_diag))
        if not s5_passed:
            violations.append(f"Contradicts established empirical target evidence: {s5_details}")

        # --- Final Verdict Formulation ---
        passed_stages = [s.stage_name for s in stage_results if s.passed]
        failed_stages = [s.stage_name for s in stage_results if not s.passed]

        if len(violations) > 0:
            verdict = ApplicabilityVerdict.REJECTED
            confidence = 0.95
            rationale = f"Transfer REJECTED due to {len(violations)} fundamental violation(s): {'; '.join(violations)}."
        elif is_insufficient_info:
            verdict = ApplicabilityVerdict.INSUFFICIENT_INFORMATION
            confidence = 0.50
            rationale = "Transfer cannot be conclusively verified due to missing variable dimensions or parameters."
        elif len(conditions_required) > 0:
            verdict = ApplicabilityVerdict.CONDITIONAL
            confidence = 0.85
            rationale = (
                f"Transfer conditionally accepted subject to {len(conditions_required)} constraint(s): "
                f"{'; '.join(conditions_required)}."
            )
        else:
            verdict = ApplicabilityVerdict.ACCEPTED
            confidence = 0.95
            rationale = "Transfer structurally, dimensionally, physically, and empirically verified within target domain."

        return ApplicabilityEvaluation(
            transfer_id=candidate.transfer_id,
            verdict=verdict,
            confidence=confidence,
            passed_stages=passed_stages,
            failed_stages=failed_stages,
            stage_results=stage_results,
            conditions_required=conditions_required,
            violations=violations,
            rationale=rationale,
        )

    def _check_structural_compatibility(
        self, candidate: CandidateTransfer, target_bundle: DomainKnowledgeBundle
    ) -> Tuple[bool, str, Dict]:
        target_concept_names = {c.name for c in target_bundle.concepts}
        if candidate.proposed_source_concept not in target_concept_names:
            return False, f"Proposed source concept '{candidate.proposed_source_concept}' missing in target domain.", {}
        if candidate.proposed_target_concept not in target_concept_names:
            return False, f"Proposed target concept '{candidate.proposed_target_concept}' missing in target domain.", {}
        return True, "Proposed concepts structurally present in target domain.", {
            "source_concept": candidate.proposed_source_concept,
            "target_concept": candidate.proposed_target_concept,
        }

    def _check_dimensional_homogeneity(
        self, candidate: CandidateTransfer, target_bundle: DomainKnowledgeBundle
    ) -> Tuple[bool, str, Dict, bool]:
        """Verifies SI dimensional homogeneity of candidate equation."""
        if not candidate.proposed_equation:
            # Relational transfer without equation: structurally compatible
            return True, "No equation associated with candidate transfer (pure relational projection).", {}, False

        # Gather dimensional catalog for target variables
        dim_catalog: Dict[str, SIDimension] = dict(COMMON_DIMENSIONS_CATALOG)
        for c in target_bundle.concepts:
            if c.symbol and c.si_dimension:
                parsed_dim = parse_si_formula(c.si_dimension)
                if parsed_dim:
                    dim_catalog[c.symbol.lower()] = parsed_dim
                    dim_catalog[c.symbol] = parsed_dim

        # Check equation through SimpleHypothesisTester
        res = self.tester.validate_equation(
            candidate.proposed_equation,
            custom_dimensions=dim_catalog,
        )

        if res.is_dimensionally_valid is True:
            return True, f"Dimensionally homogeneous: [{res.lhs_dimension}] == [{res.rhs_dimension}].", {
                "lhs": res.lhs_dimension, "rhs": res.rhs_dimension
            }, False
        elif res.is_dimensionally_valid is False:
            return False, f"Dimensional mismatch: LHS [{res.lhs_dimension}] != RHS [{res.rhs_dimension}].", {
                "lhs": res.lhs_dimension, "rhs": res.rhs_dimension, "failed": res.failed_conditions
            }, False
        else:
            return False, f"Missing dimensional definitions for equation variables: {res.explanation}", {
                "equation": candidate.proposed_equation
            }, True

    def _check_physical_assumptions(
        self, candidate: CandidateTransfer, target_bundle: DomainKnowledgeBundle
    ) -> Tuple[bool, str, Dict, List[str], List[str]]:
        violations: List[str] = []
        conditions_required: List[str] = []

        source_assumptions = candidate.source_relation.assumptions_required
        target_assumptions = set(a.lower() for a in target_bundle.assumptions)

        for s_assump in source_assumptions:
            s_clean = s_assump.lower().replace(" ", "_")
            # Check if target domain explicitly has an opposing / mutually exclusive assumption
            conflicting_target_assumps = MUTUALLY_EXCLUSIVE_ASSUMPTIONS.get(s_clean, [])
            for conf in conflicting_target_assumps:
                if conf in target_assumptions:
                    violations.append(
                        f"Source assumption '{s_assump}' contradicts target domain condition '{conf}'."
                    )

            # If not violated, but target does not explicitly list it, it becomes a conditional requirement
            if s_clean not in target_assumptions and not violations:
                conditions_required.append(f"Requires target domain to satisfy assumption: '{s_assump}'")

        if violations:
            return False, f"Assumption conflict(s): {'; '.join(violations)}", {"violations": violations}, conditions_required, violations
        return True, "Physical assumptions compatible or conditionally scoped.", {}, conditions_required, []

    def _check_boundary_conditions(
        self, candidate: CandidateTransfer, target_bundle: DomainKnowledgeBundle
    ) -> Tuple[bool, str, Dict, List[str], List[str]]:
        violations: List[str] = []
        conditions: List[str] = []

        for bc in target_bundle.boundary_conditions:
            if bc.variable_name in candidate.mapped_symbols.values() or bc.variable_name in candidate.mapped_concept_names.values():
                conditions.append(
                    f"Operational limit: {bc.variable_name} must respect [{bc.min_value} to {bc.max_value}] {bc.unit or ''}"
                )

        return True, "Boundary conditions recorded.", {}, conditions, violations

    def _check_target_contradictions(
        self, candidate: CandidateTransfer, target_bundle: DomainKnowledgeBundle
    ) -> Tuple[bool, str, Dict]:
        """
        Checks if the target domain already has established empirical facts or relations
        that directly contradict the proposed candidate relation.
        """
        proposed_rel_val = candidate.proposed_relation_type.value if hasattr(candidate.proposed_relation_type, "value") else str(candidate.proposed_relation_type)
        opposing_type = OPPOSING_RELATIONS.get(proposed_rel_val)

        if not opposing_type:
            return True, "No opposing relation types defined for candidate relation.", {}

        for t_rel in target_bundle.relations:
            # Check concept pair (including reverse pair for symmetric relations)
            t_rel_val = t_rel.relation_type.value if hasattr(t_rel.relation_type, "value") else str(t_rel.relation_type)
            pair_match = (
                (t_rel.source_concept == candidate.proposed_source_concept and t_rel.target_concept == candidate.proposed_target_concept)
                or (
                    proposed_rel_val in [RelationType.PROPORTIONAL_TO.value, RelationType.INVERSELY_PROPORTIONAL_TO.value]
                    and t_rel.source_concept == candidate.proposed_target_concept
                    and t_rel.target_concept == candidate.proposed_source_concept
                )
            )
            if pair_match and t_rel_val == opposing_type:
                return False, (
                    f"Target domain already contains documented relation '{t_rel.source_concept}' "
                    f"-[{t_rel.relation_type}]-> '{t_rel.target_concept}' (tier {t_rel.epistemic_tier}), "
                    f"which contradicts proposed [{candidate.proposed_relation_type}]."
                ), {"conflicting_relation": t_rel.model_dump()}

        return True, "No conflicting relations found in target domain.", {}

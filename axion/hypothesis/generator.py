import uuid
from typing import List, Optional
from axion.core.types import EpistemicTier, ProvenancePointer
from axion.transfer.types import (
    ApplicabilityEvaluation,
    ApplicabilityVerdict,
    CandidateTransfer,
    TransferRecord,
)
from axion.hypothesis.types import (
    ExperimentProposal,
    ExperimentType,
    StructuredHypothesis,
)

class HypothesisGenerator:
    """
    Component 7: Hypothesis Generator.
    Synthesizes formal, falsifiable scientific hypotheses from accepted and conditional
    cross-domain transfers and multi-domain composed systems.
    Enforces strict epistemic demarcation (HYPOTHESIS_CONJECTURED).
    """

    def generate_hypotheses_from_transfer_record(
        self,
        record: TransferRecord,
        include_conditional: bool = True,
    ) -> List[StructuredHypothesis]:
        hypotheses: List[StructuredHypothesis] = []

        # Map candidate transfers to their evaluations
        eval_map = {e.transfer_id: e for e in record.evaluations}

        qualifying_candidates: List[CandidateTransfer] = list(record.accepted_transfers)
        if include_conditional:
            qualifying_candidates.extend(record.conditional_transfers)

        for candidate in qualifying_candidates:
            eval_res: Optional[ApplicabilityEvaluation] = eval_map.get(candidate.transfer_id)
            if not eval_res:
                continue

            hyp = self._build_hypothesis(candidate, eval_res, record)
            hypotheses.append(hyp)

        return hypotheses

    def _build_hypothesis(
        self,
        candidate: CandidateTransfer,
        evaluation: ApplicabilityEvaluation,
        record: TransferRecord,
    ) -> StructuredHypothesis:
        hyp_id = f"hyp-{uuid.uuid4().hex[:8]}"
        title = (
            f"Analogical Hypothesis: {candidate.proposed_source_concept} "
            f"{candidate.proposed_relation_type.value} {candidate.proposed_target_concept} in {record.target_domain}"
        )

        # Build empirical premise
        s_rel = candidate.source_relation
        premise = [
            f"Documented relation in {record.source_domain}: '{s_rel.source_concept}' -[{s_rel.relation_type.value}]-> '{s_rel.target_concept}'.",
            f"Alignment mapping: {record.alignment.structural_similarity_score:.2f} structural similarity between {record.source_domain} and {record.target_domain}.",
            f"Applicability Guard outcome: {evaluation.verdict.value} with confidence {evaluation.confidence:.2f}.",
        ]

        # Mechanism description
        eq_clause = f" governed by the transferred relation {candidate.proposed_equation}" if candidate.proposed_equation else ""
        mechanism = (
            f"By analogical schema projection from {record.source_domain}, the functional role of "
            f"'{candidate.proposed_source_concept}' exerts a direct influence on '{candidate.proposed_target_concept}'"
            f"{eq_clause}. This transfers the underlying relational dynamics of {record.source_domain} into {record.target_domain}."
        )

        # Falsifiable prediction
        if candidate.proposed_equation:
            prediction = (
                f"Empirical variation of '{candidate.proposed_source_concept}' will yield a corresponding change in "
                f"'{candidate.proposed_target_concept}' conforming quantitatively to equation '{candidate.proposed_equation}'."
            )
        else:
            prediction = (
                f"Modulation of '{candidate.proposed_source_concept}' will exhibit a {candidate.proposed_relation_type.value} "
                f"response in '{candidate.proposed_target_concept}' under controlled target conditions."
            )

        # Counterevidence / Falsification conditions
        counterevidence = [
            f"Observation of non-correlation or opposite relationship (e.g. opposing effect on {candidate.proposed_target_concept}).",
            f"Deviation of experimental observations from predicted equation by more than the experimental error margin.",
        ]
        if evaluation.conditions_required:
            counterevidence.append(
                f"Breakdown of prerequisite operating assumptions: {'; '.join(evaluation.conditions_required)}."
            )

        # Suggested experiment proposals
        experiments: List[ExperimentProposal] = [
            ExperimentProposal(
                proposal_id=f"exp-sym-{uuid.uuid4().hex[:6]}",
                experiment_type=ExperimentType.SYMBOLIC_DERIVATION,
                description=(
                    f"Perform formal algebraic derivation in SymPy to verify asymptotic behavior and conservation laws "
                    f"for equation: {candidate.proposed_equation or candidate.proposed_relation_type.value}."
                ),
                target_variables=[candidate.proposed_source_concept, candidate.proposed_target_concept],
                expected_signature="Conservation laws satisfied; no non-physical singular divergence.",
                falsification_threshold="Singular divergence or conservation violation at domain boundaries.",
            ),
            ExperimentProposal(
                proposal_id=f"exp-num-{uuid.uuid4().hex[:6]}",
                experiment_type=ExperimentType.NUMERICAL_SIMULATION,
                description=(
                    f"Execute parameterized numerical simulation across target parameter space to quantify the response of "
                    f"'{candidate.proposed_target_concept}' to perturbations in '{candidate.proposed_source_concept}'."
                ),
                target_variables=[candidate.proposed_source_concept, candidate.proposed_target_concept],
                expected_signature=f"Concordance with {candidate.proposed_relation_type.value} trend across boundary range.",
                falsification_threshold="Statistical $R^2 < 0.85$ against hypothesized governing model.",
            ),
            ExperimentProposal(
                proposal_id=f"exp-lab-{uuid.uuid4().hex[:6]}",
                experiment_type=ExperimentType.LABORATORY_MEASUREMENT,
                description=(
                    f"Physical experimental sweep measuring '{candidate.proposed_target_concept}' while controlling for "
                    f"boundary conditions: {', '.join(evaluation.conditions_required) or 'nominal operating conditions'}."
                ),
                target_variables=[candidate.proposed_source_concept, candidate.proposed_target_concept],
                expected_signature=f"Empirical response signature matching {candidate.proposed_equation or candidate.proposed_relation_type.value}.",
                falsification_threshold="Null hypothesis: slope indistinguishable from zero or statistically inverted.",
            ),
        ]

        uncertainty = 0.20 if evaluation.verdict == ApplicabilityVerdict.ACCEPTED else 0.45

        provenance_links: List[ProvenancePointer] = []
        if candidate.provenance:
            provenance_links.append(candidate.provenance)
        elif candidate.source_relation and candidate.source_relation.provenance:
            provenance_links.append(candidate.source_relation.provenance)

        return StructuredHypothesis(
            hypothesis_id=hyp_id,
            title=title,
            premise=premise,
            mechanism=mechanism,
            prediction=prediction,
            counterevidence_conditions=counterevidence,
            suggested_experiments=experiments,
            uncertainty_level=uncertainty,
            epistemic_tier=EpistemicTier.HYPOTHESIS_CONJECTURED,
            source_domains=[record.source_domain],
            target_domain=record.target_domain,
            applicability_verdict=evaluation.verdict,
            required_conditions=evaluation.conditions_required,
            provenance_links=provenance_links,
        )

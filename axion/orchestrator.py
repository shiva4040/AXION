import uuid
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from axion.transfer.types import (
    AlignmentMethod,
    ApplicabilityVerdict,
    DomainKnowledgeBundle,
    TransferRecord,
)
from axion.transfer.engine import TransferEngine
from axion.hypothesis.types import StructuredHypothesis
from axion.hypothesis.generator import HypothesisGenerator
from axion.hypothesis_tester.types import (
    ExperimentRecord,
    ExperimentRequest,
    ExperimentType,
    ExperimentVerdict,
)
from axion.hypothesis_tester.tester import FullHypothesisTester
from axion.knowledge_memory.types import (
    DependentImpactReport,
    KnowledgeStatus,
    ValidatedFinding,
)
from axion.knowledge_memory.memory import ValidatedKnowledgeMemory

class InvestigationOutcome(BaseModel):
    """
    End-to-end outcome of an AXION 8-stage cognitive research workflow:
    Problem -> Reasoning -> Composition -> Transfer -> Guard -> Hypothesis -> Experiment -> Memory.
    """
    investigation_id: str
    query: str
    transfer_record: Optional[TransferRecord] = None
    hypotheses: List[StructuredHypothesis] = Field(default_factory=list)
    experiments: List[ExperimentRecord] = Field(default_factory=list)
    validated_findings: List[ValidatedFinding] = Field(default_factory=list)
    rejected_hypotheses: List[str] = Field(default_factory=list)
    summary: str

class CognitivePipeline:
    """
    AXION 8-Stage Neuro-Symbolic Research Coordinator.
    Integrates Knowledge Foundation, Reasoning System, Transfer Engine,
    Hypothesis Generator, Full Hypothesis Tester, and Validated Knowledge Memory.
    """

    def __init__(
        self,
        transfer_engine: Optional[TransferEngine] = None,
        hypothesis_gen: Optional[HypothesisGenerator] = None,
        tester: Optional[FullHypothesisTester] = None,
        memory: Optional[ValidatedKnowledgeMemory] = None,
    ):
        self.transfer_engine = transfer_engine or TransferEngine()
        self.hypothesis_gen = hypothesis_gen or HypothesisGenerator()
        self.tester = tester or FullHypothesisTester()
        self.memory = memory or ValidatedKnowledgeMemory()

    def run_investigation(
        self,
        query: str,
        source_domain: DomainKnowledgeBundle,
        target_domain: DomainKnowledgeBundle,
        experimental_dataset: Optional[List[Dict[str, float]]] = None,
        experiment_type: ExperimentType = ExperimentType.DATASET_EVALUATION,
        target_variable: Optional[str] = None,
        tolerance: float = 0.10,
    ) -> InvestigationOutcome:
        inv_id = f"inv-{uuid.uuid4().hex[:8]}"

        # Stages 1 to 5: Alignment, Composition, Projection, Applicability Guard
        transfer_rec: TransferRecord = self.transfer_engine.execute_transfer(
            source_bundle=source_domain,
            target_bundle=target_domain,
            method=AlignmentMethod.STRUCTURE_MAPPING,
        )

        # Stage 6: Hypothesis Generation
        hypotheses: List[StructuredHypothesis] = self.hypothesis_gen.generate_hypotheses_from_transfer_record(
            record=transfer_rec,
            include_conditional=True,
        )

        experiments: List[ExperimentRecord] = []
        validated_findings: List[ValidatedFinding] = []
        rejected_hypotheses: List[str] = []

        # Stage 7: Full Hypothesis Testing & Stage 8: Validated Knowledge Memory
        for hyp in hypotheses:
            # Determine equation or prediction model
            cand = next((c for c in transfer_rec.candidate_transfers if c.proposed_source_concept in hyp.title), None)
            pred_eq = cand.proposed_equation if cand and cand.proposed_equation else None

            # Fallback to symbolic check if no dataset is provided
            chosen_exp_type = experiment_type if (experimental_dataset and pred_eq) else ExperimentType.SYMBOLIC_TEST

            # Determine target variable if not provided
            t_var = target_variable
            if not t_var and cand:
                # Use mapped symbol or concept name
                t_var = list(cand.mapped_symbols.values())[0] if cand.mapped_symbols else cand.proposed_target_concept

            exp_req = ExperimentRequest(
                hypothesis_id=hyp.hypothesis_id,
                hypothesis_title=hyp.title,
                prediction_model=pred_eq or f"{hyp.title}",
                experiment_type=chosen_exp_type,
                parameters={"target_variable": t_var, "tolerance": tolerance},
                dataset=experimental_dataset,
                tolerance=tolerance,
                assumptions=hyp.required_conditions,
            )

            exp_rec = self.tester.run_experiment(exp_req)
            experiments.append(exp_rec)

            if exp_rec.verdict == ExperimentVerdict.SUPPORTED:
                # Stage 8: Store in Validated Knowledge Memory (Tier 4)
                finding = ValidatedFinding(
                    finding_id=f"fnd-{uuid.uuid4().hex[:8]}",
                    title=f"Validated: {hyp.title}",
                    statement=hyp.prediction,
                    status=KnowledgeStatus.VALID,
                    hypothesis_id=hyp.hypothesis_id,
                    supporting_experiment_ids=[exp_rec.experiment_id],
                    source_provenance=hyp.provenance_links,
                    active_assumptions=hyp.required_conditions,
                    applicable_conditions=hyp.required_conditions,
                    limitations=exp_rec.limitations,
                    created_at="",
                    updated_at="",
                )
                stored = self.memory.store_validated_finding(finding, exp_rec)
                validated_findings.append(stored)
            else:
                rejected_hypotheses.append(
                    f"{hyp.hypothesis_id}: {exp_rec.verdict.value} ({exp_rec.failure_analysis or 'did not meet tolerance'})"
                )

        summary = (
            f"Investigation '{inv_id}' completed. Transferred {len(transfer_rec.accepted_transfers)} accepted, "
            f"{len(transfer_rec.conditional_transfers)} conditional candidates. "
            f"Generated {len(hypotheses)} hypotheses. Tested {len(experiments)} experiments: "
            f"{len(validated_findings)} validated findings stored in memory; {len(rejected_hypotheses)} rejected."
        )

        return InvestigationOutcome(
            investigation_id=inv_id,
            query=query,
            transfer_record=transfer_rec,
            hypotheses=hypotheses,
            experiments=experiments,
            validated_findings=validated_findings,
            rejected_hypotheses=rejected_hypotheses,
            summary=summary,
        )

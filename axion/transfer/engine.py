import uuid
from typing import Dict, List, Optional
from axion.transfer.types import (
    AlignmentMethod,
    ApplicabilityEvaluation,
    ApplicabilityVerdict,
    CandidateTransfer,
    DomainKnowledgeBundle,
    StructuralAlignmentResult,
    TransferRecord,
)
from axion.transfer.alignment import StructuralAligner
from axion.transfer.composition import KnowledgeComposer
from axion.transfer.projector import CandidateProjector
from axion.transfer.guard import ApplicabilityGuard

class TransferEngine:
    """
    Component 6: Cross-Domain Knowledge Composition and Transfer Engine.
    Executes the complete 5-stage research pipeline:
    1. Knowledge Identification & Provenance Preservation
    2. Structural Alignment (SMT / Graph Signature / Semantic)
    3. Multi-Domain Knowledge Composition & Variable Harmonization
    4. Candidate Analogical Schema Projection
    5. Mandatory Applicability Guard Verification
    """

    def __init__(
        self,
        aligner: Optional[StructuralAligner] = None,
        composer: Optional[KnowledgeComposer] = None,
        projector: Optional[CandidateProjector] = None,
        guard: Optional[ApplicabilityGuard] = None,
    ):
        self.aligner = aligner or StructuralAligner()
        self.composer = composer or KnowledgeComposer()
        self.projector = projector or CandidateProjector()
        self.guard = guard or ApplicabilityGuard()

    def execute_transfer(
        self,
        source_bundle: DomainKnowledgeBundle,
        target_bundle: DomainKnowledgeBundle,
        method: AlignmentMethod = AlignmentMethod.STRUCTURE_MAPPING,
        record_id: Optional[str] = None,
    ) -> TransferRecord:
        rec_id = record_id or f"rec-{uuid.uuid4().hex[:8]}"

        # Stage 1 & 2: Structural Alignment across domains
        alignment: StructuralAlignmentResult = self.aligner.align(
            source=source_bundle,
            target=target_bundle,
            method=method,
        )

        # Stage 3: Multi-Domain Knowledge Composition & Variable Harmonization
        composed_system = self.composer.compose(
            domain_bundles=[source_bundle, target_bundle],
            composition_id=f"comp-{rec_id}",
        )

        # Stage 4: Candidate Analogical Schema Projection
        candidates: List[CandidateTransfer] = self.projector.project_candidates(
            alignment=alignment,
            source=source_bundle,
            target=target_bundle,
        )

        # Stage 5: Mandatory Multi-Stage Applicability Guard
        evaluations: List[ApplicabilityEvaluation] = []
        accepted: List[CandidateTransfer] = []
        conditional: List[CandidateTransfer] = []
        rejected: List[CandidateTransfer] = []

        for cand in candidates:
            eval_res = self.guard.evaluate_transfer(cand, target_bundle)
            evaluations.append(eval_res)

            if eval_res.verdict == ApplicabilityVerdict.ACCEPTED:
                accepted.append(cand)
            elif eval_res.verdict == ApplicabilityVerdict.CONDITIONAL:
                conditional.append(cand)
            else:
                rejected.append(cand)

        return TransferRecord(
            record_id=rec_id,
            source_domain=source_bundle.domain_name,
            target_domain=target_bundle.domain_name,
            alignment=alignment,
            candidate_transfers=candidates,
            evaluations=evaluations,
            accepted_transfers=accepted,
            conditional_transfers=conditional,
            rejected_transfers=rejected,
            composed_system=composed_system,
        )

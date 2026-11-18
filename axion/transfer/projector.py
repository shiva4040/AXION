import uuid
import re
from typing import Dict, List, Optional
from axion.transfer.types import (
    CandidateTransfer,
    DomainConcept,
    DomainKnowledgeBundle,
    DomainRelation,
    StructuralAlignmentResult,
)
from axion.core.types import EpistemicTier

class CandidateProjector:
    """
    Projects candidate relationships and equations from a source domain into a target domain
    via Analogical Schema Projection (ASP), tagging every projected candidate strictly as
    HYPOTHESIS_CONJECTURED.
    """

    def project_candidates(
        self,
        alignment: StructuralAlignmentResult,
        source: DomainKnowledgeBundle,
        target: DomainKnowledgeBundle,
    ) -> List[CandidateTransfer]:
        candidates: List[CandidateTransfer] = []

        concept_map: Dict[str, str] = {
            m.source_concept: m.target_concept for m in alignment.concept_mappings
        }

        # Build symbol mapping between aligned concepts
        source_concepts_by_name = {c.name: c for c in source.concepts}
        target_concepts_by_name = {c.name: c for c in target.concepts}

        symbol_map: Dict[str, str] = {}
        for s_name, t_name in concept_map.items():
            s_c = source_concepts_by_name.get(s_name)
            t_c = target_concepts_by_name.get(t_name)
            if s_c and t_c and s_c.symbol and t_c.symbol:
                symbol_map[s_c.symbol] = t_c.symbol

        # Identify candidate relation projections (both projected novel relations and aligned analogies requiring verification)
        for r_map in alignment.relation_mappings:
            if r_map.status not in ["PROJECTED_CANDIDATE", "ALIGNED"]:
                continue

            s_rel = r_map.source_relation
            mapped_src = concept_map.get(s_rel.source_concept)
            mapped_tgt = concept_map.get(s_rel.target_concept)

            if not mapped_src or not mapped_tgt:
                continue

            # Rewrite equation if present
            proposed_eq: Optional[str] = None
            if s_rel.equation:
                proposed_eq = self._project_equation(s_rel.equation, symbol_map)

            transfer_id = f"xfer-{uuid.uuid4().hex[:8]}"
            candidate = CandidateTransfer(
                transfer_id=transfer_id,
                source_domain=source.domain_name,
                target_domain=target.domain_name,
                source_relation=s_rel,
                proposed_source_concept=mapped_src,
                proposed_target_concept=mapped_tgt,
                proposed_relation_type=s_rel.relation_type,
                proposed_equation=proposed_eq,
                mapped_concept_names=concept_map,
                mapped_symbols=symbol_map,
                epistemic_tier=EpistemicTier.HYPOTHESIS_CONJECTURED,
                rationale=(
                    f"Transferred from {source.domain_name} '{s_rel.source_concept}' "
                    f"-[{s_rel.relation_type}]-> '{s_rel.target_concept}' via structural analogy. "
                    f"Aligned to target concepts '{mapped_src}' and '{mapped_tgt}'."
                ),
                provenance=s_rel.provenance,
            )
            candidates.append(candidate)

        return candidates

    def _project_equation(self, equation: str, symbol_map: Dict[str, str]) -> str:
        """Substitutes source symbols with mapped target symbols in equation."""
        projected = equation
        sorted_symbols = sorted(symbol_map.keys(), key=lambda s: len(s), reverse=True)
        for s_sym in sorted_symbols:
            t_sym = symbol_map[s_sym]
            pattern = r'\b' + re.escape(s_sym) + r'\b'
            projected = re.sub(pattern, t_sym, projected)
        return projected

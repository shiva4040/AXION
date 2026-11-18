import math
from typing import Dict, List, Optional, Set, Tuple
from axion.transfer.types import (
    AlignmentMethod,
    ConceptMapping,
    DomainConcept,
    DomainKnowledgeBundle,
    DomainRelation,
    RelationMapping,
    StructuralAlignmentResult,
)
from axion.core.types import RelationType

class StructuralAligner:
    """
    Identifies structural and relational alignments across different scientific domains.
    Implements Structure Mapping Theory (Gentner SMT), alongside Graph Signature
    and Semantic baselines for comparative evaluation.
    """

    def align(
        self,
        source: DomainKnowledgeBundle,
        target: DomainKnowledgeBundle,
        method: AlignmentMethod = AlignmentMethod.STRUCTURE_MAPPING,
    ) -> StructuralAlignmentResult:
        if method == AlignmentMethod.STRUCTURE_MAPPING:
            return self._align_smt(source, target)
        elif method == AlignmentMethod.GRAPH_SIGNATURE:
            return self._align_graph_signature(source, target)
        elif method == AlignmentMethod.SEMANTIC_EMBEDDING:
            return self._align_semantic(source, target)
        else:
            raise ValueError(f"Unsupported alignment method: {method}")

    def _align_smt(
        self,
        source: DomainKnowledgeBundle,
        target: DomainKnowledgeBundle,
    ) -> StructuralAlignmentResult:
        """
        Gentner Structure Mapping Theory (SMT):
        Aligns concepts based on functional relational roles and matches systems
        of connected relations (systematicity principle).
        """
        concept_mappings: List[ConceptMapping] = []
        mapped_target_concepts: Set[str] = set()

        # Phase A: Role and functional signature matching
        for s_c in source.concepts:
            best_target: Optional[DomainConcept] = None
            best_score = 0.0
            best_role = s_c.role or "unspecified"

            for t_c in target.concepts:
                if t_c.name in mapped_target_concepts:
                    continue

                score = 0.0
                # Match by explicit role
                if s_c.role and t_c.role and s_c.role.lower() == t_c.role.lower():
                    score += 0.6
                # Match by entity category (CONCEPT, PARAMETER, EQUATION, etc.)
                if s_c.category == t_c.category:
                    score += 0.2
                # Match by relational connectivity signature
                s_rel_count = sum(1 for r in source.relations if r.source_concept == s_c.name or r.target_concept == s_c.name)
                t_rel_count = sum(1 for r in target.relations if r.source_concept == t_c.name or r.target_concept == t_c.name)
                if s_rel_count > 0 and t_rel_count > 0:
                    connectivity_ratio = min(s_rel_count, t_rel_count) / max(s_rel_count, t_rel_count)
                    score += 0.2 * connectivity_ratio

                if score > best_score and score >= 0.4:
                    best_score = score
                    best_target = t_c

            if best_target:
                mapped_target_concepts.add(best_target.name)
                concept_mappings.append(
                    ConceptMapping(
                        source_concept=s_c.name,
                        target_concept=best_target.name,
                        confidence=min(1.0, best_score),
                        role=best_role,
                        explanation=f"Mapped '{s_c.name}' in {source.domain_name} to '{best_target.name}' in {target.domain_name} via role '{best_role}' and structural alignment (score {best_score:.2f}).",
                    )
                )

        concept_lookup: Dict[str, str] = {m.source_concept: m.target_concept for m in concept_mappings}

        # Phase B: Relational alignment & systematicity evaluation
        relation_mappings: List[RelationMapping] = []
        aligned_count = 0
        projected_count = 0

        for s_rel in source.relations:
            mapped_src = concept_lookup.get(s_rel.source_concept)
            mapped_tgt = concept_lookup.get(s_rel.target_concept)

            if mapped_src and mapped_tgt:
                # Check if an identical or compatible relation exists in the target domain
                matching_target_rel = next(
                    (
                        t_rel
                        for t_rel in target.relations
                        if t_rel.source_concept == mapped_src
                        and t_rel.target_concept == mapped_tgt
                        and t_rel.relation_type == s_rel.relation_type
                    ),
                    None,
                )

                if matching_target_rel:
                    aligned_count += 1
                    relation_mappings.append(
                        RelationMapping(
                            source_relation=s_rel,
                            target_relation=matching_target_rel,
                            confidence=0.95,
                            status="ALIGNED",
                            explanation=f"Exact relational isomorphism: ({s_rel.source_concept} -[{s_rel.relation_type}]-> {s_rel.target_concept}) matches ({mapped_src} -[{matching_target_rel.relation_type}]-> {mapped_tgt}).",
                        )
                    )
                else:
                    # Target does NOT have this relation: this is a candidate for analogical projection!
                    projected_count += 1
                    relation_mappings.append(
                        RelationMapping(
                            source_relation=s_rel,
                            target_relation=None,
                            confidence=0.80,
                            status="PROJECTED_CANDIDATE",
                            explanation=f"Candidate analogical projection: Source relation ({s_rel.source_concept} -[{s_rel.relation_type}]-> {s_rel.target_concept}) projects onto ({mapped_src} -> {mapped_tgt}).",
                        )
                    )
            else:
                # Concepts not mapped
                relation_mappings.append(
                    RelationMapping(
                        source_relation=s_rel,
                        target_relation=None,
                        confidence=0.2,
                        status="MISMATCHED",
                        explanation=f"Unmapped source relation components: source_concept='{s_rel.source_concept}', target_concept='{s_rel.target_concept}'.",
                    )
                )

        # Calculate structural similarity and systematicity scores incorporating role coverage and relational projection
        total_source_rels = max(len(source.relations), 1)
        concept_coverage = len(concept_mappings) / max(len(source.concepts), 1)
        relational_coverage = (aligned_count + 0.8 * projected_count) / total_source_rels
        structural_sim = 0.4 * concept_coverage + 0.6 * relational_coverage
        structural_sim = max(0.0, min(1.0, structural_sim))

        # Systematicity: ratio of mapped connected relational chains
        systematicity = 0.3 * concept_coverage + 0.7 * ((aligned_count * 1.0 + projected_count * 0.8) / total_source_rels)
        systematicity = max(0.0, min(1.0, systematicity))

        # Identify explicit domain differences
        domain_differences = self._detect_domain_differences(source, target)

        alignable_roles = list(set(m.role for m in concept_mappings if m.role != "unspecified"))

        return StructuralAlignmentResult(
            source_domain=source.domain_name,
            target_domain=target.domain_name,
            method=AlignmentMethod.STRUCTURE_MAPPING,
            concept_mappings=concept_mappings,
            relation_mappings=relation_mappings,
            structural_similarity_score=round(structural_sim, 3),
            systematicity_score=round(systematicity, 3),
            domain_differences=domain_differences,
            alignable_roles=alignable_roles,
        )

    def _align_graph_signature(
        self,
        source: DomainKnowledgeBundle,
        target: DomainKnowledgeBundle,
    ) -> StructuralAlignmentResult:
        """
        Graph Signature Alignment Baseline:
        Matches nodes based solely on graph degree and relation type distribution,
        without understanding functional roles or systematicity.
        """
        concept_mappings: List[ConceptMapping] = []
        mapped_targets: Set[str] = set()

        for s_c in source.concepts:
            s_deg = sum(1 for r in source.relations if r.source_concept == s_c.name or r.target_concept == s_c.name)
            best_target: Optional[DomainConcept] = None
            best_diff = 9999

            for t_c in target.concepts:
                if t_c.name in mapped_targets:
                    continue
                t_deg = sum(1 for r in target.relations if r.source_concept == t_c.name or r.target_concept == t_c.name)
                diff = abs(s_deg - t_deg)
                if diff < best_diff:
                    best_diff = diff
                    best_target = t_c

            if best_target and best_diff <= 2:
                mapped_targets.add(best_target.name)
                sim = 1.0 / (1.0 + best_diff)
                concept_mappings.append(
                    ConceptMapping(
                        source_concept=s_c.name,
                        target_concept=best_target.name,
                        confidence=round(sim, 2),
                        role="degree_matched",
                        explanation=f"Graph signature match based on degree: source={s_deg}, target={best_target.name}.",
                    )
                )

        relation_mappings: List[RelationMapping] = []
        for s_rel in source.relations:
            relation_mappings.append(
                RelationMapping(
                    source_relation=s_rel,
                    target_relation=None,
                    confidence=0.5,
                    status="PROJECTED_CANDIDATE",
                    explanation="Graph signature candidate projection.",
                )
            )

        sim_score = len(concept_mappings) / max(len(source.concepts), 1)
        domain_differences = self._detect_domain_differences(source, target)

        return StructuralAlignmentResult(
            source_domain=source.domain_name,
            target_domain=target.domain_name,
            method=AlignmentMethod.GRAPH_SIGNATURE,
            concept_mappings=concept_mappings,
            relation_mappings=relation_mappings,
            structural_similarity_score=round(min(1.0, sim_score), 3),
            systematicity_score=0.3,
            domain_differences=domain_differences,
            alignable_roles=["degree_matched"],
        )

    def _align_semantic(
        self,
        source: DomainKnowledgeBundle,
        target: DomainKnowledgeBundle,
    ) -> StructuralAlignmentResult:
        """
        Semantic Alignment Baseline:
        Matches concepts using category and lexical token overlap.
        """
        concept_mappings: List[ConceptMapping] = []
        mapped_targets: Set[str] = set()

        for s_c in source.concepts:
            s_tokens = set(s_c.name.lower().replace("_", " ").split())
            best_target: Optional[DomainConcept] = None
            best_overlap = 0

            for t_c in target.concepts:
                if t_c.name in mapped_targets:
                    continue
                t_tokens = set(t_c.name.lower().replace("_", " ").split())
                overlap = len(s_tokens.intersection(t_tokens))
                if s_c.category == t_c.category:
                    overlap += 1
                if overlap > best_overlap:
                    best_overlap = overlap
                    best_target = t_c

            if best_target and best_overlap > 0:
                mapped_targets.add(best_target.name)
                conf = min(1.0, best_overlap / max(len(s_tokens), 1))
                concept_mappings.append(
                    ConceptMapping(
                        source_concept=s_c.name,
                        target_concept=best_target.name,
                        confidence=round(conf, 2),
                        role="semantic_overlap",
                        explanation=f"Semantic category/token overlap match between '{s_c.name}' and '{best_target.name}'.",
                    )
                )

        relation_mappings: List[RelationMapping] = []
        for s_rel in source.relations:
            relation_mappings.append(
                RelationMapping(
                    source_relation=s_rel,
                    target_relation=None,
                    confidence=0.4,
                    status="PROJECTED_CANDIDATE",
                    explanation="Semantic baseline candidate projection.",
                )
            )

        sim_score = len(concept_mappings) / max(len(source.concepts), 1)
        domain_differences = self._detect_domain_differences(source, target)

        return StructuralAlignmentResult(
            source_domain=source.domain_name,
            target_domain=target.domain_name,
            method=AlignmentMethod.SEMANTIC_EMBEDDING,
            concept_mappings=concept_mappings,
            relation_mappings=relation_mappings,
            structural_similarity_score=round(min(1.0, sim_score), 3),
            systematicity_score=0.25,
            domain_differences=domain_differences,
            alignable_roles=["semantic_overlap"],
        )

    def _detect_domain_differences(
        self,
        source: DomainKnowledgeBundle,
        target: DomainKnowledgeBundle,
    ) -> List[str]:
        """Identifies explicit assumption, boundary, or ontological divergences."""
        diffs: List[str] = []

        s_assump = set(a.lower() for a in source.assumptions)
        t_assump = set(a.lower() for a in target.assumptions)

        # Check for unshared assumptions
        for a in s_assump:
            if a not in t_assump:
                diffs.append(f"Source domain relies on assumption '{a}', which is absent in target domain.")
        for a in t_assump:
            if a not in s_assump:
                diffs.append(f"Target domain enforces assumption '{a}', which is absent in source domain.")

        # Check boundary condition scope
        s_vars = set(bc.variable_name for bc in source.boundary_conditions)
        t_vars = set(bc.variable_name for bc in target.boundary_conditions)
        if s_vars != t_vars:
            diffs.append(f"Variable parameter space differs: source regulates {sorted(list(s_vars))}, target regulates {sorted(list(t_vars))}.")

        return diffs

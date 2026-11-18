import uuid
from typing import Dict, List, Set, Optional
from axion.transfer.types import (
    BoundaryConstraint,
    ComposedSystem,
    DomainConcept,
    DomainKnowledgeBundle,
    DomainRelation,
    HarmonizedVariable,
)
from axion.core.types import ProvenancePointer

class KnowledgeComposer:
    """
    Composes knowledge representations across multiple scientific domains into a unified,
    transparent, and inspectable system of equations, relations, and constraints.
    Handles variable harmonization, unit alignment, and provenance tracking.
    """

    def compose(
        self,
        domain_bundles: List[DomainKnowledgeBundle],
        composition_id: Optional[str] = None,
    ) -> ComposedSystem:
        comp_id = composition_id or f"comp-{uuid.uuid4().hex[:8]}"
        domains = [b.domain_name for b in domain_bundles]

        # Step 1: Harmonize variables across domains to resolve symbol collisions
        harmonized_vars, symbol_map = self._harmonize_variables(domain_bundles)

        # Step 2: Harmonize equations with resolved symbols
        composed_equations: List[str] = []
        for bundle in domain_bundles:
            for rel in bundle.relations:
                if rel.equation:
                    eq_harmonized = self._rewrite_equation_with_symbols(rel.equation, bundle.domain_name, symbol_map)
                    composed_equations.append(eq_harmonized)

        # Step 3: Combine domain relations with rewritten concepts/symbols
        composed_relations: List[DomainRelation] = []
        provenance_chain: List[ProvenancePointer] = []

        for bundle in domain_bundles:
            for rel in bundle.relations:
                composed_relations.append(rel)
                if rel.provenance:
                    provenance_chain.append(rel.provenance)

        # Step 4: Union active assumptions & boundary constraints
        active_assumptions: List[str] = []
        for bundle in domain_bundles:
            for assump in bundle.assumptions:
                active_assumptions.append(f"[{bundle.domain_name}] {assump}")

        active_constraints: List[BoundaryConstraint] = []
        for bundle in domain_bundles:
            for bc in bundle.boundary_conditions:
                active_constraints.append(bc)

        return ComposedSystem(
            composition_id=comp_id,
            domains=domains,
            harmonized_variables=harmonized_vars,
            composed_equations=composed_equations,
            composed_relations=composed_relations,
            active_assumptions=active_assumptions,
            active_constraints=active_constraints,
            provenance_chain=provenance_chain,
        )

    def _harmonize_variables(
        self,
        bundles: List[DomainKnowledgeBundle],
    ) -> tuple[List[HarmonizedVariable], Dict[str, Dict[str, str]]]:
        """
        Detects symbol conflicts across domains (e.g. 'T' as Temperature in thermodynamics
        vs 'T' as Period/Tension in mechanics) and namespaces them cleanly.
        Returns harmonized variable list and a lookup: {domain_name: {old_symbol: resolved_symbol}}.
        """
        symbol_counts: Dict[str, List[tuple[str, DomainConcept]]] = {}
        for bundle in bundles:
            for concept in bundle.concepts:
                if concept.symbol:
                    sym = concept.symbol.strip()
                    if sym not in symbol_counts:
                        symbol_counts[sym] = []
                    symbol_counts[sym].append((bundle.domain_name, concept))

        harmonized: List[HarmonizedVariable] = []
        domain_symbol_map: Dict[str, Dict[str, str]] = {b.domain_name: {} for b in bundles}

        for sym, occurrences in symbol_counts.items():
            # If the same symbol appears in multiple domains for different concepts, disambiguate
            unique_concepts = set(occ[1].name for occ in occurrences)
            is_collision = len(occurrences) > 1 and len(unique_concepts) > 1

            for domain_name, concept in occurrences:
                if is_collision:
                    short_dom = domain_name.split(":")[-1][:3].lower()
                    resolved_sym = f"{sym}_{short_dom}"
                else:
                    resolved_sym = sym

                domain_symbol_map[domain_name][sym] = resolved_sym

                harmonized.append(
                    HarmonizedVariable(
                        source_symbol=sym,
                        canonical_name=concept.name,
                        domain_origins=[domain_name],
                        si_dimension=concept.si_dimension,
                        resolved_symbol=resolved_sym,
                    )
                )

        return harmonized, domain_symbol_map

    def _rewrite_equation_with_symbols(
        self,
        equation: str,
        domain_name: str,
        symbol_map: Dict[str, Dict[str, str]],
    ) -> str:
        """Rewrites equation string replacing any colliding symbols with resolved namespaces."""
        rewritten = equation
        d_map = symbol_map.get(domain_name, {})
        # Replace multi-char symbols first, then single-char to avoid sub-token corruptions
        sorted_symbols = sorted(d_map.keys(), key=lambda s: len(s), reverse=True)
        for old_sym in sorted_symbols:
            new_sym = d_map[old_sym]
            if old_sym != new_sym:
                # Basic token replacement
                import re
                pattern = r'\b' + re.escape(old_sym) + r'\b'
                rewritten = re.sub(pattern, new_sym, rewritten)
        return rewritten

import pytest
from axion.transfer.types import (
    DomainConcept,
    DomainKnowledgeBundle,
    DomainRelation,
)
from axion.core.types import EntityCategory, EpistemicTier, RelationType, ProvenancePointer
from axion.transfer.composition import KnowledgeComposer

def test_variable_harmonization_resolves_symbol_collisions():
    composer = KnowledgeComposer()

    # Domain 1 uses T for Temperature
    b1 = DomainKnowledgeBundle(
        domain_name="physics:thermodynamics",
        concepts=[
            DomainConcept(
                name="Temperature",
                domain="physics:thermodynamics",
                symbol="T",
                si_dimension="[Θ]",
                role="potential",
            )
        ],
        relations=[
            DomainRelation(
                source_concept="Temperature",
                target_concept="Temperature",
                equation="E = k_b * T",
                provenance=ProvenancePointer(document_id="doc1", chunk_id="chk1", page_number=1, extracted_snippet="E = k_b * T")
            )
        ],
        assumptions=["thermal_equilibrium"]
    )

    # Domain 2 uses T for Period
    b2 = DomainKnowledgeBundle(
        domain_name="mechanics:oscillations",
        concepts=[
            DomainConcept(
                name="Period",
                domain="mechanics:oscillations",
                symbol="T",
                si_dimension="[T]",
                role="time",
            )
        ],
        relations=[
            DomainRelation(
                source_concept="Period",
                target_concept="Period",
                equation="f = 1 / T",
                provenance=ProvenancePointer(document_id="doc2", chunk_id="chk2", page_number=2, extracted_snippet="f = 1 / T")
            )
        ],
        assumptions=["harmonic_motion"]
    )

    composed = composer.compose([b1, b2])

    assert len(composed.domains) == 2
    assert len(composed.harmonized_variables) == 2

    # Check that colliding symbol T was disambiguated
    resolved_symbols = [v.resolved_symbol for v in composed.harmonized_variables]
    assert len(set(resolved_symbols)) == 2  # Disambiguated into 2 unique symbols
    assert any("the" in s for s in resolved_symbols)
    assert any("osc" in s for s in resolved_symbols)

    # Verify equations were rewritten
    assert len(composed.composed_equations) == 2
    eq_str = " ".join(composed.composed_equations)
    assert "T_the" in eq_str
    assert "T_osc" in eq_str

    # Verify provenance chain preserved
    assert len(composed.provenance_chain) == 2
    doc_ids = [p.document_id for p in composed.provenance_chain]
    assert "doc1" in doc_ids
    assert "doc2" in doc_ids

import pytest
from axion.transfer.types import (
    AlignmentMethod,
    DomainConcept,
    DomainKnowledgeBundle,
    DomainRelation,
    StructuralAlignmentResult,
)
from axion.core.types import EntityCategory, EpistemicTier, RelationType
from axion.transfer.alignment import StructuralAligner

@pytest.fixture
def hydraulic_domain():
    return DomainKnowledgeBundle(
        domain_name="fluid_mechanics:pipe",
        concepts=[
            DomainConcept(name="Pressure Drop", domain="fluid_mechanics:pipe", role="potential", category=EntityCategory.CONCEPT, symbol="dP"),
            DomainConcept(name="Volumetric Flow", domain="fluid_mechanics:pipe", role="flux", category=EntityCategory.CONCEPT, symbol="Q"),
            DomainConcept(name="Hydraulic Resistance", domain="fluid_mechanics:pipe", role="resistance", category=EntityCategory.CONCEPT, symbol="R_h"),
        ],
        relations=[
            DomainRelation(
                source_concept="Pressure Drop",
                target_concept="Volumetric Flow",
                relation_type=RelationType.PROPORTIONAL_TO,
                equation="dP = Q * R_h",
                epistemic_tier=EpistemicTier.FACT_DOCUMENTED,
                assumptions_required=["laminar_flow", "steady_state"],
            )
        ],
        assumptions=["laminar_flow", "steady_state"],
    )

@pytest.fixture
def electrical_domain():
    return DomainKnowledgeBundle(
        domain_name="physics:circuits",
        concepts=[
            DomainConcept(name="Electric Voltage", domain="physics:circuits", role="potential", category=EntityCategory.CONCEPT, symbol="V"),
            DomainConcept(name="Electric Current", domain="physics:circuits", role="flux", category=EntityCategory.CONCEPT, symbol="I"),
            DomainConcept(name="Electric Resistance", domain="physics:circuits", role="resistance", category=EntityCategory.CONCEPT, symbol="R"),
        ],
        relations=[
            DomainRelation(
                source_concept="Electric Voltage",
                target_concept="Electric Current",
                relation_type=RelationType.PROPORTIONAL_TO,
                equation="V = I * R",
                epistemic_tier=EpistemicTier.FACT_DOCUMENTED,
                assumptions_required=["ohmic_conduction", "steady_state"],
            )
        ],
        assumptions=["ohmic_conduction", "steady_state"],
    )

def test_smt_alignment_identifies_functional_isomorphism(hydraulic_domain, electrical_domain):
    aligner = StructuralAligner()
    result = aligner.align(
        source=hydraulic_domain,
        target=electrical_domain,
        method=AlignmentMethod.STRUCTURE_MAPPING,
    )

    assert result.source_domain == "fluid_mechanics:pipe"
    assert result.target_domain == "physics:circuits"
    assert result.structural_similarity_score > 0.8
    assert result.systematicity_score > 0.8

    # Verify role mappings
    mappings = {m.source_concept: m.target_concept for m in result.concept_mappings}
    assert mappings["Pressure Drop"] == "Electric Voltage"
    assert mappings["Volumetric Flow"] == "Electric Current"
    assert mappings["Hydraulic Resistance"] == "Electric Resistance"

    # Verify relational alignment
    assert len(result.relation_mappings) == 1
    rel_map = result.relation_mappings[0]
    assert rel_map.status == "ALIGNED"
    assert rel_map.source_relation.source_concept == "Pressure Drop"
    assert rel_map.target_relation.source_concept == "Electric Voltage"

def test_smt_alignment_identifies_domain_differences(hydraulic_domain, electrical_domain):
    aligner = StructuralAligner()
    result = aligner.align(source=hydraulic_domain, target=electrical_domain)
    # Check domain differences regarding unshared assumptions
    diffs = " ".join(result.domain_differences)
    assert "laminar_flow" in diffs
    assert "ohmic_conduction" in diffs

def test_comparative_alignment_methods(hydraulic_domain, electrical_domain):
    aligner = StructuralAligner()
    smt_res = aligner.align(hydraulic_domain, electrical_domain, AlignmentMethod.STRUCTURE_MAPPING)
    sig_res = aligner.align(hydraulic_domain, electrical_domain, AlignmentMethod.GRAPH_SIGNATURE)
    sem_res = aligner.align(hydraulic_domain, electrical_domain, AlignmentMethod.SEMANTIC_EMBEDDING)

    assert smt_res.method == AlignmentMethod.STRUCTURE_MAPPING
    assert sig_res.method == AlignmentMethod.GRAPH_SIGNATURE
    assert sem_res.method == AlignmentMethod.SEMANTIC_EMBEDDING
    # SMT should have higher systematicity score than graph signature
    assert smt_res.systematicity_score > sig_res.systematicity_score

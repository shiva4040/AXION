import pytest
from axion.knowledge_graph.graph import KnowledgeGraphStore
from axion.knowledge_graph.schema import ExtractedEntity, ExtractedRelation, GraphExtractionResult
from axion.reasoning.contradiction import ContradictionDetector
from axion.core.types import RelationType, EpistemicTier, EntityCategory

@pytest.mark.asyncio
async def test_contradiction_detection_opposing_relations(test_db_session):
    kg_store = KnowledgeGraphStore(test_db_session)

    # Ingest Claim 1 from Document A: Tensile Strain increases Conductivity
    res1 = GraphExtractionResult(
        entities=[
            ExtractedEntity(name="Lattice Strain", domain="physics:materials", category=EntityCategory.PARAMETER),
            ExtractedEntity(name="Ionic Conductivity", domain="physics:materials", category=EntityCategory.PARAMETER)
        ],
        relations=[
            ExtractedRelation(
                source_name="Lattice Strain",
                target_name="Ionic Conductivity",
                relation_type=RelationType.PROPORTIONAL_TO,
                epistemic_tier=EpistemicTier.FACT_DOCUMENTED,
                confidence=0.95,
                evidence_snippet="Tensile strain expands crystal channels, increasing ionic conductivity proportionally."
            )
        ]
    )
    await kg_store.add_extraction_result(res1, chunk_id="chunk_doc_a_01", default_domain="physics:materials")

    # Ingest Claim 2 from Document B: Tensile Strain decreases / is inversely proportional to Conductivity
    res2 = GraphExtractionResult(
        entities=[
            ExtractedEntity(name="Lattice Strain", domain="physics:materials", category=EntityCategory.PARAMETER),
            ExtractedEntity(name="Ionic Conductivity", domain="physics:materials", category=EntityCategory.PARAMETER)
        ],
        relations=[
            ExtractedRelation(
                source_name="Lattice Strain",
                target_name="Ionic Conductivity",
                relation_type=RelationType.INVERSELY_PROPORTIONAL_TO,
                epistemic_tier=EpistemicTier.FACT_DOCUMENTED,
                confidence=0.90,
                evidence_snippet="Lattice strain induces phase segregation, rendering conductivity inversely proportional to strain."
            )
        ]
    )
    await kg_store.add_extraction_result(res2, chunk_id="chunk_doc_b_09", default_domain="physics:materials")

    # Run Contradiction Detector
    detector = ContradictionDetector(test_db_session)
    alerts = await detector.scan_contradictions()

    assert len(alerts) >= 1
    alert = alerts[0]
    assert alert.concept_a == "Lattice Strain"
    assert alert.concept_b == "Ionic Conductivity"
    assert alert.relation_1 in [RelationType.PROPORTIONAL_TO, RelationType.INVERSELY_PROPORTIONAL_TO]
    assert alert.relation_2 in [RelationType.PROPORTIONAL_TO, RelationType.INVERSELY_PROPORTIONAL_TO]
    assert alert.source_chunk_1 != alert.source_chunk_2
    assert "Direct scientific contradiction" in alert.explanation

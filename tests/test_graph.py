import pytest
from axion.knowledge_graph.extractor import KnowledgeGraphExtractor
from axion.knowledge_graph.graph import KnowledgeGraphStore
from axion.knowledge_graph.schema import ExtractedEntity, ExtractedRelation, GraphExtractionResult
from axion.core.types import EntityCategory, RelationType, EpistemicTier

@pytest.mark.asyncio
async def test_extractor_rule_based():
    extractor = KnowledgeGraphExtractor()
    text = "Power_demand is proportional to Velocity. Force is governed by Acceleration."
    result = extractor._rule_based_extract(text, domain="physics:mechanics")
    
    assert len(result.entities) >= 2
    assert len(result.relations) >= 1
    assert any(r.relation_type == RelationType.PROPORTIONAL_TO for r in result.relations)
    assert any(r.relation_type == RelationType.GOVERNED_BY for r in result.relations)

@pytest.mark.asyncio
async def test_graph_store_and_networkx_export(test_db_session):
    store = KnowledgeGraphStore(test_db_session)
    
    extraction = GraphExtractionResult(
        entities=[
            ExtractedEntity(name="Voltage", domain="eng:electrical", category=EntityCategory.PARAMETER, symbol="V"),
            ExtractedEntity(name="Current", domain="eng:electrical", category=EntityCategory.PARAMETER, symbol="I"),
            ExtractedEntity(name="Resistance", domain="eng:electrical", category=EntityCategory.PARAMETER, symbol="R")
        ],
        relations=[
            ExtractedRelation(
                source_name="Voltage",
                target_name="Current",
                relation_type=RelationType.PROPORTIONAL_TO,
                epistemic_tier=EpistemicTier.FACT_DOCUMENTED,
                confidence=1.0,
                evidence_snippet="Ohm's Law: V = I * R"
            ),
            ExtractedRelation(
                source_name="Voltage",
                target_name="Resistance",
                relation_type=RelationType.PROPORTIONAL_TO,
                epistemic_tier=EpistemicTier.FACT_DOCUMENTED,
                confidence=1.0,
                evidence_snippet="Ohm's Law: V = I * R"
            )
        ]
    )

    stats = await store.add_extraction_result(extraction, chunk_id="chunk_test_01", default_domain="eng:electrical")
    assert stats["nodes_processed"] == 3
    assert stats["edges_created"] == 2

    # Export to NetworkX
    G = await store.export_to_networkx(domain_filter="eng:electrical")
    assert G.number_of_nodes() == 3
    assert G.number_of_edges() == 2
    assert "Voltage" in G
    assert "Current" in G
    assert G["Voltage"]["Current"]["relation_type"] == "proportional_to"

    # Multi-hop path discovery
    paths = await store.find_paths("Voltage", "Current", max_hops=2)
    assert len(paths) >= 1
    assert paths[0] == ["Voltage", "Current"]

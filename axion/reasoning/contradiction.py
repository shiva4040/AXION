from typing import List, Dict, Tuple, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from axion.database.models import GraphNode, GraphEdge, EdgeProvenance, DocumentChunk, Document
from axion.core.types import RelationType
from axion.reasoning.types import ContradictionAlert

OPPOSING_RELATIONS = {
    RelationType.PROPORTIONAL_TO.value: RelationType.INVERSELY_PROPORTIONAL_TO.value,
    RelationType.INVERSELY_PROPORTIONAL_TO.value: RelationType.PROPORTIONAL_TO.value,
    RelationType.REQUIRES.value: RelationType.INHIBITS.value,
    RelationType.INHIBITS.value: RelationType.REQUIRES.value,
    RelationType.CATALYZES.value: RelationType.INHIBITS.value,
}

class ContradictionDetector:
    """
    Component 5 Subsystem:
    Scans the Knowledge Graph to detect, isolate, and explain conflicting claims
    between competing primary sources.
    """
    def __init__(self, db_session: AsyncSession):
        self.session = db_session

    async def scan_contradictions(
        self,
        domain_filter: Optional[str] = None
    ) -> List[ContradictionAlert]:
        """
        Scans all edges in the Knowledge Graph for mutually conflicting claims on identical concept pairs.
        """
        alerts: List[ContradictionAlert] = []

        # Load all edges with source and target nodes
        stmt = (
            select(
                GraphEdge,
                GraphNode.canonical_name.label("source_name"),
                GraphNode.domain_namespace.label("source_domain")
            )
            .join(GraphNode, GraphEdge.source_node_id == GraphNode.id)
        )
        if domain_filter:
            stmt = stmt.where(GraphNode.domain_namespace == domain_filter)

        res = await self.session.execute(stmt)
        edge_rows = res.all()

        # Group edges by node pair: (source_node_id, target_node_id)
        pair_map: Dict[Tuple[str, str], List[Any]] = {}
        for edge, src_name, src_domain in edge_rows:
            pair = (edge.source_node_id, edge.target_node_id)
            if pair not in pair_map:
                pair_map[pair] = []
            pair_map[pair].append((edge, src_name))

        # Check for opposing relations in each pair
        for (src_id, tgt_id), edges in pair_map.items():
            if len(edges) < 2:
                continue

            for i in range(len(edges)):
                for j in range(i + 1, len(edges)):
                    edge_1, src_name_1 = edges[i]
                    edge_2, src_name_2 = edges[j]

                    r1 = edge_1.relation_type
                    r2 = edge_2.relation_type

                    # Check if r1 and r2 are opposing
                    if OPPOSING_RELATIONS.get(r1) == r2:
                        # Fetch target node name
                        tgt_node_stmt = select(GraphNode.canonical_name).where(GraphNode.id == tgt_id)
                        tgt_res = await self.session.execute(tgt_node_stmt)
                        tgt_name = tgt_res.scalar_one_or_none() or "Unknown"

                        # Fetch provenance for edge 1
                        prov_stmt_1 = (
                            select(EdgeProvenance.extracted_snippet, EdgeProvenance.chunk_id)
                            .where(EdgeProvenance.edge_id == edge_1.id)
                        )
                        p_res_1 = await self.session.execute(prov_stmt_1)
                        p1 = p_res_1.first()
                        snippet_1 = p1[0] if p1 else "Document snippet unavailable"
                        chunk_id_1 = p1[1] if p1 else "unknown_chunk_1"

                        # Fetch provenance for edge 2
                        prov_stmt_2 = (
                            select(EdgeProvenance.extracted_snippet, EdgeProvenance.chunk_id)
                            .where(EdgeProvenance.edge_id == edge_2.id)
                        )
                        p_res_2 = await self.session.execute(prov_stmt_2)
                        p2 = p_res_2.first()
                        snippet_2 = p2[0] if p2 else "Document snippet unavailable"
                        chunk_id_2 = p2[1] if p2 else "unknown_chunk_2"

                        alert = ContradictionAlert(
                            concept_a=src_name_1,
                            concept_b=tgt_name,
                            relation_1=RelationType(r1) if r1 in RelationType._value2member_map_ else RelationType.GOVERNED_BY,
                            source_chunk_1=chunk_id_1,
                            snippet_1=snippet_1,
                            relation_2=RelationType(r2) if r2 in RelationType._value2member_map_ else RelationType.GOVERNED_BY,
                            source_chunk_2=chunk_id_2,
                            snippet_2=snippet_2,
                            explanation=(
                                f"Direct scientific contradiction detected between concepts '{src_name_1}' and '{tgt_name}': "
                                f"Source 1 asserts relation '{r1}' ('{snippet_1[:80]}'), "
                                f"while Source 2 asserts conflicting relation '{r2}' ('{snippet_2[:80]}')."
                            )
                        )
                        alerts.append(alert)

        return alerts

import uuid
from typing import List, Dict, Any, Optional
import networkx as nx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from axion.database.models import GraphNode, GraphEdge, EdgeProvenance
from axion.knowledge_graph.schema import ExtractedEntity, ExtractedRelation, GraphExtractionResult
from axion.core.types import EpistemicTier, RelationType

class KnowledgeGraphStore:
    """
    Component 2: Scientific & Cross-Domain Knowledge Graph Engine.
    Manages typed relational graph persistence and in-memory NetworkX algorithmic analysis.
    """
    def __init__(self, db_session: AsyncSession):
        self.session = db_session

    async def get_or_create_node(self, entity: ExtractedEntity) -> GraphNode:
        """Finds or creates a canonical GraphNode."""
        stmt = select(GraphNode).where(
            and_(
                GraphNode.canonical_name == entity.name,
                GraphNode.domain_namespace == entity.domain
            )
        )
        res = await self.session.execute(stmt)
        node = res.scalars().first()
        if not node:
            node = GraphNode(
                id=str(uuid.uuid4()),
                canonical_name=entity.name,
                domain_namespace=entity.domain,
                category=entity.category.value if hasattr(entity.category, "value") else str(entity.category),
                symbol=entity.symbol,
                si_dimension=entity.si_dimension,
                description=entity.description,
                attributes=entity.attributes
            )
            self.session.add(node)
            await self.session.flush()
        return node

    async def add_extraction_result(
        self,
        extraction: GraphExtractionResult,
        chunk_id: str,
        default_domain: str = "general_science"
    ) -> Dict[str, int]:
        """
        Persists extracted entities, directed edges, and provenance links into the database.
        """
        nodes_created = 0
        edges_created = 0
        node_map: Dict[str, GraphNode] = {}

        # 1. Persist or link nodes
        for ent in extraction.entities:
            node = await self.get_or_create_node(ent)
            node_map[ent.name] = node
            nodes_created += 1

        # 2. Persist edges and provenance
        for rel in extraction.relations:
            src_node = node_map.get(rel.source_name)
            if not src_node:
                src_node = await self.get_or_create_node(ExtractedEntity(name=rel.source_name, domain=default_domain))
                node_map[rel.source_name] = src_node

            tgt_node = node_map.get(rel.target_name)
            if not tgt_node:
                tgt_node = await self.get_or_create_node(ExtractedEntity(name=rel.target_name, domain=default_domain))
                node_map[rel.target_name] = tgt_node

            # Check if edge already exists
            stmt = select(GraphEdge).where(
                and_(
                    GraphEdge.source_node_id == src_node.id,
                    GraphEdge.target_node_id == tgt_node.id,
                    GraphEdge.relation_type == rel.relation_type.value
                )
            )
            res = await self.session.execute(stmt)
            edge = res.scalars().first()
            if not edge:
                edge = GraphEdge(
                    id=str(uuid.uuid4()),
                    source_node_id=src_node.id,
                    target_node_id=tgt_node.id,
                    relation_type=rel.relation_type.value,
                    epistemic_tier=rel.epistemic_tier.value,
                    confidence=rel.confidence
                )
                self.session.add(edge)
                await self.session.flush()
                edges_created += 1

            # Attach provenance
            prov = EdgeProvenance(
                id=str(uuid.uuid4()),
                edge_id=edge.id,
                chunk_id=chunk_id,
                extracted_snippet=rel.evidence_snippet,
                extraction_method="AXION_EXTRACTOR"
            )
            self.session.add(prov)

        await self.session.commit()
        return {"nodes_processed": len(extraction.entities), "edges_created": edges_created}

    async def export_to_networkx(self, domain_filter: Optional[str] = None) -> nx.DiGraph:
        """
        Loads domain nodes and edges from PostgreSQL into an in-memory NetworkX DiGraph.
        """
        G = nx.DiGraph()

        # Query nodes
        node_stmt = select(GraphNode)
        if domain_filter:
            node_stmt = node_stmt.where(GraphNode.domain_namespace == domain_filter)
        node_res = await self.session.execute(node_stmt)
        nodes = node_res.scalars().all()

        node_id_to_name = {}
        for n in nodes:
            G.add_node(
                n.canonical_name,
                id=n.id,
                domain=n.domain_namespace,
                category=n.category,
                symbol=n.symbol,
                si_dimension=n.si_dimension
            )
            node_id_to_name[n.id] = n.canonical_name

        # Query edges
        edge_stmt = select(GraphEdge)
        edge_res = await self.session.execute(edge_stmt)
        edges = edge_res.scalars().all()

        for e in edges:
            src_name = node_id_to_name.get(e.source_node_id)
            tgt_name = node_id_to_name.get(e.target_node_id)
            if src_name and tgt_name:
                G.add_edge(
                    src_name,
                    tgt_name,
                    id=e.id,
                    relation_type=e.relation_type,
                    epistemic_tier=e.epistemic_tier,
                    confidence=e.confidence
                )

        return G

    async def find_paths(
        self,
        source_concept: str,
        target_concept: str,
        max_hops: int = 4
    ) -> List[List[str]]:
        """
        Discovers all paths between two concepts up to max_hops using NetworkX.
        """
        G = await self.export_to_networkx()
        if source_concept not in G or target_concept not in G:
            return []

        try:
            paths = list(nx.all_simple_paths(G, source=source_concept, target=target_concept, cutoff=max_hops))
            return paths
        except Exception:
            return []

import re
from typing import Optional, List
from axion.core.provider import LLMProvider, ChatMessage, get_llm_provider
from axion.core.types import EntityCategory, RelationType, EpistemicTier
from axion.knowledge_graph.schema import (
    ExtractedEntity, ExtractedRelation, GraphExtractionResult
)

class KnowledgeGraphExtractor:
    """
    Component 2 Subsystem:
    Extracts typed scientific entities and causal/relational edges
    grounded in primary text chunks with strict provenance.
    """
    def __init__(self, provider: Optional[LLMProvider] = None, default_domain: str = "general_science"):
        self.provider = provider or get_llm_provider()
        self.default_domain = default_domain

    def _rule_based_extract(self, text: str, domain: str) -> GraphExtractionResult:
        """
        Deterministic extraction fallback for scientific equations and relations
        when using offline / mock providers.
        """
        entities: List[ExtractedEntity] = []
        relations: List[ExtractedRelation] = []
        seen_entities = set()

        # Pattern 1: Parameter definitions like "variable X (unit) represents ..."
        # or simple equation relations "P_solar = Area * G * efficiency"
        eq_matches = re.findall(r"([A-Za-z0-9_\^\\]+)\s*=\s*([^,\n\.]+)", text)
        for lhs, rhs in eq_matches:
            lhs_clean = lhs.strip()
            if len(lhs_clean) > 0 and len(lhs_clean) < 30:
                if lhs_clean not in seen_entities:
                    entities.append(ExtractedEntity(
                        name=lhs_clean,
                        domain=domain,
                        category=EntityCategory.EQUATION,
                        symbol=lhs_clean,
                        description=f"Governing equation LHS in: {text[:80]}"
                    ))
                    seen_entities.add(lhs_clean)

                # Look for factors in RHS
                factors = re.findall(r"[A-Za-z][A-Za-z0-9_]*", rhs)
                for f in factors:
                    f_clean = f.strip()
                    if len(f_clean) > 1 and f_clean not in seen_entities:
                        entities.append(ExtractedEntity(
                            name=f_clean,
                            domain=domain,
                            category=EntityCategory.PARAMETER,
                            symbol=f_clean
                        ))
                        seen_entities.add(f_clean)
                        relations.append(ExtractedRelation(
                            source_name=lhs_clean,
                            target_name=f_clean,
                            relation_type=RelationType.PROPORTIONAL_TO,
                            epistemic_tier=EpistemicTier.FACT_DOCUMENTED,
                            confidence=0.95,
                            evidence_snippet=f"{lhs_clean} = {rhs.strip()[:100]}"
                        ))

        # Pattern 2: Relational language: "X is governed by Y" or "X requires Y"
        rel_pattern = re.compile(
            r"([A-Za-z\s]{3,30}?)\s+(is governed by|is proportional to|requires|inhibits|catalyzes)\s+([A-Za-z\s]{3,30})",
            re.IGNORECASE
        )
        for match in rel_pattern.finditer(text):
            src, rel_str, tgt = match.groups()
            src = src.strip().title()
            tgt = tgt.strip().title()
            rel_str = rel_str.lower().strip()
            
            rel_type = RelationType.GOVERNED_BY
            if "proportional" in rel_str:
                rel_type = RelationType.PROPORTIONAL_TO
            elif "requires" in rel_str:
                rel_type = RelationType.REQUIRES
            elif "inhibits" in rel_str:
                rel_type = RelationType.INHIBITS
            elif "catalyzes" in rel_str:
                rel_type = RelationType.CATALYZES

            if src not in seen_entities:
                entities.append(ExtractedEntity(name=src, domain=domain, category=EntityCategory.CONCEPT))
                seen_entities.add(src)
            if tgt not in seen_entities:
                entities.append(ExtractedEntity(name=tgt, domain=domain, category=EntityCategory.CONCEPT))
                seen_entities.add(tgt)

            relations.append(ExtractedRelation(
                source_name=src,
                target_name=tgt,
                relation_type=rel_type,
                epistemic_tier=EpistemicTier.FACT_DOCUMENTED,
                confidence=0.90,
                evidence_snippet=match.group(0)
            ))

        return GraphExtractionResult(entities=entities, relations=relations)

    async def extract_from_chunk(self, chunk_text: str, domain: Optional[str] = None) -> GraphExtractionResult:
        """
        Extracts scientific entities and relations from a text chunk.
        """
        target_domain = domain or self.default_domain
        
        # If running MockProvider, utilize rule-based extractor
        from axion.core.provider import MockProvider
        if isinstance(self.provider, MockProvider):
            return self._rule_based_extract(chunk_text, target_domain)

        prompt = f"""
You are a scientific knowledge graph extraction engine.
Extract all scientific concepts, physical parameters, laws, and equations from the following text.
For each relationship between concepts, specify the exact relation type from:
[governed_by, proportional_to, inversely_proportional_to, requires, inhibits, catalyzes, composed_of].
Return ONLY a valid JSON object matching this schema:
{{
  "entities": [
    {{"name": "...", "domain": "{target_domain}", "category": "CONCEPT|PARAMETER|EQUATION|MATERIAL|CONSTRAINT", "symbol": "...", "si_dimension": "..."}}
  ],
  "relations": [
    {{"source_name": "...", "target_name": "...", "relation_type": "...", "confidence": 1.0, "evidence_snippet": "..."}}
  ]
}}

Source text:
{chunk_text}
"""
        messages = [
            ChatMessage(role="system", content="You are a precise scientific ontology extractor. Output strictly valid JSON."),
            ChatMessage(role="user", content=prompt)
        ]
        
        resp = await self.provider.generate_text(messages=messages, temperature=0.0)
        try:
            import json
            data = json.loads(resp.text)
            return GraphExtractionResult.model_validate(data)
        except Exception:
            # Fallback to rule-based parser on JSON decoding issue
            return self._rule_based_extract(chunk_text, target_domain)

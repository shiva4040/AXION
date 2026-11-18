from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from axion.core.types import EpistemicTier, EntityCategory, RelationType

class ExtractedEntity(BaseModel):
    name: str = Field(description="Canonical entity or concept name, e.g. 'Seebeck Coefficient'")
    domain: str = Field(description="Domain namespace, e.g. 'physics:thermoelectricity'")
    category: EntityCategory = Field(default=EntityCategory.CONCEPT)
    symbol: Optional[str] = Field(default=None, description="Mathematical or physical symbol, e.g. 'S' or 'V_oc'")
    si_dimension: Optional[str] = Field(default=None, description="SI base dimension formula, e.g. '[M][L]2[T]-3[I]-1'")
    description: Optional[str] = None
    attributes: Dict[str, Any] = Field(default_factory=dict)

class ExtractedRelation(BaseModel):
    source_name: str
    target_name: str
    relation_type: RelationType = Field(default=RelationType.GOVERNED_BY)
    epistemic_tier: EpistemicTier = Field(default=EpistemicTier.FACT_DOCUMENTED)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    evidence_snippet: str = Field(description="Exact sentence or equation snippet from document supporting this relation")

class GraphExtractionResult(BaseModel):
    entities: List[ExtractedEntity] = Field(default_factory=list)
    relations: List[ExtractedRelation] = Field(default_factory=list)

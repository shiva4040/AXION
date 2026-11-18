from enum import Enum
from typing import Optional, Any
from pydantic import BaseModel, Field

class EpistemicTier(str, Enum):
    """
    AXION Epistemic Ladder:
    Strict categorization of evidence confidence to eliminate flat-confidence hallucination.
    """
    FACT_DOCUMENTED = "FACT_DOCUMENTED"         # Tier 1: Verified primary source text with page coordinates
    INFERENCE_DEDUCED = "INFERENCE_DEDUCED"     # Tier 2: Deductions from Tier 1 premises using verified logic
    HYPOTHESIS_CONJECTURED = "HYPOTHESIS_CONJECTURED" # Tier 3: Conjectured mechanism awaiting verification
    FINDING_VALIDATED = "FINDING_VALIDATED"     # Tier 4: Empirically validated via sandbox computation

class TrustTier(str, Enum):
    """Source provenance trust tiers."""
    PEER_REVIEWED = "PEER_REVIEWED"
    TECHNICAL_DOC = "TECHNICAL_DOC"
    PUBLIC_WEB = "PUBLIC_WEB"
    UNVERIFIED = "UNVERIFIED"

class EntityCategory(str, Enum):
    """Typed scientific entity classification."""
    CONCEPT = "CONCEPT"
    PRINCIPLE = "PRINCIPLE"
    PARAMETER = "PARAMETER"
    EQUATION = "EQUATION"
    MATERIAL = "MATERIAL"
    CONSTRAINT = "CONSTRAINT"

class RelationType(str, Enum):
    """Typed directional scientific relationships."""
    GOVERNED_BY = "governed_by"
    PROPORTIONAL_TO = "proportional_to"
    INVERSELY_PROPORTIONAL_TO = "inversely_proportional_to"
    REQUIRES = "requires"
    INHIBITS = "inhibits"
    CATALYZES = "catalyzes"
    COMPOSED_OF = "composed_of"
    DERIVED_FROM = "derived_from"
    TRANSFERS_TO = "transfers_to"  # Provisional analogical transfer edge

class BoundingBox(BaseModel):
    """Bounding box coordinates on a specific page of a PDF."""
    page_number: int
    x0: float
    y0: float
    x1: float
    y1: float

class ProvenancePointer(BaseModel):
    """Immutable link back to primary source evidence."""
    document_id: str
    chunk_id: str
    page_number: int
    bounding_box: Optional[BoundingBox] = None
    extracted_snippet: str

import re
import uuid
import logging
from typing import Any, Dict, List, Optional, Set, Tuple

from axion.core.provider import LLMProvider
from axion.core.types import BoundingBox, EpistemicTier, ProvenancePointer
from axion.pipeline.types import (
    AcquiredChunk,
    AcquisitionPayload,
    ExtractedClaim,
)

logger = logging.getLogger(__name__)

MATH_STOP_WORDS_SPLIT = re.compile(
    r"\s+(?:under|assuming|where|when|for|with|if|given|in)\b", re.IGNORECASE
)

# Patterns for equations
EQUATION_PATTERNS = [
    re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*\s*=\s*[^;\n\.]+)", re.IGNORECASE),
    re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*\s+is\s+proportional\s+to\s+[A-Za-z_][A-Za-z0-9_]*)", re.IGNORECASE),
    re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*\s+varies\s+inversely\s+with\s+[A-Za-z_][A-Za-z0-9_]*)", re.IGNORECASE),
]

# Patterns for operational conditions and assumptions
CONDITION_PATTERNS = [
    re.compile(r"\b(assuming\s+[^,\.;\n]+)", re.IGNORECASE),
    re.compile(r"\b(under\s+[^,\.;\n]+\s+conditions?)", re.IGNORECASE),
    re.compile(r"\b(only\s+when\s+[^,\.;\n]+)", re.IGNORECASE),
    re.compile(r"\b(valid\s+for\s+[^,\.;\n]+)", re.IGNORECASE),
    re.compile(r"\b(for\s+(?:low|high|steady|laminar|turbulent|incompressible)[^,\.;\n]*)", re.IGNORECASE),
    re.compile(r"\b(laminar\s+flow|turbulent\s+flow|steady[- ]state|incompressible|ideal\s+gas)", re.IGNORECASE),
    re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*\s*(?:>|<|>=|<=|in)\s*[^,\.;\n]+)", re.IGNORECASE),
]

# Pattern for variable symbols in equations (e.g. P, V, I, R, Solar_Power, Drag_Force)
VAR_TOKEN_PATTERN = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*)\b")

MATH_KEYWORDS = {
    "is", "proportional", "to", "varies", "inversely", "with", "equals",
    "the", "a", "an", "and", "or", "in", "for", "at", "by", "of"
}


class MinimalEvidenceExtractor:
    """
    Stage 03: Minimal Evidence Extractor.
    Extracts atomic factual claims, equations, variables, conditions,
    and verbatim quotations with strict ProvenancePointer anchoring from acquired literature.
    """

    def __init__(self, provider: Optional[LLMProvider] = None):
        self.provider = provider

    def extract_equations_and_variables(self, text: str) -> Tuple[List[str], List[str]]:
        """Extracts mathematical equations and participating variable symbols."""
        equations: List[str] = []
        variables: Set[str] = set()

        for pattern in EQUATION_PATTERNS:
            for match in pattern.finditer(text):
                raw_eq = match.group(1).strip()
                # Split off trailing prose clauses (e.g. 'under steady-state conditions')
                eq = MATH_STOP_WORDS_SPLIT.split(raw_eq)[0].strip()
                # Clean trailing periods or punctuation
                eq = eq.rstrip(".,;")
                if eq and len(eq) > 2 and eq not in equations:
                    equations.append(eq)
                    # Extract variable symbols
                    tokens = VAR_TOKEN_PATTERN.findall(eq)
                    for tok in tokens:
                        if tok.lower() not in MATH_KEYWORDS and not tok.isdigit():
                            variables.add(tok)

        return equations, sorted(list(variables))

    def extract_conditions(self, text: str) -> List[str]:
        """Extracts operational conditions, physical assumptions, and validity boundaries."""
        conditions: List[str] = []
        for pattern in CONDITION_PATTERNS:
            for match in pattern.finditer(text):
                cond = match.group(1).strip().rstrip(".,;")
                if cond and len(cond) > 3 and cond not in conditions:
                    conditions.append(cond)
        return conditions

    def extract_claims_from_chunk(self, chunk: AcquiredChunk) -> List[ExtractedClaim]:
        """
        Segments a single chunk's text into atomic claims, extracting equations,
        variables, and conditions while preserving exact substring provenance.
        """
        claims: List[ExtractedClaim] = []
        text = chunk.text_content.strip()
        if not text:
            return claims

        # Split into sentences or lines
        raw_sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n+", text) if s.strip()]

        for i, sentence in enumerate(raw_sentences):
            # Check length to ensure meaningful factual content
            if len(sentence) < 10:
                continue

            # Verbatim quotation assurance: sentence must be a substring of chunk text
            verbatim_snippet = sentence
            if sentence not in text:
                # Fallback to safe slice that exists in text
                idx = text.find(sentence[:20])
                if idx != -1:
                    verbatim_snippet = text[idx:idx + len(sentence)]
                else:
                    verbatim_snippet = text[:min(len(text), 150)]

            equations, variables = self.extract_equations_and_variables(sentence)
            conditions = self.extract_conditions(sentence)

            # Build strict ProvenancePointer
            prov = ProvenancePointer(
                document_id=chunk.document_id,
                chunk_id=chunk.chunk_id,
                page_number=chunk.page_number,
                bounding_box=chunk.bounding_box,
                extracted_snippet=verbatim_snippet,
            )

            claim_id = f"clm-{chunk.chunk_id}-{i}"
            claims.append(
                ExtractedClaim(
                    claim_id=claim_id,
                    statement=sentence,
                    epistemic_tier=EpistemicTier.FACT_DOCUMENTED,
                    conditions=conditions,
                    equations=equations,
                    variables=variables,
                    provenance=prov,
                    confidence=1.0,
                )
            )

        # Fallback: if no multi-sentence split yielded claims, extract the whole chunk as a single claim
        if not claims and text:
            eqs, vars_ = self.extract_equations_and_variables(text)
            conds = self.extract_conditions(text)
            prov = ProvenancePointer(
                document_id=chunk.document_id,
                chunk_id=chunk.chunk_id,
                page_number=chunk.page_number,
                bounding_box=chunk.bounding_box,
                extracted_snippet=text[:300].strip(),
            )
            claims.append(
                ExtractedClaim(
                    claim_id=f"clm-{chunk.chunk_id}-0",
                    statement=text[:300].strip(),
                    epistemic_tier=EpistemicTier.FACT_DOCUMENTED,
                    conditions=conds,
                    equations=eqs,
                    variables=vars_,
                    provenance=prov,
                    confidence=1.0,
                )
            )

        return claims

    def extract_claims_from_memory(self, memory_item: Dict[str, Any]) -> List[ExtractedClaim]:
        """Extracts validated claims from stored verified findings in memory."""
        fid = memory_item.get("finding_id", f"mem-{uuid.uuid4().hex[:6]}")
        statement = memory_item.get("statement", "").strip()
        if not statement:
            return []

        conditions = memory_item.get("applicable_conditions", []) + memory_item.get("active_assumptions", [])
        eqs, vars_ = self.extract_equations_and_variables(statement)

        prov = ProvenancePointer(
            document_id=f"memory:{fid}",
            chunk_id=f"mem-chunk-{fid}",
            page_number=1,
            extracted_snippet=statement[:300],
        )

        return [
            ExtractedClaim(
                claim_id=f"clm-mem-{fid}",
                statement=statement,
                epistemic_tier=EpistemicTier.FINDING_VALIDATED,
                conditions=list(dict.fromkeys(conditions)),
                equations=eqs,
                variables=vars_,
                provenance=prov,
                confidence=1.0,
            )
        ]

    async def extract_evidence(
        self,
        payload: AcquisitionPayload,
    ) -> List[ExtractedClaim]:
        """
        Executes Stage 03 Evidence Extraction over all acquired chunks and memory items.
        """
        all_claims: List[ExtractedClaim] = []

        # 1. Extract from acquired document chunks
        for chunk in payload.retrieved_chunks:
            chunk_claims = self.extract_claims_from_chunk(chunk)
            all_claims.extend(chunk_claims)

        # 2. Extract from candidate memory items
        for mem_item in payload.candidate_memory_items:
            mem_claims = self.extract_claims_from_memory(mem_item)
            all_claims.extend(mem_claims)

        logger.debug(
            "Stage 03 extracted %d claims from %d chunks and %d memory items",
            len(all_claims),
            len(payload.retrieved_chunks),
            len(payload.candidate_memory_items),
        )
        return all_claims

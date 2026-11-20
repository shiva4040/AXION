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
    ExtractedEvidenceItem,
    QuestionSpec,
    SubQuestion,
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

        underlying_snippet = statement
        doc_id = f"memory:{fid}"
        page_num = 1
        source_prov = memory_item.get("source_provenance")
        if source_prov and len(source_prov) > 0:
            sp = source_prov[0]
            if isinstance(sp, dict):
                underlying_snippet = sp.get("extracted_snippet") or statement
                page_num = sp.get("page_number", 1)
            elif hasattr(sp, "extracted_snippet"):
                underlying_snippet = sp.extracted_snippet or statement
                page_num = sp.page_number or 1

        prov = ProvenancePointer(
            document_id=doc_id,
            chunk_id=f"mem-chunk-{fid}",
            page_number=page_num,
            extracted_snippet=underlying_snippet[:300],
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


class ScientificEvidenceExtractor(MinimalEvidenceExtractor):
    """
    Stage 03: Enriched Scientific Evidence Extractor.
    Extracts multi-faceted scientific knowledge (facts, equations, variables, conditions,
    experimental findings, assumptions, materials, limitations) from diverse literature types.
    Explicitly maps each item to Stage 01 subquestions with grounded relevance explanations,
    detects internal contradictions, and identifies missing information.
    """

    def __init__(self, provider: Optional[LLMProvider] = None):
        super().__init__(provider=provider)

    def classify_item_type(self, statement: str, has_equations: bool, has_conditions: bool) -> str:
        s_lower = statement.lower()
        if has_equations or "=" in statement or "proportional to" in s_lower:
            return "equation"
        if any(w in s_lower for w in ["limit", "limitation", "breakdown", "valid only", "cannot"]):
            return "limitation"
        if any(w in s_lower for w in ["assuming", "assumed", "assumption", "idealized", "neglecting"]):
            return "assumption"
        if any(w in s_lower for w in ["measured", "experiment", "observed", "yielded", "data shows", "result"]):
            return "experimental_result"
        if any(w in s_lower for w in ["material", "silicon", "copper", "fluid", "polymer", "dielectric", "conductor"]):
            return "material"
        if any(w in s_lower for w in ["stator", "rotor", "piston", "valve", "inverter", "component", "cylinder"]):
            return "component"
        if any(w in s_lower for w in ["method", "procedure", "algorithm", "technique", "protocol"]):
            return "method"
        if has_conditions:
            return "condition"
        return "fact"

    def attribute_relevance(
        self,
        statement: str,
        item_type: str,
        variables: List[str],
        subquestions: List[SubQuestion],
        raw_query: str,
    ) -> Tuple[List[str], str]:
        """
        Maps extracted evidence to relevant subquestions and generates an explanatory note.
        """
        matched_sq_ids: List[str] = []
        s_tokens = set(re.findall(r"\b[A-Za-z0-9_]+\b", statement.lower()))
        var_tokens = set([v.lower() for v in variables])

        for sq in subquestions:
            sq_tokens = set(re.findall(r"\b[A-Za-z0-9_]+\b", f"{sq.question} {sq.target_subject} {sq.information_needed}".lower()))
            overlap = (s_tokens | var_tokens) & sq_tokens
            # Disregard stop words in overlap
            meaningful_overlap = [t for t in overlap if len(t) > 3 and t not in MATH_KEYWORDS]
            if meaningful_overlap:
                matched_sq_ids.append(sq.id)

        # Fallback to SQ-1 if no specific subquestion matched
        if not matched_sq_ids and subquestions:
            matched_sq_ids = [subquestions[0].id]

        matched_str = ", ".join(matched_sq_ids) if matched_sq_ids else "primary research question"
        if item_type == "equation":
            explanation = f"Provides mathematical governing relation directly resolving information requirement for {matched_str}."
        elif item_type == "condition" or item_type == "assumption":
            explanation = f"Establishes physical regime and boundary constraints for {matched_str}."
        elif item_type == "limitation":
            explanation = f"Identifies operational limits and critical breakdown thresholds for {matched_str}."
        elif item_type == "experimental_result":
            explanation = f"Supplies verified empirical benchmark data supporting {matched_str}."
        else:
            explanation = f"Grounded factual foundation addressing target requirements of {matched_str}."

        return matched_sq_ids, explanation

    def detect_evidence_contradictions(
        self, items: List[ExtractedEvidenceItem]
    ) -> List[Tuple[str, str, str]]:
        """
        Detects opposing claims or conflicting equations between evidence items.
        """
        contradictions: List[Tuple[str, str, str]] = []
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                item_a = items[i]
                item_b = items[j]

                # Directional contradiction check: increases vs decreases for same variable
                text_a = item_a.statement.lower()
                text_b = item_b.statement.lower()

                common_vars = set(item_a.variables.keys()) & set(item_b.variables.keys())
                for var in common_vars:
                    if (
                        ("increase" in text_a and "decrease" in text_b)
                        or ("increase" in text_b and "decrease" in text_a)
                        or ("proportional" in text_a and "inversely proportional" in text_b)
                        or ("inversely proportional" in text_a and "proportional" in text_b)
                    ):
                        note = f"Directional contradiction detected on variable '{var}' between [{item_a.source_name}] and [{item_b.source_name}]."
                        item_a.is_contradicted = True
                        item_b.is_contradicted = True
                        item_a.contradiction_notes = note
                        item_b.contradiction_notes = note
                        contradictions.append((item_a.item_id, item_b.item_id, note))

        return contradictions

    def identify_missing_evidence(
        self,
        subquestions: List[SubQuestion],
        items: List[ExtractedEvidenceItem],
    ) -> List[str]:
        """
        Identifies subquestions that lack sufficient backing evidence.
        """
        covered_sq_ids = set()
        for item in items:
            for sq_id in item.relevant_subquestion_ids:
                covered_sq_ids.add(sq_id)

        missing: List[str] = []
        for sq in subquestions:
            if sq.id not in covered_sq_ids:
                missing.append(
                    f"Subquestion {sq.id} ('{sq.question[:60]}...') requires additional acquisition: {sq.information_needed}."
                )

        return missing

    async def extract_structured_evidence(
        self,
        payload: AcquisitionPayload,
        question_spec: Optional[QuestionSpec] = None,
    ) -> List[ExtractedEvidenceItem]:
        """
        Extracts structured scientific evidence items, maps them to Stage 01 subquestions,
        and annotates provenance and contradictions.
        """
        evidence_items: List[ExtractedEvidenceItem] = []
        subquestions = question_spec.subquestions if question_spec else []
        raw_query = question_spec.raw_query if question_spec else ""

        # Extract from retrieved chunks
        for chunk in payload.retrieved_chunks:
            claims = self.extract_claims_from_chunk(chunk)
            for clm in claims:
                item_type = self.classify_item_type(
                    clm.statement,
                    has_equations=len(clm.equations) > 0,
                    has_conditions=len(clm.conditions) > 0,
                )
                vars_dict = {v: "physical_variable" for v in clm.variables}
                matched_sqs, explanation = self.attribute_relevance(
                    statement=clm.statement,
                    item_type=item_type,
                    variables=clm.variables,
                    subquestions=subquestions,
                    raw_query=raw_query,
                )

                ev_item = ExtractedEvidenceItem(
                    item_id=f"ev-{clm.claim_id}",
                    item_type=item_type,
                    statement=clm.statement,
                    canonical_symbol=clm.variables[0] if clm.variables else None,
                    variables=vars_dict,
                    relevance_explanation=explanation,
                    relevant_subquestion_ids=matched_sqs,
                    source_name=chunk.source_title or chunk.document_id,
                    source_uri=chunk.source_uri,
                    source_title=chunk.source_title or chunk.document_id,
                    epistemic_tier=clm.epistemic_tier,
                    confidence=clm.confidence,
                    provenance=clm.provenance,
                    assumptions=[c for c in clm.conditions if "assum" in c.lower()],
                    conditions=[c for c in clm.conditions if "assum" not in c.lower()],
                )
                evidence_items.append(ev_item)

        # Detect any contradictions
        self.detect_evidence_contradictions(evidence_items)

        return evidence_items


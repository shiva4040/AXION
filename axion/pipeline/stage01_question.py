import re
import uuid
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set
from pydantic import BaseModel

from axion.core.provider import LLMProvider
from axion.orchestrator import DOMAIN_KEYWORD_MAP
from axion.pipeline.types import QuestionIntent, QuestionSpec

logger = logging.getLogger(__name__)

STOP_WORDS: Set[str] = {
    "what", "how", "why", "when", "where", "who", "which", "does", "do", "did",
    "is", "are", "was", "were", "can", "we", "could", "would", "should", "the",
    "a", "an", "and", "or", "in", "on", "at", "by", "for", "with", "about",
    "like", "through", "over", "between", "under", "into", "from", "to", "of",
    "calculate", "compute", "determine", "find", "give", "show", "explain"
}

TRANSFER_PHRASES: List[str] = [
    "transfer from", "transfer to", "transfer between",
    "analog of", "analogy between", "analogous to",
    "map from", "mapping between", "cross-domain",
    "bridge between", "pipe to wire", "hydraulic to electrical",
    "thermal to electrical", "fluid to electrical", "mechanical to electrical"
]

CALCULATION_KEYWORDS: List[str] = [
    "calculate", "compute", "numerical", "value of", "solve for",
    "magnitude", "equals", "=", "+", "-", "*", "/", "ratio", "derive"
]

HYPOTHESIS_KEYWORDS: List[str] = [
    "hypothesis", "hypothesize", "conjecture", "plausible", "test whether",
    "falsify", "evidence for", "predict"
]

FEASIBILITY_KEYWORDS: List[str] = [
    "feasible", "feasibility", "can we build", "is it possible",
    "limit of", "efficiency limit", "bounds"
]

# Common physical units pattern
UNIT_PATTERN = re.compile(
    r"\b(-?\d+(?:\.\d+)?)\s*(V|A|W|J|K|°C|m/s|m|kg|Pa|kPa|MPa|Ohm|Ω|Hz|kHz|MHz|rad/s|mol|N)\b",
    re.IGNORECASE
)

# Common variable equality / constraint pattern
EQUALITY_PATTERN = re.compile(
    r"\b([A-Za-z_][A-Za-z0-9_]*)\s*(=|<|>|<=|>=)\s*(-?\d+(?:\.\d+)?(?:\s*[a-zA-Z/Ω°]+)?)\b"
)


class MinimalQuestionProcessor:
    """
    Stage 01: Minimal Question Processor.
    Deconstructs user queries, identifies participating scientific domains,
    classifies query intent, and extracts target variables and declared constraints.
    """

    def __init__(self, provider: Optional[LLMProvider] = None):
        self.provider = provider

    def classify_intent(self, query: str, domains_count: int) -> QuestionIntent:
        """Determines the primary scientific or engineering objective of the query."""
        q_lower = query.lower()

        # Check for cross-domain transfer
        if any(p in q_lower for p in TRANSFER_PHRASES):
            return QuestionIntent.ANALOGICAL_TRANSFER
        if domains_count >= 2 and any(w in q_lower for w in ["transfer", "analog", "analogy", "map", "bridge"]):
            return QuestionIntent.ANALOGICAL_TRANSFER

        # Check for quantitative calculations
        if any(kw in q_lower for kw in CALCULATION_KEYWORDS) or UNIT_PATTERN.search(query):
            return QuestionIntent.QUANTITATIVE_CALCULATION

        # Check for feasibility checks
        if any(kw in q_lower for kw in FEASIBILITY_KEYWORDS):
            return QuestionIntent.FEASIBILITY_CHECK

        # Check for hypothesis evaluation
        if any(kw in q_lower for kw in HYPOTHESIS_KEYWORDS):
            return QuestionIntent.HYPOTHESIS_EVALUATION

        return QuestionIntent.EXPLANATION

    def detect_domains(self, query: str) -> List[str]:
        """Classifies participating scientific/engineering domain tags using keyword mapping."""
        q_lower = query.lower()
        detected: List[str] = []

        for domain_name, keywords in DOMAIN_KEYWORD_MAP.items():
            if any(re.search(rf"\b{re.escape(kw)}\b", q_lower) for kw in keywords):
                if domain_name not in detected:
                    detected.append(domain_name)

        return detected

    def extract_concepts(self, query: str) -> List[str]:
        """Extracts non-stopword technical concepts and multi-word terms."""
        clean = re.sub(r"[^\w\s\-]", " ", query.lower())
        words = [w for w in clean.split() if len(w) > 2 and w not in STOP_WORDS]
        # Preserve order while removing duplicates
        seen = set()
        concepts = []
        for w in words:
            if w not in seen:
                seen.add(w)
                concepts.append(w)
        return concepts

    def extract_variables_and_constraints(self, query: str) -> tuple[List[str], Dict[str, Any], Dict[str, Any]]:
        """
        Extracts target variables, declared constraints, and numerical parameters.
        Returns (target_variables, identified_constraints, declared_parameters).
        """
        targets: List[str] = []
        constraints: Dict[str, Any] = {}
        parameters: Dict[str, Any] = {}

        # 1. Parameter extraction: e.g. "V = 10 V" or "T = 300 K"
        for match in EQUALITY_PATTERN.finditer(query):
            var_name, op, val = match.groups()
            if op == "=":
                parameters[var_name] = val.strip()
            else:
                constraints[var_name] = f"{op} {val.strip()}"

        # 2. Units extraction without explicit assignment: e.g. "with 10 V and 5 A"
        for match in UNIT_PATTERN.finditer(query):
            num, unit = match.groups()
            # If not already part of an equality assignment
            if not any(num in str(p) for p in parameters.values()):
                key = f"val_{len(parameters) + 1}"
                parameters[key] = f"{num} {unit}"

        # 3. Target variables extraction
        target_phrases = [
            r"(?:calculate|compute|find|determine|solve for|what is)\s+(?:the\s+)?([A-Za-z_][A-Za-z0-9_]*)",
            r"(?:calculate|compute|find|determine|solve for|what is)\s+(?:the\s+)?([A-Za-z]+(?:\s+[A-Za-z]+){1,2})",
        ]
        for pattern in target_phrases:
            for match in re.finditer(pattern, query, re.IGNORECASE):
                candidate = match.group(1).strip()
                words = candidate.split()
                if not any(w.lower() in STOP_WORDS for w in words):
                    if candidate not in targets:
                        targets.append(candidate)

        # 4. Physical assumptions as qualitative constraints
        q_lower = query.lower()
        if "laminar" in q_lower:
            constraints["flow_regime"] = "laminar"
        if "turbulent" in q_lower:
            constraints["flow_regime"] = "turbulent"
        if "steady state" in q_lower or "steady-state" in q_lower:
            constraints["temporal"] = "steady_state"
        if "incompressible" in q_lower:
            constraints["compressibility"] = "incompressible"

        return targets, constraints, parameters

    async def process_question(
        self,
        raw_query: str,
        document_id: Optional[str] = None,
        query_id: Optional[str] = None
    ) -> QuestionSpec:
        """
        Executes Stage 01 Question Processing pipeline.
        Produces a validated QuestionSpec.
        """
        qid = query_id or f"q-{uuid.uuid4().hex[:8]}"
        domains = self.detect_domains(raw_query)
        intent = self.classify_intent(raw_query, len(domains))
        concepts = self.extract_concepts(raw_query)
        targets, constraints, params = self.extract_variables_and_constraints(raw_query)

        return QuestionSpec(
            query_id=qid,
            raw_query=raw_query,
            intent=intent,
            target_variables=targets,
            domain_tags=domains,
            identified_constraints=constraints,
            extracted_concepts=concepts,
            declared_parameters=params,
            document_id=document_id,
            timestamp=datetime.now(timezone.utc)
        )

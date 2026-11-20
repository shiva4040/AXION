import json
import logging
import re
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple

from pydantic import BaseModel, ValidationError

from axion.core.provider import ChatMessage, LLMProvider, MockProvider
from axion.orchestrator import DOMAIN_KEYWORD_MAP
from axion.pipeline.agentic_planning.engine import AgenticPlanningEngine
from axion.pipeline.types import (
    LLMQuestionProvenance,
    QuestionIntent,
    QuestionSpec,
    StructuredQuestionAnalysis,
    SubQuestion,
)

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
    "thermal to electrical", "fluid to electrical", "mechanical to electrical",
    "counteract", "trade-off", "tradeoff", "versus", "trade off"
]

EXTENDED_DOMAIN_KEYWORD_MAP: Dict[str, List[str]] = {
    **DOMAIN_KEYWORD_MAP,
    "aerodynamics:fluid": ["aerodynamic", "aerodynamics", "drag", "lift", "boundary layer", "airfoil", "wind"],
    "physics:photovoltaics": ["photovoltaic", "solar cell", "pv", "irradiance", "insolation", "bandgap"],
    "engineering:automotive": ["vehicle", "car", "powertrain", "chassis", "cruising speed"],
}

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

UNIT_PATTERN = re.compile(
    r"\b(-?\d+(?:\.\d+)?)\s*(V|A|W|J|K|°C|m/s|km/h|m|cm|mm|kg|g|Pa|kPa|MPa|bar|Ohm|Ω|Hz|kHz|MHz|rad/s|mol|N|kN|deg|rad)\b",
    re.IGNORECASE
)

EQUALITY_PATTERN = re.compile(
    r"\b([A-Za-z_][A-Za-z0-9_]*)\s*(=|<|>|<=|>=)\s*(-?\d+(?:\.\d+)?(?:\s*[a-zA-Z/Ω°]+)?)\b"
)

STAGE01_SYSTEM_PROMPT = """You are AXION's Stage 01 Scientific Question Parser.
Your role is SOLELY linguistic and conceptual analysis of scientific and engineering queries.

CRITICAL RULES:
1. You MUST NOT answer the user's scientific question.
2. You MUST NOT calculate numerical values, solve equations, or derive answers.
3. You MUST NOT judge whether user assertions are scientifically true or false.
4. You MUST extract what is explicitly stated and distinguish it from what is inferred.
5. You MUST decompose complex inquiries into structured, dependent subquestions.
6. You MUST specify clear research requirements for Stage 02 knowledge acquisition.
7. You MUST identify any ambiguity, underspecification, or missing physical variables.

You must return a single, valid JSON object matching this schema:
{
  "intended_meaning": "Faithful summary of what the user is asking without answering it",
  "scientific_subject": "Core scientific or engineering subject under inquiry",
  "relevant_concepts": ["concept1", "concept2"],
  "entities": ["entity1", "entity2"],
  "target_variables": ["variable or quantity the user wants found/explained"],
  "explicit_parameters": {"var_name": "value with unit as stated in prompt"},
  "explicit_constraints": {"constraint_name": "condition explicitly stated"},
  "inferred_constraints": {"condition_name": "inferred physical assumption (e.g. ideal gas, laminar)"},
  "problem_type": "quantitative_calculation | analogical_transfer | feasibility_check | hypothesis_evaluation | parameter_estimation | conceptual_explanation",
  "primary_domains": ["domain1", "domain2"],
  "ambiguity_detected": false,
  "ambiguity_notes": ["any ambiguous term or unspecified scope"],
  "missing_information": ["unspecified boundary conditions, fluid properties, or constants required"],
  "clarification_needed": false,
  "clarification_prompt": null,
  "subquestions": [
    {
      "id": "SQ-1",
      "question": "Subquestion statement",
      "target_subject": "Subject or domain",
      "information_needed": ["What specific information or equation is required"],
      "depends_on": [],
      "status": "pending"
    }
  ],
  "research_requirements": ["Requirement 1 for Stage 02 acquisition", "Requirement 2"],
  "subquestion_dependencies": {"SQ-3": ["SQ-1", "SQ-2"]}
}

Return ONLY the JSON object. Do not enclose in markdown fences or include explanatory text."""


class ScientificQuestionProcessor:
    """
    Stage 01: Scientific Question Processor.
    Leverages frontier LLMs (Google Gemini) for deep linguistic understanding, entity extraction,
    and ambiguity detection, paired with AXION's independent validation layer for domain mapping,
    schema adherence, and constraint verification.
    """

    def __init__(
        self,
        provider: Optional[LLMProvider] = None,
        default_timeout: float = 12.0
    ):
        self.provider = provider
        self.default_timeout = default_timeout

    def classify_intent(self, query: str, domains_count: int, problem_type: Optional[str] = None) -> QuestionIntent:
        """Determines the primary scientific or engineering objective of the query."""
        if problem_type:
            pt = problem_type.lower()
            if "analog" in pt or "transfer" in pt:
                return QuestionIntent.ANALOGICAL_TRANSFER
            if "calculation" in pt or "numerical" in pt or "parameter" in pt:
                return QuestionIntent.QUANTITATIVE_CALCULATION
            if "feasibility" in pt or "limit" in pt:
                return QuestionIntent.FEASIBILITY_CHECK
            if "hypothesis" in pt:
                return QuestionIntent.HYPOTHESIS_EVALUATION

        q_lower = query.lower()
        if any(p in q_lower for p in TRANSFER_PHRASES):
            return QuestionIntent.ANALOGICAL_TRANSFER
        if domains_count >= 2 and any(w in q_lower for w in ["transfer", "analog", "analogy", "map", "bridge"]):
            return QuestionIntent.ANALOGICAL_TRANSFER
        if any(kw in q_lower for kw in CALCULATION_KEYWORDS) or UNIT_PATTERN.search(query):
            return QuestionIntent.QUANTITATIVE_CALCULATION
        if any(kw in q_lower for kw in FEASIBILITY_KEYWORDS):
            return QuestionIntent.FEASIBILITY_CHECK
        if any(kw in q_lower for kw in HYPOTHESIS_KEYWORDS):
            return QuestionIntent.HYPOTHESIS_EVALUATION

        return QuestionIntent.EXPLANATION

    def detect_domains(self, query: str) -> List[str]:
        """Classifies participating scientific/engineering domain tags using AXION keyword mapping."""
        q_lower = query.lower()
        detected: List[str] = []
        for domain_name, keywords in EXTENDED_DOMAIN_KEYWORD_MAP.items():
            if any(re.search(rf"\b{re.escape(kw)}", q_lower) for kw in keywords):
                if domain_name not in detected:
                    detected.append(domain_name)
        return detected

    def extract_concepts_rule_based(self, query: str) -> List[str]:
        """Extracts non-stopword technical concepts and multi-word terms."""
        clean = re.sub(r"[^\w\s\-]", " ", query.lower())
        words = [w for w in clean.split() if len(w) > 2 and w not in STOP_WORDS]
        seen = set()
        concepts = []
        for w in words:
            if w not in seen:
                seen.add(w)
                concepts.append(w)
        return concepts

    def extract_variables_and_constraints_rule_based(
        self, query: str
    ) -> Tuple[List[str], Dict[str, Any], Dict[str, Any]]:
        """Extracts target variables, declared constraints, and numerical parameters via regex."""
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

    def _extract_json_payload(self, text: str) -> Optional[Dict[str, Any]]:
        """Robustly extracts JSON payload from LLM responses, stripping code fences if present."""
        clean = text.strip()
        # Direct parse attempt
        try:
            return json.loads(clean)
        except Exception:
            pass

        # Match markdown block ```json ... ``` or ``` ... ```
        fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", clean)
        if fence_match:
            try:
                return json.loads(fence_match.group(1).strip())
            except Exception:
                pass

        # Match outermost braces { ... }
        start = clean.find("{")
        end = clean.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(clean[start:end + 1])
            except Exception:
                pass

        return None

    def validate_and_filter_llm_analysis(
        self,
        raw_query: str,
        analysis: StructuredQuestionAnalysis,
        rule_domains: List[str],
        rule_params: Dict[str, Any],
        rule_constraints: Dict[str, Any],
        rule_targets: List[str],
    ) -> Tuple[Dict[str, Any], Dict[str, str], Dict[str, str], List[str], List[str], bool, bool]:
        """
        AXION Independent Validation Layer:
        - Validates that parameters are genuinely grounded in raw_query text.
        - Reconciles canonical domain tags.
        - Merges rule-based extractions to prevent LLM omissions.
        - Verifies ambiguity and missing information flags.
        """
        validated_params: Dict[str, Any] = dict(rule_params)
        for k, v in analysis.explicit_parameters.items():
            # Check if value or variable name actually appears in raw query
            val_str = str(v)
            num_match = re.search(r"\d+", val_str)
            if num_match and num_match.group() in raw_query:
                validated_params[k] = val_str
            elif k.lower() in raw_query.lower():
                validated_params[k] = val_str

        # Reconcile constraints
        explicit_constraints = dict(analysis.explicit_constraints)
        for ck, cv in rule_constraints.items():
            if ck not in explicit_constraints:
                explicit_constraints[ck] = str(cv)

        inferred_constraints = dict(analysis.inferred_constraints)

        # Merge domain tags (canonical AXION tags guaranteed + recognized LLM domains)
        merged_domains = list(rule_domains)
        for d in analysis.primary_domains:
            norm_d = d.lower().replace(" ", "_").strip()
            matched = False
            for canon in EXTENDED_DOMAIN_KEYWORD_MAP.keys():
                if norm_d in canon or canon in norm_d:
                    if canon not in merged_domains:
                        merged_domains.append(canon)
                    matched = True
                    break
            if not matched and norm_d not in merged_domains and len(norm_d) > 2:
                merged_domains.append(norm_d)

        # Merge target variables
        merged_targets = list(rule_targets)
        for tv in analysis.target_variables:
            if tv not in merged_targets and tv.lower() not in [t.lower() for t in merged_targets]:
                merged_targets.append(tv)

        # Ambiguity and clarification rules
        q_words = [w for w in re.sub(r"[^\w\s]", "", raw_query).split() if w.lower() not in STOP_WORDS]
        ambiguity_detected = analysis.ambiguity_detected or (len(q_words) <= 2 and not rule_params)
        clarification_needed = analysis.clarification_needed or (len(q_words) <= 2 and not rule_targets)

        return (
            validated_params,
            explicit_constraints,
            inferred_constraints,
            merged_domains,
            merged_targets,
            ambiguity_detected,
            clarification_needed,
        )

    def decompose_question_rule_based(
        self,
        raw_query: str,
        domains: List[str],
        concepts: List[str],
        targets: List[str],
        intent: QuestionIntent,
    ) -> Tuple[List[SubQuestion], List[str], Dict[str, List[str]]]:
        """
        Deterministically decomposes scientific inquiries into ordered subquestions
        with dependency tracking and explicit research requirements for Stage 02.
        """
        subquestions: List[SubQuestion] = []
        requirements: List[str] = []
        dependencies: Dict[str, List[str]] = {}

        q_lower = raw_query.lower()

        if intent == QuestionIntent.ANALOGICAL_TRANSFER or len(domains) >= 2 or any(p in q_lower for p in TRANSFER_PHRASES):
            dom1 = domains[0] if len(domains) > 0 else "source_domain"
            dom2 = domains[1] if len(domains) > 1 else "target_domain"

            sq1 = SubQuestion(
                id="SQ-1",
                question=f"What are the governing equations, state variables, and constitutive parameters in {dom1}?",
                target_subject=dom1,
                information_needed=[f"Constitutive equations and flux-potential relations for {dom1}"],
                depends_on=[],
                status="pending"
            )
            sq2 = SubQuestion(
                id="SQ-2",
                question=f"What are the governing equations, dissipation mechanisms, and boundary conditions in {dom2}?",
                target_subject=dom2,
                information_needed=[f"Mathematical formulation, parameters, and operating envelope for {dom2}"],
                depends_on=[],
                status="pending"
            )
            sq3 = SubQuestion(
                id="SQ-3",
                question=f"What is the formal structural mapping, dimensional equivalence, and trade-off coupling between {dom1} and {dom2}?",
                target_subject="Cross-Domain Integration",
                information_needed=["Isomorphism between relational structures and dimensional consistency checks"],
                depends_on=["SQ-1", "SQ-2"],
                status="pending"
            )
            subquestions = [sq1, sq2, sq3]
            dependencies = {"SQ-3": ["SQ-1", "SQ-2"]}
            requirements = [
                f"Empirical constitutive relations and parameters for {dom1}",
                f"Governing conservation laws and boundary conditions for {dom2}",
                f"Applicability limits, dimensional scaling, and analogical transfer criteria"
            ]
        elif intent == QuestionIntent.QUANTITATIVE_CALCULATION or len(targets) > 0:
            target_str = ", ".join(targets) if targets else "target physical quantity"
            sq1 = SubQuestion(
                id="SQ-1",
                question=f"Which fundamental physical law and algebraic/differential equations govern {target_str}?",
                target_subject=domains[0] if domains else "Constitutive Physics",
                information_needed=["Analytical or empirical formula expressing target variables as functions of system parameters"],
                depends_on=[],
                status="pending"
            )
            sq2 = SubQuestion(
                id="SQ-2",
                question=f"What numerical values, boundary constraints, and dimensional units apply to the system parameters?",
                target_subject="System Parameters & Constraints",
                information_needed=["Parameter values, units, and regime validity limits (e.g., Reynolds number, temperature)"],
                depends_on=[],
                status="pending"
            )
            sq3 = SubQuestion(
                id="SQ-3",
                question=f"What is the mathematically verified numerical evaluation and sensitivity of {target_str}?",
                target_subject="Numerical Evaluation & Verification",
                information_needed=["Substitution into governing equations and unit-checked calculation"],
                depends_on=["SQ-1", "SQ-2"],
                status="pending"
            )
            subquestions = [sq1, sq2, sq3]
            dependencies = {"SQ-3": ["SQ-1", "SQ-2"]}
            requirements = [
                f"Governing equations for {target_str}",
                "Numerical values and SI units for specified parameters",
                "Operating validity regimes and physical boundary conditions"
            ]
        else:
            subj = domains[0] if domains else (" ".join(concepts[:2]) if concepts else "System Under Inquiry")
            sq1 = SubQuestion(
                id="SQ-1",
                question=f"What are the foundational physical principles, components, and definitions underlying {subj}?",
                target_subject=subj,
                information_needed=["Definitions, components, and microscopic/macroscopic mechanism"],
                depends_on=[],
                status="pending"
            )
            sq2 = SubQuestion(
                id="SQ-2",
                question=f"How do energy transfer, conservation laws, and external interactions govern its behavior?",
                target_subject="Physical Mechanisms & Dynamics",
                information_needed=["Mathematical or empirical relations describing operation and dynamics"],
                depends_on=["SQ-1"],
                status="pending"
            )
            sq3 = SubQuestion(
                id="SQ-3",
                question=f"What are the practical constraints, efficiency limits, and verification criteria for this phenomenon?",
                target_subject="Limits & Synthesis",
                information_needed=["Thermodynamic, structural, or empirical limits and synthesis"],
                depends_on=["SQ-1", "SQ-2"],
                status="pending"
            )
            subquestions = [sq1, sq2, sq3]
            dependencies = {"SQ-2": ["SQ-1"], "SQ-3": ["SQ-1", "SQ-2"]}
            requirements = [
                f"Peer-reviewed publications on operational principles of {subj}",
                "Mathematical models and empirical parameters",
                "Observed experimental constraints and boundary limits"
            ]

        return subquestions, requirements, dependencies

    async def process_question(
        self,
        raw_query: str,
        document_id: Optional[str] = None,
        query_id: Optional[str] = None
    ) -> QuestionSpec:
        """
        Executes Stage 01 Question Processing pipeline.
        Invokes LLM (Google Gemini) for structured parsing when available,
        applies AXION independent validation, and produces a complete QuestionSpec.
        """
        qid = query_id or f"q-{uuid.uuid4().hex[:8]}"
        t0 = time.perf_counter()

        # Step 1: Execute rule-based baseline extraction
        rule_domains = self.detect_domains(raw_query)
        rule_concepts = self.extract_concepts_rule_based(raw_query)
        rule_targets, rule_constraints, rule_params = self.extract_variables_and_constraints_rule_based(raw_query)
        rule_intent = self.classify_intent(raw_query, len(rule_domains))

        # Execute 13-agent scientific planning engine
        agentic_state_dict: Optional[Dict[str, Any]] = None
        try:
            agentic_engine = AgenticPlanningEngine(llm_provider=self.provider)
            agentic_state = agentic_engine.plan_research(raw_query)
            agentic_state_dict = agentic_state.model_dump()
        except Exception as e:
            logger.warning("Agentic research planning failed: %s", e)

        llm_provenance = LLMQuestionProvenance(
            model_name="rule_based_fallback",
            fallback_rule_based=True,
            parsed_successfully=True,
            validation_passed=True
        )

        analysis: Optional[StructuredQuestionAnalysis] = None

        # Step 2: Use LLM provider if configured and not mock
        if self.provider is not None and not isinstance(self.provider, MockProvider):
            try:
                messages = [
                    ChatMessage(role="system", content=STAGE01_SYSTEM_PROMPT),
                    ChatMessage(role="user", content=f"Process this scientific inquiry:\n\n{raw_query}")
                ]
                resp = await self.provider.generate_text(
                    messages=messages,
                    temperature=0.0,
                    max_tokens=1500
                )
                dt_ms = (time.perf_counter() - t0) * 1000.0

                raw_json = self._extract_json_payload(resp.text)
                if raw_json:
                    analysis = StructuredQuestionAnalysis.model_validate(raw_json)
                    llm_provenance = LLMQuestionProvenance(
                        model_name=resp.model or getattr(self.provider, "model", "gemini-3.1-flash-lite"),
                        latency_ms=round(dt_ms, 2),
                        prompt_tokens=resp.prompt_tokens,
                        completion_tokens=resp.completion_tokens,
                        total_tokens=resp.total_tokens,
                        parsed_successfully=True,
                        validation_passed=True,
                        fallback_rule_based=False
                    )
                else:
                    logger.warning("Stage 01: LLM response did not contain valid JSON payload. Text: %s", resp.text[:200])
                    llm_provenance = LLMQuestionProvenance(
                        model_name=getattr(self.provider, "model", "unknown"),
                        latency_ms=round(dt_ms, 2),
                        prompt_tokens=resp.prompt_tokens,
                        completion_tokens=resp.completion_tokens,
                        total_tokens=resp.total_tokens,
                        error="Failed to extract JSON from LLM response",
                        fallback_rule_based=True
                    )
            except Exception as e:
                dt_ms = (time.perf_counter() - t0) * 1000.0
                logger.error("Stage 01 LLM invocation error: %s", e)
                llm_provenance = LLMQuestionProvenance(
                    model_name=getattr(self.provider, "model", "unknown"),
                    latency_ms=round(dt_ms, 2),
                    error=str(e),
                    fallback_rule_based=True
                )
                # In strict mode, propagate if explicitly requested by provider
                if getattr(self.provider, "strict", False):
                    raise e

        # Step 3: AXION Independent Validation Layer
        if analysis:
            (
                final_params,
                explicit_constraints,
                inferred_constraints,
                final_domains,
                final_targets,
                ambiguity_detected,
                clarification_needed,
            ) = self.validate_and_filter_llm_analysis(
                raw_query=raw_query,
                analysis=analysis,
                rule_domains=rule_domains,
                rule_params=rule_params,
                rule_constraints=rule_constraints,
                rule_targets=rule_targets,
            )
            final_intent = self.classify_intent(raw_query, len(final_domains), analysis.problem_type)
            final_concepts = list(dict.fromkeys(rule_concepts + analysis.relevant_concepts))

            # Reconcile subquestions & research requirements
            if analysis.subquestions and len(analysis.subquestions) > 0:
                final_subquestions = analysis.subquestions
                final_reqs = analysis.research_requirements or [
                    f"Research literature on {analysis.scientific_subject or raw_query[:30]}"
                ]
                final_deps = analysis.subquestion_dependencies or {}
            else:
                rule_sqs, rule_reqs, rule_deps = self.decompose_question_rule_based(
                    raw_query=raw_query,
                    domains=final_domains,
                    concepts=final_concepts,
                    targets=final_targets,
                    intent=final_intent,
                )
                final_subquestions = rule_sqs
                final_reqs = rule_reqs
                final_deps = rule_deps

            return QuestionSpec(
                query_id=qid,
                raw_query=raw_query,
                intent=final_intent,
                target_variables=final_targets,
                domain_tags=final_domains,
                identified_constraints={**explicit_constraints, **inferred_constraints},
                extracted_concepts=final_concepts,
                declared_parameters=final_params,
                document_id=document_id,
                timestamp=datetime.now(timezone.utc),
                # Extended structured fields
                intended_meaning=analysis.intended_meaning,
                scientific_subject=analysis.scientific_subject,
                entities=analysis.entities,
                explicit_constraints=explicit_constraints,
                inferred_constraints=inferred_constraints,
                problem_type=analysis.problem_type,
                ambiguity_detected=ambiguity_detected,
                ambiguity_notes=analysis.ambiguity_notes,
                missing_information=analysis.missing_information,
                clarification_needed=clarification_needed,
                clarification_prompt=analysis.clarification_prompt,
                llm_provenance=llm_provenance,
                subquestions=final_subquestions,
                research_requirements=final_reqs,
                subquestion_dependencies=final_deps,
                agentic_research_state=agentic_state_dict,
            )

        # Step 4: Fallback / Deterministic Rule-Based Assembly
        # Detect basic missing information / ambiguity for rule-based path
        q_words = [w for w in re.sub(r"[^\w\s]", "", raw_query).split() if w.lower() not in STOP_WORDS]
        ambiguity_detected = len(q_words) <= 2 and not rule_params
        missing_info = ["Specific numerical parameters or boundary conditions"] if ambiguity_detected else []

        fallback_sqs, fallback_reqs, fallback_deps = self.decompose_question_rule_based(
            raw_query=raw_query,
            domains=rule_domains,
            concepts=rule_concepts,
            targets=rule_targets,
            intent=rule_intent,
        )

        return QuestionSpec(
            query_id=qid,
            raw_query=raw_query,
            intent=rule_intent,
            target_variables=rule_targets,
            domain_tags=rule_domains,
            identified_constraints=rule_constraints,
            extracted_concepts=rule_concepts,
            declared_parameters=rule_params,
            document_id=document_id,
            timestamp=datetime.now(timezone.utc),
            # Extended fields in deterministic mode
            intended_meaning=raw_query.strip(),
            scientific_subject=" ".join(rule_domains) if rule_domains else "General Science",
            entities=[],
            explicit_constraints={k: str(v) for k, v in rule_constraints.items()},
            inferred_constraints={},
            problem_type=rule_intent.value.lower(),
            ambiguity_detected=ambiguity_detected,
            ambiguity_notes=["Short or underspecified prompt"] if ambiguity_detected else [],
            missing_information=missing_info,
            clarification_needed=ambiguity_detected,
            clarification_prompt="Could you specify the governing system or numerical parameters?" if ambiguity_detected else None,
            llm_provenance=llm_provenance,
            subquestions=fallback_sqs,
            research_requirements=fallback_reqs,
            subquestion_dependencies=fallback_deps,
            agentic_research_state=agentic_state_dict,
        )


# Backward-compatible alias
MinimalQuestionProcessor = ScientificQuestionProcessor

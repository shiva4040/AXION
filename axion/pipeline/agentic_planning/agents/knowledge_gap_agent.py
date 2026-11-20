"""Agent 11: Knowledge Gap and Constraint Agent.

Identifies missing parameters, unverified assumptions, practical engineering limitations,
and formulates targeted directives for Stage 02 resolution.
"""

from typing import Any, Dict, List
import logging
from axion.pipeline.agentic_planning.base_agent import BaseResearchAgent
from axion.pipeline.agentic_planning.types import (
    AgentRole,
    AgenticResearchState,
    KnowledgeGap,
    FindingType,
)

logger = logging.getLogger(__name__)


class KnowledgeGapAgent(BaseResearchAgent):
    """Detects missing empirical data, unverified assumptions, and operational constraints."""

    def __init__(self, llm_provider: Any = None):
        super().__init__(
            role=AgentRole.KNOWLEDGE_GAP,
            name="Knowledge Gap and Constraint Agent",
            llm_provider=llm_provider,
        )

    def execute(self, state: AgenticResearchState, context: Dict[str, Any] = None) -> AgenticResearchState:
        self.set_active(state)
        query = state.original_question

        prompt = f"""You are the AXION Knowledge Gap and Constraint Agent.
Analyze the scientific research question:
"{query}"

Review the existing findings across domains, equations, processes, and materials.
Identify:
1. Missing empirical constants, unknown variables, and operating parameters.
2. Unverified scientific or engineering assumptions.
3. Practical physical, thermal, or economic constraints.
4. Specific Stage 02 acquisition directives to resolve these gaps.

Return JSON in this exact structure:
{{
  "knowledge_gaps": [
    {{
      "gap_id": "GAP-01",
      "description": "Specific motor casing temperature profile and accessible thermal flux are unknown without motor rating and duty cycle.",
      "gap_type": "missing_parameter",
      "severity": "CRITICAL",
      "impact_on_research": "Prevents exact calculation of net electrical power output and payback period.",
      "resolution_approach": "Acquire empirical temperature field maps for standard 15-75 kW TEFC induction motors under IEC 60034 test standards.",
      "recommended_stage02_searches": [
        "\"induction motor\" casing surface temperature measurement infrared",
        "\"TEFC motor\" external thermal map \"casing heat flux\""
      ]
    }},
    {{
      "gap_id": "GAP-02",
      "description": "Contact thermal resistance across curved or finned motor casing interfaces.",
      "gap_type": "empirical_uncertainty",
      "severity": "HIGH",
      "impact_on_research": "High interface resistance will reduce the effective Delta T across the TEG legs by 30-50%, drastically reducing harvested voltage.",
      "resolution_approach": "Retrieve experimental thermal contact conductance data for compressible graphite sheets under 0.5-1.5 MPa mounting pressure on cast iron.",
      "recommended_stage02_searches": [
        "\"thermal contact resistance\" cast iron \"pyrolytic graphite\"",
        "clamping pressure TIM \"heat flux\" degradation"
      ]
    }},
    {{
      "gap_id": "GAP-03",
      "description": "Unverified assumption that TEG module operates at continuous steady-state temperature.",
      "gap_type": "unverified_assumption",
      "severity": "MEDIUM",
      "impact_on_research": "Industrial motors undergo load cycling and stops, subjecting TEGs to thermal cycling fatigue and transient power drops.",
      "resolution_approach": "Review thermal transient response models and thermal-cycling fatigue data for soldered Bi2Te3 junctions.",
      "recommended_stage02_searches": [
        "thermoelectric module \"thermal cycling\" reliability fatigue",
        "transient thermal response TEG motor startup"
      ]
    }},
    {{
      "gap_id": "GAP-04",
      "description": "Cold-side heatsink airflow interaction with motor cooling fan wake.",
      "gap_type": "constraint",
      "severity": "MEDIUM",
      "impact_on_research": "Placing a heatsink in the motor cooling fan airstream may increase cold-side heat rejection but disrupt the motor's own convective cooling.",
      "resolution_approach": "Evaluate aerodynamic drag and convective heat transfer coefficients in TEFC fan slipstreams.",
      "recommended_stage02_searches": [
        "TEFC motor fan aerodynamic slipstream convective cooling",
        "parasitic pressure drop motor heatsink airflow"
      ]
    }}
  ]
}}
"""

        parsed = self.call_llm_json(prompt, state)
        if not parsed or "knowledge_gaps" not in parsed:
            parsed = self._fallback_knowledge_gaps(query)

        gaps = []
        for g in parsed.get("knowledge_gaps", []):
            try:
                gap = KnowledgeGap(
                    gap_id=g.get("gap_id", f"GAP-{len(gaps) + 1:02d}"),
                    description=g.get("description", ""),
                    gap_type=g.get("gap_type", "missing_parameter"),
                    severity=g.get("severity", "MEDIUM"),
                    impact_on_research=g.get("impact_on_research", ""),
                    resolution_approach=g.get("resolution_approach", ""),
                    recommended_stage02_searches=g.get("recommended_stage02_searches", []),
                )
                gaps.append(gap)
            except Exception as e:
                logger.warning(f"Error parsing knowledge gap: {e}")

        state.knowledge_gaps = gaps

        # Record finding
        self.record_finding(
            state=state,
            finding_type=FindingType.KNOWLEDGE_GAP,
            title=f"Discovered {len(gaps)} Critical Knowledge Gaps & Practical Constraints",
            content=f"Identified missing thermal parameters, interfacial uncertainties, and aerodynamic constraints with Stage 02 directives.",
            scientific_basis="Uncertainty quantification, thermal resistance budgeting, and industrial machine reliability analysis.",
            confidence=0.94,
            tags=["knowledge_gaps", "constraints", "uncertainties", "stage02_directives"],
        )

        self.set_completed(state, findings_count=len(gaps))
        return state

    def _fallback_knowledge_gaps(self, query: str) -> Dict[str, Any]:
        """Deterministic knowledge gaps fallback."""
        return {
            "knowledge_gaps": [
                {
                    "gap_id": "GAP-01",
                    "description": "Specific motor casing temperature and accessible conductive heat flux are unknown without motor power rating and loading history.",
                    "gap_type": "missing_parameter",
                    "severity": "CRITICAL",
                    "impact_on_research": "Uncertainty in accessible temperature differential directly scales power output predictions.",
                    "resolution_approach": "Retrieve experimental thermal data for 15-55 kW TEFC induction motors under IEC 60034 standards.",
                    "recommended_stage02_searches": [
                        "\"induction motor\" casing temperature profile IEC 60034",
                        "TEFC motor external surface heat flux measurement"
                    ],
                },
                {
                    "gap_id": "GAP-02",
                    "description": "Interfacial contact thermal resistance across curved cast iron casing surface.",
                    "gap_type": "empirical_uncertainty",
                    "severity": "HIGH",
                    "impact_on_research": "Excessive contact resistance severely degrades effective Delta T across TEG couples.",
                    "resolution_approach": "Search for contact conductance data for pyrolytic graphite sheets and phase change pads on cast iron.",
                    "recommended_stage02_searches": [
                        "thermal contact resistance cast iron TIM graphite",
                        "clamping pressure interface resistance motor casing"
                    ],
                },
                {
                    "gap_id": "GAP-03",
                    "description": "Motor load cycling effects and thermal fatigue on thermoelectric solder joints.",
                    "gap_type": "unverified_assumption",
                    "severity": "MEDIUM",
                    "impact_on_research": "Assumes continuous thermal steady state; real factory machines cycle frequently causing joint shear stress.",
                    "resolution_approach": "Acquire thermal fatigue lifetime models for Bi2Te3 modules under cyclic temperature differentials.",
                    "recommended_stage02_searches": [
                        "thermoelectric module reliability thermal cycling industrial",
                        "solder joint shear stress TEG thermal expansion mismatch"
                    ],
                },
            ]
        }

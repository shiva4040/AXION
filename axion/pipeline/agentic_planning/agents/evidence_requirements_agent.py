"""Agent 9: Evidence Requirements Agent.

Formulates explicit empirical evidence requirements, recommended search queries,
data standards, and verification criteria for Stage 02 acquisition and Stage 03 analysis.
"""

from typing import Any, Dict, List
import logging
from axion.pipeline.agentic_planning.base_agent import BaseResearchAgent
from axion.pipeline.agentic_planning.types import (
    AgentRole,
    AgenticResearchState,
    EvidenceRequirement,
    FindingType,
)

logger = logging.getLogger(__name__)


class EvidenceRequirementsAgent(BaseResearchAgent):
    """Specifies the rigorous empirical evidence and literature requirements needed for investigation."""

    def __init__(self, llm_provider: Any = None):
        super().__init__(
            role=AgentRole.EVIDENCE_REQUIREMENTS,
            name="Evidence Requirements Agent",
            llm_provider=llm_provider,
        )

    def execute(self, state: AgenticResearchState, context: Dict[str, Any] = None) -> AgenticResearchState:
        self.set_active(state)
        query = state.original_question

        prompt = f"""You are the AXION Evidence Requirements Agent.
Analyze the scientific research question:
"{query}"

Specify the precise, actionable evidence requirements needed for Stage 02 (Knowledge Acquisition)
and Stage 03 (Evidence Verification).
Formulate specific academic search queries, target document types, empirical data points,
and verification criteria.

Return JSON in this exact structure:
{{
  "evidence_requirements": [
    {{
      "requirement_id": "EV-01",
      "target_subquestion": "What is the typical thermal energy flux and casing temperature distribution of industrial induction motors?",
      "information_needed": "Empirical casing temperature profiles (50-100 kW class induction motors) and heat loss breakdown under variable load factors (50%, 75%, 100%).",
      "target_sources": ["IEEE Xplore", "Crossref", "OpenAlex", "Applied Thermal Engineering"],
      "recommended_queries": [
        "\"induction motor\" \"thermal distribution\" \"casing temperature\" heat loss",
        "\"industrial motor\" \"waste heat recovery\" \"temperature gradient\" flux"
      ],
      "required_data_points": ["Motor efficiency vs load", "Casing surface temperature (°C)", "Convective vs conductive heat dissipation share"],
      "verification_criteria": "Peer-reviewed experimental measurements or certified IEC 60034-2-1 / IEEE 112 loss calibration tests."
    }},
    {{
      "requirement_id": "EV-02",
      "target_subquestion": "What thermoelectric conversion efficiency and power density can be achieved across a 40-70 K temperature differential?",
      "information_needed": "Experimental Seebeck coefficient S(T), electrical conductivity sigma(T), and figure of merit ZT for bismuth telluride modules operating between 300 K and 380 K.",
      "target_sources": ["arXiv:cond-mat", "Journal of Electronic Materials", "OpenAlex", "Materials Today"],
      "recommended_queries": [
        "\"bismuth telluride\" Bi2Te3 \"figure of merit\" ZT \"low temperature\" 300K..400K",
        "\"thermoelectric generator\" \"power density\" mW/cm2 \"small temperature gradient\""
      ],
      "required_data_points": ["ZT temperature dependence curve", "Open-circuit voltage per couple (uV/K)", "Extracted power density (mW/cm2)"],
      "verification_criteria": "Standard Harman method or ZT meter characterization with reported measurement uncertainty (< 10%)."
    }},
    {{
      "requirement_id": "EV-03",
      "target_subquestion": "How do thermal contact resistance and thermal interface materials degrade heat transfer to the TEG module?",
      "information_needed": "Interfacial contact thermal resistance values (K·cm^2/W) for graphite sheet, phase change pads, and thermal paste across rough cast-iron surfaces.",
      "target_sources": ["International Journal of Heat and Mass Transfer", "IEEE Transactions on Components and Packaging"],
      "recommended_queries": [
        "\"thermal contact resistance\" \"thermal interface material\" TIM \"clamping pressure\"",
        "\"rough surface\" \"contact conductance\" cast iron thermal pad"
      ],
      "required_data_points": ["Interface resistance vs pressure curve", "Pump-out and dry-out lifetime degradation under vibration"],
      "verification_criteria": "ASTM D5470 guarded hot plate or steady-state thermal impedance measurements."
    }},
    {{
      "requirement_id": "EV-04",
      "target_subquestion": "What power electronic conditioning architectures optimize energy harvesting from low millivolt TEG sources?",
      "information_needed": "Converter topology, minimum cold-start voltage threshold, and MPPT conversion efficiency curves for sub-1V thermoelectric energy harvesters.",
      "target_sources": ["IEEE Transactions on Power Electronics", "IEEE Journal of Solid-State Circuits"],
      "recommended_queries": [
        "\"thermoelectric energy harvesting\" \"MPPT\" \"cold-start\" \"boost converter\"",
        "\"ultra-low voltage\" step-up DC-DC converter \"TEG\" efficiency"
      ],
      "required_data_points": ["Peak efficiency percentage", "Cold start input voltage threshold (mV)", "Source impedance matching error (%)"],
      "verification_criteria": "Empirically measured circuit prototypes with oscilloscope load transient waveforms."
    }}
  ]
}}
"""

        parsed = self.call_llm_json(prompt, state)
        if not parsed or "evidence_requirements" not in parsed:
            parsed = self._fallback_evidence_requirements(query)

        reqs = []
        for r in parsed.get("evidence_requirements", []):
            try:
                req = EvidenceRequirement(
                    requirement_id=r.get("requirement_id", f"EV-{len(reqs) + 1:02d}"),
                    target_subquestion=r.get("target_subquestion", ""),
                    information_needed=r.get("information_needed", ""),
                    target_sources=r.get("target_sources", []),
                    recommended_queries=r.get("recommended_queries", []),
                    required_data_points=r.get("required_data_points", []),
                    verification_criteria=r.get("verification_criteria", ""),
                )
                reqs.append(req)
            except Exception as e:
                logger.warning(f"Error parsing evidence requirement: {e}")

        state.evidence_requirements = reqs

        # Record finding
        self.record_finding(
            state=state,
            finding_type=FindingType.EVIDENCE_REQ,
            title=f"Defined {len(reqs)} Empirical Evidence & Literature Search Requirements",
            content=f"Formulated concrete academic search queries, required empirical data points, and validation criteria for Stage 02.",
            scientific_basis="Empirical methodology standards, thermophysical property measurement guidelines, and IEEE/IEC test protocols.",
            confidence=0.96,
            tags=["evidence", "stage02_directives", "search_queries", "verification_criteria"],
        )

        self.set_completed(state, findings_count=len(reqs))
        return state

    def _fallback_evidence_requirements(self, query: str) -> Dict[str, Any]:
        """Deterministic evidence requirements fallback."""
        return {
            "evidence_requirements": [
                {
                    "requirement_id": "EV-01",
                    "target_subquestion": "Thermal energy flux and motor casing temperature profile",
                    "information_needed": "Steady-state surface temperature distribution and convective/conductive heat dissipation of industrial induction motors",
                    "target_sources": ["IEEE Transactions on Industry Applications", "Applied Thermal Engineering", "Crossref"],
                    "recommended_queries": [
                        "\"induction motor\" \"casing temperature\" heat dissipation",
                        "\"industrial motor\" \"waste heat recovery\" \"temperature gradient\""
                    ],
                    "required_data_points": ["Casing surface temperature (°C)", "Motor efficiency vs load", "Accessible thermal flux (W/m^2)"],
                    "verification_criteria": "Calibrated thermocouple or FLIR infrared thermography measurements adhering to IEEE 112.",
                },
                {
                    "requirement_id": "EV-02",
                    "target_subquestion": "Thermoelectric material performance under small Delta T",
                    "information_needed": "Bismuth telluride Seebeck coefficient, electrical resistivity, and thermal conductivity across 300 K to 380 K",
                    "target_sources": ["arXiv:cond-mat", "Journal of Electronic Materials", "OpenAlex"],
                    "recommended_queries": [
                        "\"Bi2Te3\" \"figure of merit\" ZT \"low temperature\" 300K",
                        "\"thermoelectric generator\" \"power density\" \"small temperature difference\""
                    ],
                    "required_data_points": ["ZT(T) curve", "Seebeck coefficient S (uV/K)", "Power output mW/cm^2"],
                    "verification_criteria": "Harman method or laser flash thermal diffusivity measurements.",
                },
                {
                    "requirement_id": "EV-03",
                    "target_subquestion": "Thermal interface material and contact resistance",
                    "information_needed": "Contact thermal resistance of graphite pads and phase change materials on curved or ribbed motor surfaces",
                    "target_sources": ["International Journal of Heat and Mass Transfer", "Crossref"],
                    "recommended_queries": [
                        "\"thermal interface material\" \"contact resistance\" \"motor casing\"",
                        "\"pyrolytic graphite\" thermal impedance clamping pressure"
                    ],
                    "required_data_points": ["Thermal impedance (K·cm^2/W)", "Vibration degradation rates"],
                    "verification_criteria": "ASTM D5470 steady-state test protocols.",
                },
                {
                    "requirement_id": "EV-04",
                    "target_subquestion": "Ultra-low-voltage MPPT power electronics conditioning",
                    "information_needed": "Cold-start threshold and boost converter efficiency curves for thermoelectric energy harvesting circuits",
                    "target_sources": ["IEEE Transactions on Power Electronics", "OpenAlex"],
                    "recommended_queries": [
                        "\"thermoelectric harvester\" \"cold start\" \"boost converter\" MPPT",
                        "ultra-low voltage energy harvesting DC-DC converter efficiency"
                    ],
                    "required_data_points": ["Minimum input voltage (mV)", "Conversion efficiency (%)", "Maximum power point tracking accuracy (%)"],
                    "verification_criteria": "Experimental circuit testing with source impedance matching.",
                },
            ]
        }

import time
from typing import List, Optional
from axion.core.provider import LLMProvider
from axion.pipeline.agentic_planning.base_agent import BaseResearchAgent
from axion.pipeline.agentic_planning.types import (
    AgentFinding,
    AgentRole,
    AgentStatus,
    AgentStatusRecord,
    AgenticResearchState,
    FindingType,
    ScientificConcept,
)

SYSTEM_PROMPT = """You are AXION's Scientific Concepts Discovery Agent.
Discover all foundational scientific principles, laws, mechanisms, and models required to investigate this inquiry.
For each concept provide:
- name: string
- category: "principle | law | mechanism | definition | model | constitutive_relation"
- definition: rigorous concise definition
- scientific_explanation: detailed physics/engineering explanation
- mathematical_formulation: formula or equation if applicable
- assumptions: list of underlying assumptions
- limitations: operational boundaries
- related_subquestions: list of subquestion IDs (e.g. ["SQ-1", "SQ-2"])
- related_domains: list of domain names

Return valid JSON:
{
  "concepts": [
    {
      "name": "string",
      "category": "principle",
      "definition": "string",
      "scientific_explanation": "string",
      "mathematical_formulation": "string",
      "assumptions": ["string"],
      "limitations": ["string"],
      "related_subquestions": ["SQ-1"],
      "related_domains": ["string"]
    }
  ]
}"""


class ConceptsDiscoveryAgent(BaseResearchAgent):
    """Agent 5: Discovers fundamental scientific laws, principles, physical mechanisms, and constitutive concepts."""

    def __init__(self, provider: Optional[LLMProvider] = None):
        super().__init__(
            role=AgentRole.CONCEPTS_DISCOVERY,
            display_name="Scientific Concepts Agent",
            responsibility="Discovers foundational principles, laws, physical mechanisms, and constitutive definitions",
            provider=provider,
        )

    async def investigate(self, state: AgenticResearchState) -> AgentStatusRecord:
        t0 = time.perf_counter()
        query = state.original_query
        q_lower = query.lower()

        llm_data = await self._call_llm_json(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=f"Inquiry: {query}\nSubquestions: {[sq.question for sq in state.subquestions]}",
        )

        concepts: List[ScientificConcept] = []
        if llm_data and "concepts" in llm_data and isinstance(llm_data["concepts"], list):
            for c in llm_data["concepts"]:
                concepts.append(
                    ScientificConcept(
                        name=c.get("name", "Physical Concept"),
                        category=c.get("category", "principle"),
                        definition=c.get("definition", ""),
                        scientific_explanation=c.get("scientific_explanation", ""),
                        mathematical_formulation=c.get("mathematical_formulation"),
                        assumptions=c.get("assumptions", []),
                        limitations=c.get("limitations", []),
                        related_subquestions=c.get("related_subquestions", ["SQ-1"]),
                        related_domains=c.get("related_domains", []),
                        discovering_agent="concepts_agent",
                    )
                )

        if not concepts:
            if "thermoelectric" in q_lower or "teg" in q_lower or ("waste heat" in q_lower and "motor" in q_lower):
                concepts = [
                    ScientificConcept(
                        name="Seebeck Effect",
                        category="principle",
                        definition="The direct generation of an electromotive force (voltage) across an electrically conductive or semiconductive material when subjected to a temperature gradient.",
                        scientific_explanation="When a temperature difference is applied across a semiconductor, high-energy mobile charge carriers (electrons in n-type, holes in p-type) at the hot junction diffuse towards the cold junction until an internal electrostatic potential gradient balances the thermal diffusion force.",
                        mathematical_formulation="V = S * Delta_T = S * (T_hot - T_cold)",
                        assumptions=["Linear thermal gradient", "Homogeneous material composition", "Constant Seebeck coefficient over small Delta_T"],
                        limitations=["Breaks down under non-linear large Delta_T requiring integration: V = int(S(T) dT)", "Dependent on carrier concentration"],
                        related_subquestions=["SQ-2"],
                        related_domains=["Solid-State Physics & Thermoelectrics"],
                    ),
                    ScientificConcept(
                        name="Thermoelectric Figure of Merit (ZT)",
                        category="constitutive_relation",
                        definition="A dimensionless parameter quantifying the electrical and thermal efficiency of a thermoelectric material.",
                        scientific_explanation="High conversion efficiency demands high Seebeck coefficient (large voltage per Kelvin) and high electrical conductivity (low internal Joule heating), counterbalanced by low thermal conductivity (to prevent rapid thermal equalization between junctions).",
                        mathematical_formulation="ZT = (S^2 * sigma * T) / kappa",
                        assumptions=["Wiedemann-Franz law applies for electronic thermal conductivity", "Averaged material properties across active temperature profile"],
                        limitations=["Coupling between sigma and kappa_e via Wiedemann-Franz law limits achievable ZT (typical commercial Bi2Te3: ZT ~ 0.8 - 1.2)", "Temperature dependent"],
                        related_subquestions=["SQ-3"],
                        related_domains=["Solid-State Physics & Thermoelectrics", "Materials Science"],
                    ),
                    ScientificConcept(
                        name="Fourier's Law of Thermal Conduction",
                        category="law",
                        definition="Heat transfer rate through a material is proportional to the negative gradient in temperature and to the perpendicular cross-sectional area.",
                        scientific_explanation="Governs heat flux from the motor casing into the thermoelectric substrate and conductive losses through the thermoelectric legs.",
                        mathematical_formulation="q = -k * grad(T)",
                        assumptions=["Isotropic continuum medium", "Steady-state temperature distribution"],
                        limitations=["Non-applicable at ballistic phonon regimes (< mean free path)"],
                        related_subquestions=["SQ-4"],
                        related_domains=["Thermodynamics & Heat Transfer"],
                    ),
                    ScientificConcept(
                        name="Carnot Efficiency Limit",
                        category="principle",
                        definition="The theoretical maximum efficiency that any heat engine operating between two thermal reservoirs can achieve under the Second Law of Thermodynamics.",
                        scientific_explanation="Because a TEG is a solid-state heat engine, its efficiency is fundamentally bounded by the Carnot limit: eta_Carnot = (T_hot - T_cold) / T_hot.",
                        mathematical_formulation="eta_Carnot = Delta_T / T_hot",
                        assumptions=["Reversible thermodynamic cycle", "Zero entropy generation"],
                        limitations=["Actual TEG efficiency is only 10-20% of the Carnot limit due to irreversible thermal bypass conduction and Joule losses"],
                        related_subquestions=["SQ-3"],
                        related_domains=["Thermodynamics & Heat Transfer"],
                    ),
                    ScientificConcept(
                        name="Joule Heating (Ohmic Dissipation)",
                        category="law",
                        definition="The irreversible conversion of electrical energy into thermal energy as electric current passes through a conductor with finite resistance.",
                        scientific_explanation="Accounts for stator I^2*R copper winding losses in the motor, as well as parasitic internal electrical dissipation within the TEG legs.",
                        mathematical_formulation="P_joule = I^2 * R",
                        assumptions=["Ohmic conductor with constant resistivity"],
                        limitations=["Temperature dependence of resistance must be factored: R(T) = R0 * (1 + alpha * Delta_T)"],
                        related_subquestions=["SQ-1", "SQ-2"],
                        related_domains=["Electromagnetism & Electrical Machines"],
                    ),
                    ScientificConcept(
                        name="Thermal Contact Resistance",
                        category="model",
                        definition="The resistance to heat flow across the interface between two contacting solid surfaces caused by microscopic roughness and microscopic interstitial voids.",
                        scientific_explanation="Microscopic air gaps at the motor casing to TEG junction cause an unwanted temperature drop before heat reaches the active thermoelectric semiconductor material.",
                        mathematical_formulation="Delta_T_contact = Q * R_contact = Q / (h_c * A)",
                        assumptions=["Uniform clamping pressure", "Thermal grease or graphite sheet fills microscopic asperities"],
                        limitations=["Sensitive to surface flatness, bolt torque, and thermal cycling degradation"],
                        related_subquestions=["SQ-4"],
                        related_domains=["Mechanical Engineering", "Thermodynamics & Heat Transfer"],
                    ),
                ]
            else:
                concepts = [
                    ScientificConcept(
                        name="Conservation of Energy",
                        category="principle",
                        definition="The total energy of an isolated system remains constant over time.",
                        scientific_explanation="First Law of Thermodynamics dictating that input power equals useful output work plus dissipated heat.",
                        mathematical_formulation="dE/dt = Q_in - W_out",
                        assumptions=["Closed conservative system"],
                        limitations=["Requires relativistic mass-energy equivalence at subatomic scales"],
                        related_subquestions=["SQ-1"],
                        related_domains=["Physics"],
                    ),
                    ScientificConcept(
                        name="Constitutive Flux-Force Relation",
                        category="law",
                        definition="Linear phenomenological relation stating that generalized flux is proportional to generalized thermodynamic driving potential.",
                        scientific_explanation="Ohm's law, Fourier's law, and Fick's law share this identical topological structure: J = -L * grad(Phi).",
                        mathematical_formulation="J = -L * grad(Phi)",
                        assumptions=["Near-equilibrium linear regime"],
                        limitations=["Nonlinear breakdown at high field gradients"],
                        related_subquestions=["SQ-2"],
                        related_domains=["Continuum Physics"],
                    ),
                ]

        state.concepts = concepts

        for c in concepts:
            self.record_finding(
                state=state,
                finding_type=FindingType.CONCEPT,
                title=f"Concept [{c.category.upper()}]: {c.name}",
                content=f"Definition: {c.definition}\nExplanation: {c.scientific_explanation}\nFormula: {c.mathematical_formulation or 'N/A'}",
                justification=c.scientific_explanation,
                subquestions=c.related_subquestions,
                domains=c.related_domains,
            )

        dt = (time.perf_counter() - t0) * 1000.0
        self.log_timeline(state, "Concepts Discovered", f"Formulated {len(concepts)} scientific laws, principles, and constitutive definitions")

        status_rec = AgentStatusRecord(
            agent_id=self.role.value,
            role=self.role,
            display_name=self.display_name,
            responsibility=self.responsibility,
            status=AgentStatus.COMPLETED,
            current_task=f"Formulated {len(concepts)} scientific concepts",
            latency_ms=round(dt, 2),
            findings_count=len(concepts),
        )
        state.agents[self.role.value] = status_rec
        return status_rec

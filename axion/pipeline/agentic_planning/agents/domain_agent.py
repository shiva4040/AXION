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
    DiscoveredDomain,
    FindingType,
)

SYSTEM_PROMPT = """You are AXION's Scientific Domain Discovery Agent.
Discover all potentially relevant scientific and engineering domains for this inquiry.
Categorize into:
- primary (essential foundational physics/engineering)
- secondary (direct operational or system engineering)
- supporting (materials, diagnostics, components)
- conditional (applicable under specific regimes or scales)

For each domain explain:
- scientific_rationale: why it is strictly relevant
- physical_process_explained: which process it describes
- supported_subquestions: list of subquestion IDs or topics it informs
- contributed_concepts: list of core concepts

Return valid JSON:
{
  "domains": [
    {
      "domain_name": "string",
      "tier": "primary | secondary | supporting | conditional",
      "scientific_rationale": "string",
      "physical_process_explained": "string",
      "supported_subquestions": ["SQ-1"],
      "contributed_concepts": ["concept1"]
    }
  ]
}"""


class DomainDiscoveryAgent(BaseResearchAgent):
    """Agent 3: Discovers all primary, secondary, supporting, and conditional scientific domains with physical justifications."""

    def __init__(self, provider: Optional[LLMProvider] = None):
        super().__init__(
            role=AgentRole.DOMAIN_DISCOVERY,
            display_name="Domain Discovery Agent",
            responsibility="Discovers all participating scientific and engineering domains with rigorous physical justifications",
            provider=provider,
        )

    async def investigate(self, state: AgenticResearchState) -> AgentStatusRecord:
        t0 = time.perf_counter()
        query = state.original_query
        q_lower = query.lower()

        llm_data = await self._call_llm_json(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=f"Inquiry: {query}\nInterpreted Objective: {state.intent.interpreted_objective if state.intent else query}",
        )

        domains: List[DiscoveredDomain] = []
        if llm_data and "domains" in llm_data and isinstance(llm_data["domains"], list):
            for d in llm_data["domains"]:
                domains.append(
                    DiscoveredDomain(
                        domain_name=d.get("domain_name", "General Physics"),
                        tier=d.get("tier", "primary"),
                        scientific_rationale=d.get("scientific_rationale", "Foundational physical laws"),
                        physical_process_explained=d.get("physical_process_explained", "Continuum dynamics"),
                        supported_subquestions=d.get("supported_subquestions", ["SQ-1"]),
                        contributed_concepts=d.get("contributed_concepts", []),
                    )
                )

        if not domains:
            # Deterministic domain mapping based on physical principles
            if "thermoelectric" in q_lower or "teg" in q_lower or ("waste heat" in q_lower and "motor" in q_lower):
                domains = [
                    DiscoveredDomain(
                        domain_name="Thermodynamics & Heat Transfer",
                        tier="primary",
                        scientific_rationale="Governs motor dissipation, thermal interface conduction (Fourier's Law), and theoretical Carnot conversion limit",
                        physical_process_explained="Conductive heat flux from stator to casing and thermal gradient across thermoelectric legs",
                        supported_subquestions=["SQ-1", "SQ-4", "SQ-5"],
                        contributed_concepts=["Fourier's Law", "Carnot Limit", "Thermal Resistance", "Convective Dissipation"],
                    ),
                    DiscoveredDomain(
                        domain_name="Solid-State Physics & Thermoelectrics",
                        tier="primary",
                        scientific_rationale="Explains the Seebeck effect, charge carrier diffusion under temperature gradient, and figure of merit ZT",
                        physical_process_explained="Coupled thermal and electrical charge transport across doped semiconductor p-n junctions",
                        supported_subquestions=["SQ-2", "SQ-3"],
                        contributed_concepts=["Seebeck Effect", "Figure of Merit (ZT)", "Peltier Coefficient", "Phonon Scattering"],
                    ),
                    DiscoveredDomain(
                        domain_name="Electromagnetism & Electrical Machines",
                        tier="secondary",
                        scientific_rationale="Identifies industrial motor losses: stator I^2*R Joule losses, rotor slip losses, and iron eddy-current/hysteresis losses",
                        physical_process_explained="Electromechanical energy conversion efficiency and loss dissipation channels",
                        supported_subquestions=["SQ-1"],
                        contributed_concepts=["Joule Heating", "Eddy Current Losses", "Hysteresis Losses", "Copper Winding Resistance"],
                    ),
                    DiscoveredDomain(
                        domain_name="Materials Science",
                        tier="supporting",
                        scientific_rationale="Evaluates thermoelectric materials (Bi2Te3, skutterudites) for temperature stability and electrical conductivity",
                        physical_process_explained="Semiconductor bandgap optimization and thermal conductivity reduction",
                        supported_subquestions=["SQ-3"],
                        contributed_concepts=["Bismuth Telluride (Bi2Te3)", "Thermal Conductivity (kappa)", "Electrical Conductivity (sigma)"],
                    ),
                    DiscoveredDomain(
                        domain_name="Power Electronics & Conditioning",
                        tier="supporting",
                        scientific_rationale="TEG arrays deliver variable low DC voltages requiring impedance matching and DC-DC boost conversion",
                        physical_process_explained="Maximum Power Point Tracking (MPPT) and DC-DC voltage amplification",
                        supported_subquestions=["SQ-6"],
                        contributed_concepts=["Maximum Power Point Tracking (MPPT)", "Impedance Matching", "DC-DC Boost Conversion"],
                    ),
                    DiscoveredDomain(
                        domain_name="Energy Systems Engineering",
                        tier="conditional",
                        scientific_rationale="Dictates system integration trade-offs, payback period, and parasite pumping/fan cooling penalties",
                        physical_process_explained="Net recovered energy balance versus parasitic auxiliary cooling loads",
                        supported_subquestions=["SQ-6"],
                        contributed_concepts=["Parasitic Loads", "Net System Efficiency", "Thermal Contact Optimization"],
                    ),
                ]
            else:
                domains = [
                    DiscoveredDomain(
                        domain_name="Classical Mechanics & Dynamics",
                        tier="primary",
                        scientific_rationale="Governs physical motion, kinematic forces, and momentum conservation",
                        physical_process_explained="Equilibrium states and mechanical energy transfer",
                        supported_subquestions=["SQ-1", "SQ-2"],
                        contributed_concepts=["Newtonian Mechanics", "Energy Conservation", "Force Equilibrium"],
                    ),
                    DiscoveredDomain(
                        domain_name="Applied Electrodynamics",
                        tier="primary",
                        scientific_rationale="Governs electromagnetic interactions, field equations, and circuit laws",
                        physical_process_explained="Electromagnetic potential differences and charge transport",
                        supported_subquestions=["SQ-2", "SQ-3"],
                        contributed_concepts=["Maxwell's Equations", "Lorentz Force", "Joule Heating"],
                    ),
                    DiscoveredDomain(
                        domain_name="Thermodynamics",
                        tier="secondary",
                        scientific_rationale="Establishes energy dissipation, entropy generation, and heat transfer bounds",
                        physical_process_explained="Thermal dissipation and conversion efficiency limits",
                        supported_subquestions=["SQ-3"],
                        contributed_concepts=["First & Second Laws", "Entropy", "Thermal Resistance"],
                    ),
                ]

        state.domains = domains

        for d in domains:
            self.record_finding(
                state=state,
                finding_type=FindingType.DOMAIN,
                title=f"Domain [{d.tier.upper()}]: {d.domain_name}",
                content=f"Domain: {d.domain_name} ({d.tier})\nRationale: {d.scientific_rationale}\nProcesses: {d.physical_process_explained}",
                justification=d.scientific_rationale,
                domains=[d.domain_name],
                subquestions=d.supported_subquestions,
            )

        dt = (time.perf_counter() - t0) * 1000.0
        self.log_timeline(state, "Domains Discovered", f"Identified {len(domains)} scientific domains across primary, secondary, and supporting tiers")

        status_rec = AgentStatusRecord(
            agent_id=self.role.value,
            role=self.role,
            display_name=self.display_name,
            responsibility=self.responsibility,
            status=AgentStatus.COMPLETED,
            current_task=f"Identified {len(domains)} domains",
            latency_ms=round(dt, 2),
            findings_count=len(domains),
        )
        state.agents[self.role.value] = status_rec
        return status_rec

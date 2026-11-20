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
    HierarchicalSubQuestion,
)

SYSTEM_PROMPT = """You are AXION's Research Question Decomposition Agent.
Decompose the scientific inquiry into a complete, structured hierarchy of subquestions:
- SQ-1: Constitutive mechanisms & input loss channels
- SQ-2: Conversion physics & governing equations
- SQ-3: Dimensionless figure of merit / efficiency factors
- SQ-4: Thermal/physical coupling & interface boundary conditions
- SQ-5: Dissipation, cooling & environmental heat sinking
- SQ-6: System electrical conditioning & integration trade-offs

For each subquestion specify:
- id: e.g. "SQ-1"
- level: "main | major_area | subquestion | investigative"
- question: full question text
- purpose: scientific goal
- relevant_domains: list of domain names
- required_concepts: list of concepts
- required_variables: list of variables
- expected_evidence: expected experimental or theoretical evidence
- depends_on: list of prerequisite subquestion IDs (e.g. ["SQ-1"])
- priority: "HIGH | MEDIUM | LOW"
- completion_criteria: criteria to consider this subquestion answerable

Return valid JSON:
{
  "subquestions": [
    {
      "id": "SQ-1",
      "level": "subquestion",
      "question": "string",
      "purpose": "string",
      "relevant_domains": ["string"],
      "required_concepts": ["string"],
      "required_variables": ["string"],
      "expected_evidence": "string",
      "depends_on": [],
      "priority": "HIGH",
      "completion_criteria": "string"
    }
  ]
}"""


class QuestionDecompositionAgent(BaseResearchAgent):
    """Agent 4: Decomposes inquiry into a rigorous hierarchy of dependent scientific research subquestions."""

    def __init__(self, provider: Optional[LLMProvider] = None):
        super().__init__(
            role=AgentRole.QUESTION_DECOMPOSITION,
            display_name="Question Decomposition Agent",
            responsibility="Decomposes inquiry into structured, ordered subquestions with explicit dependency tracking",
            provider=provider,
        )

    async def investigate(self, state: AgenticResearchState) -> AgentStatusRecord:
        t0 = time.perf_counter()
        query = state.original_query
        q_lower = query.lower()

        llm_data = await self._call_llm_json(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=f"Original Query: {query}\nObjective: {state.intent.interpreted_objective if state.intent else ''}",
        )

        subquestions: List[HierarchicalSubQuestion] = []
        if llm_data and "subquestions" in llm_data and isinstance(llm_data["subquestions"], list):
            for sq in llm_data["subquestions"]:
                subquestions.append(
                    HierarchicalSubQuestion(
                        id=sq.get("id", f"SQ-{len(subquestions) + 1}"),
                        level=sq.get("level", "subquestion"),
                        question=sq.get("question", ""),
                        purpose=sq.get("purpose", ""),
                        relevant_domains=sq.get("relevant_domains", []),
                        required_concepts=sq.get("required_concepts", []),
                        required_variables=sq.get("required_variables", []),
                        expected_evidence=sq.get("expected_evidence", ""),
                        depends_on=sq.get("depends_on", []),
                        priority=sq.get("priority", "HIGH"),
                        completion_criteria=sq.get("completion_criteria", ""),
                        status="pending",
                    )
                )

        if not subquestions:
            # Deterministic domain-specific subquestion hierarchy
            if "thermoelectric" in q_lower or "teg" in q_lower or ("waste heat" in q_lower and "motor" in q_lower):
                subquestions = [
                    HierarchicalSubQuestion(
                        id="SQ-1",
                        level="major_area",
                        question="What mechanisms produce waste heat losses in an industrial electric motor, and how much heat flux is accessible at the motor casing?",
                        purpose="Quantify available thermal energy input and distinguish stator Joule losses from bearing/friction losses",
                        relevant_domains=["Electromagnetism & Electrical Machines", "Thermodynamics & Heat Transfer"],
                        required_concepts=["Joule Heating", "Eddy Current Loss", "Casing Thermal Resistance"],
                        required_variables=["P_input", "P_output", "P_loss", "T_surface"],
                        expected_evidence="Motor efficiency curves (IE2-IE4 standards), stator loss breakdowns, and thermal imaging data",
                        depends_on=[],
                        priority="HIGH",
                        completion_criteria="Quantitative formulation of casing heat flux as a function of motor load and efficiency rating",
                    ),
                    HierarchicalSubQuestion(
                        id="SQ-2",
                        level="subquestion",
                        question="How does a thermoelectric generator convert a temperature difference into open-circuit voltage and electric power via the Seebeck effect?",
                        purpose="Formulate governing electro-thermal transport relations across p-n thermocouple legs",
                        relevant_domains=["Solid-State Physics & Thermoelectrics"],
                        required_concepts=["Seebeck Effect", "Seebeck Coefficient (S)", "Internal Electrical Resistance"],
                        required_variables=["S", "Delta_T", "V_oc", "R_int", "P_elec"],
                        expected_evidence="Constitutive Seebeck voltage equation and coupled Peltier heat equations",
                        depends_on=["SQ-1"],
                        priority="HIGH",
                        completion_criteria="Closed-form relationship expressing generated voltage and electrical power as functions of Delta_T",
                    ),
                    HierarchicalSubQuestion(
                        id="SQ-3",
                        level="subquestion",
                        question="What physical factors and material properties determine the thermoelectric figure of merit (ZT) and maximum conversion efficiency?",
                        purpose="Establish thermodynamic bounds on energy conversion and analyze tradeoffs between electrical and thermal conductivity",
                        relevant_domains=["Solid-State Physics & Thermoelectrics", "Materials Science"],
                        required_concepts=["Figure of Merit (ZT)", "Carnot Limit", "Thermal Conductivity (kappa)", "Electrical Conductivity (sigma)"],
                        required_variables=["ZT", "S", "sigma", "kappa", "T_m", "eta_max"],
                        expected_evidence="Empirical ZT curves for Bi2Te3 alloys and Carnot-normalized maximum efficiency equation",
                        depends_on=["SQ-2"],
                        priority="HIGH",
                        completion_criteria="Mathematical derivation of maximum efficiency eta_max as a function of ZT and Carnot efficiency",
                    ),
                    HierarchicalSubQuestion(
                        id="SQ-4",
                        level="subquestion",
                        question="How does thermal contact resistance and interface heat exchanger coupling between the motor casing and TEG hot side affect the temperature drop?",
                        purpose="Evaluate practical heat conduction losses across thermal interface materials (TIM)",
                        relevant_domains=["Thermodynamics & Heat Transfer", "Mechanical Engineering"],
                        required_concepts=["Thermal Interface Material (TIM)", "Thermal Contact Resistance", "Heat Exchanger Conductance"],
                        required_variables=["R_contact", "T_hot_junction", "k_TIM", "A_contact"],
                        expected_evidence="Thermal contact resistance datasets and conductive heat transfer formulations",
                        depends_on=["SQ-1", "SQ-2"],
                        priority="HIGH",
                        completion_criteria="Thermal resistance network model showing effective Delta_T across active thermoelectric legs",
                    ),
                    HierarchicalSubQuestion(
                        id="SQ-5",
                        level="subquestion",
                        question="What cold-side heat rejection mechanism (natural convection, finned heat sinks, or liquid cooling) maintains the required temperature gradient?",
                        purpose="Balance cold-side thermal dissipation against parasitic fan/pump power consumption",
                        relevant_domains=["Thermodynamics & Heat Transfer", "Energy Systems Engineering"],
                        required_concepts=["Convective Heat Transfer", "Heat Sink Fin Efficiency", "Parasitic Energy Cost"],
                        required_variables=["h_conv", "T_cold", "T_ambient", "P_parasitic"],
                        expected_evidence="Nusselt number correlations for finned convective heat sinks and ambient dissipation data",
                        depends_on=["SQ-3", "SQ-4"],
                        priority="MEDIUM",
                        completion_criteria="Heat sink thermal resistance requirement to maintain cold junction within 10 K of ambient",
                    ),
                    HierarchicalSubQuestion(
                        id="SQ-6",
                        level="investigative",
                        question="How can the low, load-dependent DC output voltage of the TEG be conditioned using MPPT boost converters to supply a useful electrical load?",
                        purpose="Design power electronic interface to extract maximum power under fluctuating thermal operating conditions",
                        relevant_domains=["Power Electronics & Conditioning"],
                        required_concepts=["Maximum Power Point Tracking (MPPT)", "DC-DC Boost Converter", "Impedance Matching"],
                        required_variables=["V_in", "V_out", "eta_converter", "R_load"],
                        expected_evidence="DC-DC boost converter topologies for low-voltage energy harvesting and impedance matching rules",
                        depends_on=["SQ-2", "SQ-3"],
                        priority="MEDIUM",
                        completion_criteria="Electrical circuit schematic and converter efficiency model operating from V_in >= 0.3 V",
                    ),
                ]
            else:
                subquestions = [
                    HierarchicalSubQuestion(
                        id="SQ-1",
                        level="major_area",
                        question=f"What are the primary governing physical mechanisms and constitutive relations underlying {query[:50]}?",
                        purpose="Identify foundational conservation laws and state equations",
                        relevant_domains=["Physics", "Applied Science"],
                        required_concepts=["Constitutive Law", "Conservation Principle"],
                        required_variables=["target_var", "state_param"],
                        expected_evidence="Peer-reviewed governing equations and experimental validation data",
                        depends_on=[],
                        priority="HIGH",
                        completion_criteria="Analytical formulation of governing relationship",
                    ),
                    HierarchicalSubQuestion(
                        id="SQ-2",
                        level="subquestion",
                        question="What explicit parameters, material properties, and operational boundary conditions govern the system?",
                        purpose="Define operating regime and numerical parameter ranges",
                        relevant_domains=["Engineering", "Material Physics"],
                        required_concepts=["Boundary Conditions", "Parameter Scaling"],
                        required_variables=["input_val", "boundary_limit"],
                        expected_evidence="Empirical measurements and calibrated parameter values",
                        depends_on=["SQ-1"],
                        priority="HIGH",
                        completion_criteria="Tabulated parameter bounds and dimensionless numbers",
                    ),
                    HierarchicalSubQuestion(
                        id="SQ-3",
                        level="investigative",
                        question="What efficiency limits, practical constraints, or cross-domain trade-offs dictate optimal performance?",
                        purpose="Evaluate limiting behavior and synthesis",
                        relevant_domains=["System Engineering"],
                        required_concepts=["Efficiency Limit", "Trade-Off Balance"],
                        required_variables=["eta", "loss"],
                        expected_evidence="Thermodynamic or empirical limits",
                        depends_on=["SQ-1", "SQ-2"],
                        priority="MEDIUM",
                        completion_criteria="Quantified performance envelope and operational limits",
                    ),
                ]

        state.subquestions = subquestions

        for sq in subquestions:
            self.record_finding(
                state=state,
                finding_type=FindingType.SUBQUESTION,
                title=f"{sq.id}: {sq.question[:50]}...",
                content=f"Subquestion [{sq.id}] ({sq.priority}): {sq.question}\nPurpose: {sq.purpose}\nExpected Evidence: {sq.expected_evidence}",
                justification=sq.purpose,
                subquestions=[sq.id],
                domains=sq.relevant_domains,
            )

        dt = (time.perf_counter() - t0) * 1000.0
        self.log_timeline(state, "Questions Decomposed", f"Generated hierarchy of {len(subquestions)} research subquestions with dependency links")

        status_rec = AgentStatusRecord(
            agent_id=self.role.value,
            role=self.role,
            display_name=self.display_name,
            responsibility=self.responsibility,
            status=AgentStatus.COMPLETED,
            current_task=f"Generated {len(subquestions)} subquestions",
            latency_ms=round(dt, 2),
            findings_count=len(subquestions),
        )
        state.agents[self.role.value] = status_rec
        return status_rec

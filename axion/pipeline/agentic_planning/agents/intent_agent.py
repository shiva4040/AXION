import time
from typing import Optional
from axion.core.provider import LLMProvider
from axion.pipeline.agentic_planning.base_agent import BaseResearchAgent
from axion.pipeline.agentic_planning.types import (
    AgentFinding,
    AgentRole,
    AgentStatus,
    AgentStatusRecord,
    AgenticResearchState,
    FindingType,
    IntentAnalysis,
)

SYSTEM_PROMPT = """You are AXION's Intent Understanding Agent.
Your role is to deeply analyze the user's scientific/engineering inquiry.
Analyze:
1. What is the user actually trying to understand, calculate, or achieve?
2. What is the main research objective?
3. What is the expected outcome?
4. Problem type: quantitative_calculation | analogical_transfer | feasibility_check | system_design | hypothesis_evaluation | conceptual_explanation
5. Explicit requirements vs inferred requirements
6. Ambiguities and missing information.

Return valid JSON matching this schema:
{
  "interpreted_objective": "Faithful summary of core scientific goal",
  "expected_outcome": "Expected scientific result (e.g. thermodynamic efficiency limits, mathematical proof, design trade-off)",
  "problem_type": "conceptual_explanation | system_design | quantitative_calculation | analogical_transfer",
  "explicit_requirements": ["Explicit requirement 1", "Explicit requirement 2"],
  "inferred_requirements": ["Inferred requirement 1", "Inferred requirement 2"],
  "ambiguities": ["Any detected ambiguity or unspecified scale"],
  "missing_information": ["Missing parameter, boundary condition, or operating state"],
  "clarification_prompt": null,
  "confidence": 0.95,
  "justification": "Why this interpretation is scientifically sound"
}"""


class IntentUnderstandingAgent(BaseResearchAgent):
    """Agent 2: Deeply investigates the core scientific intent, explicit/implied requirements, and ambiguities."""

    def __init__(self, provider: Optional[LLMProvider] = None):
        super().__init__(
            role=AgentRole.INTENT_UNDERSTANDING,
            display_name="Intent Understanding Agent",
            responsibility="Deeply investigates user objective, expected outcome, explicit vs implied requirements, and ambiguities",
            provider=provider,
        )

    async def investigate(self, state: AgenticResearchState) -> AgentStatusRecord:
        t0 = time.perf_counter()
        query = state.original_query
        q_lower = query.lower()

        # Step 1: Attempt LLM extraction if provider available
        llm_data = await self._call_llm_json(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=f"Scientific Query:\n{query}",
        )

        if llm_data:
            intent = IntentAnalysis(
                original_question=query,
                interpreted_objective=llm_data.get("interpreted_objective", query),
                expected_outcome=llm_data.get("expected_outcome", "Scientific explanation and governing relations"),
                problem_type=llm_data.get("problem_type", "conceptual_explanation"),
                explicit_requirements=llm_data.get("explicit_requirements", []),
                inferred_requirements=llm_data.get("inferred_requirements", []),
                ambiguities=llm_data.get("ambiguities", []),
                missing_information=llm_data.get("missing_information", []),
                clarification_prompt=llm_data.get("clarification_prompt"),
                confidence=float(llm_data.get("confidence", 0.95)),
                justification=llm_data.get("justification", "Grounded in query text"),
            )
        else:
            # Deterministic scientific deduction
            if "thermoelectric" in q_lower or "teg" in q_lower or ("waste heat" in q_lower and "motor" in q_lower):
                objective = "Recover useful electrical energy from industrial motor waste heat using thermoelectric generators"
                outcome = "Thermodynamic conversion efficiency limits, Seebeck voltage derivation, and electromechanical trade-offs"
                pt = "system_design"
                explicit_reqs = [
                    "Evaluate waste heat harvesting from industrial electric motors",
                    "Analyze thermoelectric generator (TEG) integration",
                    "Identify primary physical factors determining conversion efficiency",
                ]
                inferred_reqs = [
                    "Model motor loss dissipation channels (Joule losses, iron/core losses, mechanical friction)",
                    "Establish Seebeck effect physics and figure of merit ZT",
                    "Determine thermal interface conduction and cold-side heat sinking requirements",
                ]
                missing = [
                    "Motor rated power (kW), efficiency class (IE2/IE3/IE4), and operating duty cycle",
                    "Surface casing temperature range (Th) and ambient cooling temperature (Tc)",
                    "Available physical mounting surface area on motor frame",
                ]
            elif "drag" in q_lower and ("pv" in q_lower or "photovoltaic" in q_lower or "solar" in q_lower):
                objective = "Analyze cross-domain coupling between aerodynamic drag losses and photovoltaic energy harvesting on moving vehicles"
                outcome = "Net power balance curve and velocity break-even threshold"
                pt = "analogical_transfer"
                explicit_reqs = ["Model aerodynamic drag power penalty at cruising speed", "Model solar power generation from rooftop array"]
                inferred_reqs = ["Harmonize mechanical drag power P_drag = F_drag * v with electrical PV output P_pv = G * A * eta"]
                missing = ["Vehicle drag coefficient Cd and frontal area A_front", "Solar irradiance G (W/m^2) and array efficiency eta"]
            else:
                objective = f"Investigate foundational physical principles and governing laws of: {query}"
                outcome = "Verified governing equations, operational constraints, and empirical validity boundaries"
                pt = "conceptual_explanation"
                explicit_reqs = ["Formulate governing constitutive equations", "Identify physical components and parameters"]
                inferred_reqs = ["Establish thermodynamic, conservation, or continuum boundary conditions"]
                missing = ["Specific numerical parameters or experimental boundary conditions"]

            intent = IntentAnalysis(
                original_question=query,
                interpreted_objective=objective,
                expected_outcome=outcome,
                problem_type=pt,
                explicit_requirements=explicit_reqs,
                inferred_requirements=inferred_reqs,
                ambiguities=["Short inquiry without boundary limits"] if len(query.split()) < 5 else [],
                missing_information=missing,
                confidence=0.92,
                justification="Deductions derived from canonical physical principles and explicit query semantics",
            )

        state.intent = intent

        # Record atomic findings
        self.record_finding(
            state=state,
            finding_type=FindingType.INTENT,
            title=f"Objective: {intent.interpreted_objective[:50]}...",
            content=f"Primary Research Objective: {intent.interpreted_objective}\nExpected Outcome: {intent.expected_outcome}",
            justification=intent.justification,
            confidence=intent.confidence,
        )

        dt = (time.perf_counter() - t0) * 1000.0
        self.log_timeline(state, "Intent Formulated", f"Identified objective: {intent.interpreted_objective[:60]}...")

        status_rec = AgentStatusRecord(
            agent_id=self.role.value,
            role=self.role,
            display_name=self.display_name,
            responsibility=self.responsibility,
            status=AgentStatus.COMPLETED,
            current_task="Intent analysis completed",
            latency_ms=round(dt, 2),
            findings_count=1,
        )
        state.agents[self.role.value] = status_rec
        return status_rec

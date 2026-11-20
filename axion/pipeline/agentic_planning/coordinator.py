"""Agent 1: Research Coordinator Agent.

Orchestrates multi-agent research planning, manages round-based investigations,
resolves critical issues, and synthesizes the final research specification.
"""

from typing import Any, Dict, List, Optional
import logging
from axion.pipeline.agentic_planning.base_agent import BaseResearchAgent
from axion.pipeline.agentic_planning.types import (
    AgentRole,
    AgenticResearchState,
    AgentStatusRecord,
    AgentStatus,
    FindingType,
)

logger = logging.getLogger(__name__)


class ResearchCoordinatorAgent(BaseResearchAgent):
    """Central scientific orchestrator coordinating all 13 specialized research agents."""

    def __init__(self, llm_provider: Any = None):
        super().__init__(
            role=AgentRole.COORDINATOR,
            name="Research Coordinator Agent",
            llm_provider=llm_provider,
        )

    def initialize_state(self, question: str) -> AgenticResearchState:
        """Initializes a new shared state and registers all 13 agents."""
        state = AgenticResearchState(original_question=question)

        # Register roster of all 13 agents
        for role in AgentRole:
            state.agent_statuses[role.value] = AgentStatusRecord(
                role=role,
                name=self._get_agent_display_name(role),
                status=AgentStatus.IDLE,
            )

        self.log_timeline(
            state,
            event_type="ORCHESTRATION_INITIALIZED",
            description=f"Initialized 13-agent scientific planning system for query: '{question}'",
            round_number=1,
        )
        return state

    def _get_agent_display_name(self, role: AgentRole) -> str:
        names = {
            AgentRole.COORDINATOR: "Research Coordinator Agent",
            AgentRole.INTENT_UNDERSTANDING: "Intent Understanding Agent",
            AgentRole.DOMAIN_DISCOVERY: "Scientific Domain Discovery Agent",
            AgentRole.QUESTION_DECOMPOSITION: "Research Question Decomposition Agent",
            AgentRole.CONCEPTS_DISCOVERY: "Scientific Concepts Discovery Agent",
            AgentRole.VARIABLES_EQUATIONS: "Variables, Parameters & Equations Agent",
            AgentRole.PROCESS_MAPPING: "Physical Process and System Mapping Agent",
            AgentRole.MATERIALS_TECHNOLOGY: "Materials, Components and Technology Agent",
            AgentRole.EVIDENCE_REQUIREMENTS: "Evidence Requirements Agent",
            AgentRole.CROSS_DOMAIN: "Cross-Domain Connection Agent",
            AgentRole.KNOWLEDGE_GAP: "Knowledge Gap and Constraint Agent",
            AgentRole.CRITICAL_REVIEWER: "Critical Reviewer Agent",
            AgentRole.COMPLETENESS_EVALUATOR: "Completeness Evaluator Agent",
        }
        return names.get(role, role.value)

    def execute(self, state: AgenticResearchState, context: Dict[str, Any] = None) -> AgenticResearchState:
        """Coordinator synthesis finding."""
        self.set_active(state)

        total_findings = len(state.findings)
        domains_count = len(state.discovered_domains)
        subq_count = len(state.subquestions)
        eq_count = len(state.governing_equations)
        req_count = len(state.evidence_requirements)

        summary = (
            f"Orchestration completed across {state.current_round} investigation rounds. "
            f"13 specialized agents contributed {total_findings} verified findings across {domains_count} scientific domains, "
            f"{subq_count} decomposed subquestions, {eq_count} governing equations, and {req_count} Stage 02 evidence directives. "
            f"Final readiness verdict: {state.readiness_decision}."
        )

        self.record_finding(
            state=state,
            finding_type=FindingType.SYNTHESIS,
            title="Coordinated Scientific Research Plan Synthesized",
            content=summary,
            scientific_basis="Multi-agent distributed problem solving, epistemological synthesis, and bounded scientific deliberation.",
            confidence=0.98,
            tags=["coordination", "synthesis", "master_plan", "stage01_complete"],
        )

        self.set_completed(state, findings_count=1)
        return state

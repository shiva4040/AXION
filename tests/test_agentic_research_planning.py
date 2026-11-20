"""Comprehensive verification test suite for the AXION Agentic Scientific Research Planning System.

Tests all 13 specialized agent roles, bounded multi-round execution, structured findings,
adversarial critical reviews, completeness evaluations, and Stage 01/Stage 02 integration.
"""

import pytest
from axion.pipeline.agentic_planning.types import (
    AgentRole,
    AgentStatus,
    FindingType,
    AgenticResearchState,
)
from axion.pipeline.agentic_planning.coordinator import ResearchCoordinatorAgent
from axion.pipeline.agentic_planning.agents.intent_agent import IntentUnderstandingAgent
from axion.pipeline.agentic_planning.agents.domain_agent import DomainDiscoveryAgent
from axion.pipeline.agentic_planning.agents.decomposition_agent import QuestionDecompositionAgent
from axion.pipeline.agentic_planning.agents.concepts_agent import ConceptsDiscoveryAgent
from axion.pipeline.agentic_planning.agents.variables_equations_agent import VariablesAndEquationsAgent
from axion.pipeline.agentic_planning.agents.process_mapping_agent import PhysicalProcessMappingAgent
from axion.pipeline.agentic_planning.agents.materials_technology_agent import MaterialsAndComponentsAgent
from axion.pipeline.agentic_planning.agents.evidence_requirements_agent import EvidenceRequirementsAgent
from axion.pipeline.agentic_planning.agents.cross_domain_agent import CrossDomainConnectionAgent
from axion.pipeline.agentic_planning.agents.knowledge_gap_agent import KnowledgeGapAgent
from axion.pipeline.agentic_planning.agents.critical_reviewer_agent import CriticalReviewerAgent
from axion.pipeline.agentic_planning.agents.completeness_evaluator_agent import CompletenessEvaluatorAgent
from axion.pipeline.agentic_planning.engine import AgenticPlanningEngine
from axion.pipeline.stage01_question import ScientificQuestionProcessor
from axion.core.provider import MockProvider

MOTOR_TEG_QUERY = (
    "How can thermoelectric generators recover waste heat from industrial motors?"
)


def test_all_13_agents_instantiation_and_roles():
    """Verify all 13 specialized agent roles are instantiated and assigned distinct roles."""
    engine = AgenticPlanningEngine()

    agents = [
        engine.coordinator,
        engine.intent_agent,
        engine.domain_agent,
        engine.decomposition_agent,
        engine.concepts_agent,
        engine.variables_agent,
        engine.process_agent,
        engine.materials_agent,
        engine.evidence_agent,
        engine.cross_domain_agent,
        engine.gap_agent,
        engine.reviewer_agent,
        engine.evaluator_agent,
    ]

    assert len(agents) == 13
    roles = [a.role for a in agents]
    assert len(set(roles)) == 13, "All 13 agents must have unique roles"
    for a in agents:
        assert a.name is not None and len(a.name) > 0


def test_shared_agentic_state_initialization():
    """Verify state initialization registers all 13 agents with IDLE status."""
    coord = ResearchCoordinatorAgent()
    state = coord.initialize_state(MOTOR_TEG_QUERY)

    assert state.original_question == MOTOR_TEG_QUERY
    assert len(state.agent_statuses) == 13
    for role_key, status_rec in state.agent_statuses.items():
        assert status_rec.status == AgentStatus.IDLE
        assert status_rec.name is not None
    assert len(state.timeline) >= 1
    assert state.timeline[0].event_type == "ORCHESTRATION_INITIALIZED"


def test_variables_and_equations_agent_discovery():
    """Verify Agent 6 discovers governing equations (P_loss, Seebeck, ZT, eta_max) with symbols and units."""
    agent = VariablesAndEquationsAgent()
    state = AgenticResearchState(original_question=MOTOR_TEG_QUERY)
    state = agent.execute(state)

    assert len(state.governing_equations) >= 3
    eq_names = [eq.name for eq in state.governing_equations]
    assert any("Waste Heat" in name or "Loss" in name for name in eq_names)
    assert any("Seebeck" in name for name in eq_names)
    assert any("Figure of Merit" in name or "ZT" in name for name in eq_names)

    # Check symbol definitions and validity limits
    for eq in state.governing_equations:
        assert len(eq.latex) > 0
        assert len(eq.symbols) > 0
        assert eq.validity_boundaries is not None


def test_physical_process_mapping_agent():
    """Verify Agent 7 constructs sequential causal energy flow chain."""
    agent = PhysicalProcessMappingAgent()
    state = AgenticResearchState(original_question=MOTOR_TEG_QUERY)
    state = agent.execute(state)

    assert len(state.physical_process_chain) >= 4
    steps = state.physical_process_chain
    assert steps[0].step_number == 1
    assert any("Heat Generation" in s.name or "Losses" in s.name for s in steps)
    assert any("Conduction" in s.name or "TIM" in s.name for s in steps)
    assert any("Seebeck" in s.name or "Diffusion" in s.name for s in steps)
    assert any("Power Conditioning" in s.name or "MPPT" in s.name for s in steps)


def test_materials_and_components_agent():
    """Verify Agent 8 identifies active thermoelectric materials, TIM, and power conditioning."""
    agent = MaterialsAndComponentsAgent()
    state = AgenticResearchState(original_question=MOTOR_TEG_QUERY)
    state = agent.execute(state)

    assert len(state.materials_and_components) >= 3
    names = [m.name for m in state.materials_and_components]
    assert any("Bi2Te3" in n or "Bismuth Telluride" in n for n in names)
    assert any("Graphite" in n or "TIM" in n for n in names)
    assert any("MPPT" in n or "Harvester" in n for n in names)


def test_evidence_requirements_agent():
    """Verify Agent 9 formulates concrete academic search queries and empirical data targets."""
    agent = EvidenceRequirementsAgent()
    state = AgenticResearchState(original_question=MOTOR_TEG_QUERY)
    state = agent.execute(state)

    assert len(state.evidence_requirements) >= 3
    for req in state.evidence_requirements:
        assert len(req.target_sources) > 0
        assert len(req.recommended_queries) > 0
        assert len(req.required_data_points) > 0
        assert req.verification_criteria is not None


def test_cross_domain_connection_agent():
    """Verify Agent 10 discovers interdisciplinary bridges and mathematical correspondences."""
    agent = CrossDomainConnectionAgent()
    state = AgenticResearchState(original_question=MOTOR_TEG_QUERY)
    state = agent.execute(state)

    assert len(state.cross_domain_bridges) >= 2
    for b in state.cross_domain_bridges:
        assert b.source_domain != b.target_domain
        assert len(b.analogical_mapping) > 0
        assert len(b.mathematical_correspondence) > 0


def test_knowledge_gap_and_constraint_agent():
    """Verify Agent 11 detects missing parameters and assigns severity ratings."""
    agent = KnowledgeGapAgent()
    state = AgenticResearchState(original_question=MOTOR_TEG_QUERY)
    state = agent.execute(state)

    assert len(state.knowledge_gaps) >= 2
    severities = [g.severity for g in state.knowledge_gaps]
    assert "CRITICAL" in severities or "HIGH" in severities
    for g in state.knowledge_gaps:
        assert len(g.resolution_approach) > 0


def test_critical_reviewer_agent():
    """Verify Agent 12 conducts adversarial audits and issues equation corrections."""
    agent = CriticalReviewerAgent()
    state = AgenticResearchState(original_question=MOTOR_TEG_QUERY)
    state = agent.execute(state)

    assert len(state.criticisms) >= 2
    assert len(state.review_events) >= 1
    # Verify criticism has rationale and proposed correction
    for crit in state.criticisms:
        assert len(crit.rationale) > 0
        assert len(crit.proposed_correction) > 0


def test_completeness_evaluator_agent():
    """Verify Agent 13 calculates multi-dimensional completeness scores and issues verdict."""
    evaluator = CompletenessEvaluatorAgent()
    state = AgenticResearchState(original_question=MOTOR_TEG_QUERY)

    # Populate some state data to test scoring
    from axion.pipeline.agentic_planning.types import DiscoveredDomain, HierarchicalSubQuestion, GoverningEquation
    state.discovered_domains = [DiscoveredDomain(domain_name="Thermodynamics", scientific_rationale="Heat dissipation", physical_process_explained="Conduction")]
    state.subquestions = [HierarchicalSubQuestion(id="SQ-1", question="What is the heat loss?", purpose="Model loss", completion_criteria="Calculate flux")]
    state.governing_equations = [GoverningEquation(name="Waste Heat", latex="P_{loss} = P_{in}(1-\\eta)", symbols={"P_loss": "W"})]

    state = evaluator.execute(state)
    assert state.completeness_evaluation is not None
    assert 0.0 <= state.completeness_evaluation.overall_score <= 1.0
    assert state.readiness_decision in ("READY", "CONDITIONAL", "NEEDS_REVISION")
    assert len(state.completeness_evaluation.readiness_rationale) > 0


def test_agentic_planning_engine_multi_round_execution():
    """Run full 3-round execution for industrial motor waste heat recovery and check all 13 agents."""
    engine = AgenticPlanningEngine(max_rounds=3)
    state = engine.plan_research(MOTOR_TEG_QUERY)

    # All 13 agents must have completed
    for role_key, status_rec in state.agent_statuses.items():
        assert status_rec.status == AgentStatus.COMPLETED, f"Agent {role_key} did not complete"
        assert status_rec.findings_count > 0

    assert len(state.findings) >= 13
    assert len(state.discovered_domains) >= 3
    assert len(state.subquestions) >= 3
    assert len(state.governing_equations) >= 3
    assert len(state.physical_process_chain) >= 4
    assert len(state.materials_and_components) >= 3
    assert len(state.evidence_requirements) >= 3
    assert len(state.cross_domain_bridges) >= 2
    assert len(state.knowledge_gaps) >= 2
    assert len(state.criticisms) >= 2
    assert state.completeness_evaluation is not None
    assert state.readiness_decision in ("READY", "CONDITIONAL")
    assert len(state.timeline) >= 10


@pytest.mark.asyncio
async def test_stage01_integration_and_questionspec_enrichment():
    """Verify ScientificQuestionProcessor populates QuestionSpec with agentic_research_state."""
    processor = ScientificQuestionProcessor(provider=MockProvider())
    q_spec = await processor.process_question(raw_query=MOTOR_TEG_QUERY)

    assert q_spec.agentic_research_state is not None
    ars = q_spec.agentic_research_state
    assert ars["original_question"] == MOTOR_TEG_QUERY
    assert len(ars["agent_statuses"]) == 13
    assert len(ars["findings"]) >= 13
    assert len(ars["governing_equations"]) >= 3
    assert len(ars["physical_process_chain"]) >= 4
    assert len(ars["materials_and_components"]) >= 3
    assert len(ars["evidence_requirements"]) >= 3
    assert ars["readiness_decision"] in ("READY", "CONDITIONAL")

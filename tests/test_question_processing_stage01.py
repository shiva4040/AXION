import pytest
from unittest.mock import AsyncMock

from axion.core.provider import GeminiProvider, MockProvider, LLMResponse
from axion.pipeline.stage01_question import ScientificQuestionProcessor
from axion.pipeline.types import QuestionIntent, QuestionSpec, StructuredQuestionAnalysis


@pytest.mark.asyncio
async def test_stage01_deterministic_simple_question():
    """Verify Stage 01 processes simple scientific inquiry in deterministic mode."""
    processor = ScientificQuestionProcessor()
    q = "What is the thermodynamic definition of entropy in an isolated system?"
    spec = await processor.process_question(q)

    assert spec.raw_query == q
    assert spec.intent in [QuestionIntent.EXPLANATION, QuestionIntent.FEASIBILITY_CHECK]
    assert "physics:thermodynamics" in spec.domain_tags
    assert any("entropy" in c.lower() for c in spec.extracted_concepts)
    assert spec.ambiguity_detected is False
    assert spec.clarification_needed is False


@pytest.mark.asyncio
async def test_stage01_deterministic_complex_multivariable():
    """Verify extraction of multiple variables, units, parameters, and constraints."""
    processor = ScientificQuestionProcessor()
    q = (
        "Calculate the electrical power dissipation when current I = 12.5 A and "
        "resistance R = 4.0 Ohm under steady-state conditions with voltage V <= 100 V"
    )
    spec = await processor.process_question(q)

    assert spec.intent == QuestionIntent.QUANTITATIVE_CALCULATION
    assert "physics:electromagnetism" in spec.domain_tags
    assert "I" in spec.declared_parameters
    assert "R" in spec.declared_parameters
    assert spec.declared_parameters["I"] == "12.5 A"
    assert spec.declared_parameters["R"] == "4.0 Ohm"
    assert "V" in spec.identified_constraints or "temporal" in spec.identified_constraints
    assert spec.identified_constraints.get("temporal") == "steady_state"


@pytest.mark.asyncio
async def test_stage01_deterministic_mathematical_physics_with_constraints():
    """Verify physical assumptions, boundary conditions, and flow regime constraints."""
    processor = ScientificQuestionProcessor()
    q = (
        "Under laminar, incompressible, and steady-state conditions, calculate the pressure drop "
        "Delta P in a circular pipe where diameter D = 0.05 m and flow velocity v = 1.2 m/s"
    )
    spec = await processor.process_question(q)

    assert spec.intent == QuestionIntent.QUANTITATIVE_CALCULATION
    assert "fluid_mechanics:pipe_flow" in spec.domain_tags
    assert spec.identified_constraints.get("flow_regime") == "laminar"
    assert spec.identified_constraints.get("compressibility") == "incompressible"
    assert spec.identified_constraints.get("temporal") == "steady_state"
    assert "D" in spec.declared_parameters
    assert "v" in spec.declared_parameters


@pytest.mark.asyncio
async def test_stage01_deterministic_cross_domain_transfer():
    """Verify cross-domain transfer intent and multi-domain detection."""
    processor = ScientificQuestionProcessor()
    q = "Is there an analog of electrical resistance in fluid pipe flow and thermal conduction?"
    spec = await processor.process_question(q)

    assert spec.intent == QuestionIntent.ANALOGICAL_TRANSFER
    assert "physics:electromagnetism" in spec.domain_tags
    assert "fluid_mechanics:pipe_flow" in spec.domain_tags or "physics:thermodynamics" in spec.domain_tags


@pytest.mark.asyncio
async def test_stage01_ambiguity_and_missing_information_detection():
    """Verify that underspecified or incomplete questions are flagged for clarification."""
    processor = ScientificQuestionProcessor()
    q = "What is the terminal velocity?"
    spec = await processor.process_question(q)

    # Incomplete: missing body mass, fluid viscosity, drag coefficient
    assert spec.ambiguity_detected is True
    assert spec.clarification_needed is True
    assert len(spec.missing_information) > 0
    assert spec.clarification_prompt is not None


@pytest.mark.asyncio
async def test_stage01_llm_structured_parsing_and_axion_validation_layer():
    """Verify AXION independent validation of LLM structured output schema."""
    mock_provider = AsyncMock()
    mock_provider.model = "gemini-3.1-flash-lite"
    mock_provider.generate_text.return_value = LLMResponse(
        text="""
        {
          "intended_meaning": "Determine convective heat transfer coefficient under laminar flow in a mini-channel",
          "scientific_subject": "Forced Convection Heat Transfer",
          "relevant_concepts": ["convective heat transfer", "Nusselt number", "laminar boundary layer"],
          "entities": ["cooling mini-channel", "dielectric fluid"],
          "target_variables": ["h_conv", "heat transfer coefficient"],
          "explicit_parameters": {"velocity": "2.5 m/s", "T_inlet": "298 K"},
          "explicit_constraints": {"flow_regime": "laminar", "state": "steady-state"},
          "inferred_constraints": {"fluid_model": "constant thermophysical properties"},
          "problem_type": "quantitative_calculation",
          "primary_domains": ["physics:thermodynamics", "fluid_mechanics:pipe_flow"],
          "ambiguity_detected": false,
          "ambiguity_notes": [],
          "missing_information": ["channel hydraulic diameter", "fluid thermal conductivity"],
          "clarification_needed": false,
          "clarification_prompt": null
        }
        """,
        model="gemini-3.1-flash-lite",
        prompt_tokens=180,
        completion_tokens=140,
        total_tokens=320,
    )

    processor = ScientificQuestionProcessor(provider=mock_provider)
    raw_query = "Calculate h_conv for dielectric fluid with velocity = 2.5 m/s at T_inlet = 298 K in steady-state laminar flow"
    spec = await processor.process_question(raw_query)

    assert spec.intended_meaning == "Determine convective heat transfer coefficient under laminar flow in a mini-channel"
    assert spec.scientific_subject == "Forced Convection Heat Transfer"
    assert "convective heat transfer" in spec.extracted_concepts
    assert "cooling mini-channel" in spec.entities
    assert "h_conv" in spec.target_variables
    assert "velocity" in spec.declared_parameters
    assert spec.declared_parameters["velocity"] == "2.5 m/s"
    assert spec.explicit_constraints.get("flow_regime") == "laminar"
    assert spec.inferred_constraints.get("fluid_model") == "constant thermophysical properties"
    assert "channel hydraulic diameter" in spec.missing_information
    assert spec.llm_provenance is not None
    assert spec.llm_provenance.model_name == "gemini-3.1-flash-lite"
    assert spec.llm_provenance.prompt_tokens == 180
    assert spec.llm_provenance.completion_tokens == 140
    assert spec.llm_provenance.validation_passed is True


@pytest.mark.asyncio
async def test_stage01_axion_rejects_hallucinated_explicit_parameters():
    """Verify AXION blocks the LLM from inventing parameters not in the prompt."""
    mock_provider = AsyncMock()
    mock_provider.model = "gemini-3.1-flash-lite"
    # LLM hallucinates pressure = 500 kPa and viscosity = 0.001 Pa*s when not in prompt
    mock_provider.generate_text.return_value = LLMResponse(
        text="""
        {
          "intended_meaning": "Find electrical resistance of wire",
          "scientific_subject": "Ohmic Resistance",
          "relevant_concepts": ["resistance", "resistivity"],
          "entities": ["copper wire"],
          "target_variables": ["R"],
          "explicit_parameters": {"length": "10 m", "pressure": "500 kPa"},
          "explicit_constraints": {},
          "inferred_constraints": {},
          "problem_type": "quantitative_calculation",
          "primary_domains": ["physics:electromagnetism"],
          "ambiguity_detected": false,
          "ambiguity_notes": [],
          "missing_information": [],
          "clarification_needed": false,
          "clarification_prompt": null
        }
        """,
        model="gemini-3.1-flash-lite",
    )

    processor = ScientificQuestionProcessor(provider=mock_provider)
    # Notice: '500 kPa' does not exist in raw_query
    raw_query = "Find electrical resistance of wire with length = 10 m"
    spec = await processor.process_question(raw_query)

    assert "length" in spec.declared_parameters
    # 'pressure' MUST NOT be in validated declared_parameters because it is hallucinated
    assert "pressure" not in spec.declared_parameters


@pytest.mark.asyncio
async def test_stage01_live_gemini_integration():
    """Live test using real configured Gemini API (gemini-3.1-flash-lite)."""
    import os
    from axion.config import settings

    if not settings.gemini_api_key:
        pytest.skip("GEMINI_API_KEY is not configured in local environment.")

    provider = GeminiProvider(strict=True, model="gemini-3.1-flash-lite")
    processor = ScientificQuestionProcessor(provider=provider)

    test_queries = [
        # 1. Multi-variable calculation with constraints
        (
            "Calculate the electrical power dissipated in a circuit when current I = 4.5 A "
            "flows through resistance R = 8.0 Ohm under continuous steady-state conditions"
        ),
        # 2. Interdisciplinary cross-domain transfer
        (
            "How does aerodynamic drag at vehicle cruising speed v = 120 km/h counteract "
            "the electrical power generation of a roof-mounted photovoltaic array?"
        ),
        # 3. Incomplete / Ambiguous question
        (
            "What is the efficiency?"
        ),
    ]

    for q in test_queries:
        try:
            spec = await processor.process_question(q)
        except RuntimeError as e:
            if "503" in str(e) or "500" in str(e) or "Service Unavailable" in str(e):
                pytest.skip(f"Gemini API transient service unavailable: {e}")
            raise
        assert isinstance(spec, QuestionSpec)
        assert spec.llm_provenance is not None
        assert spec.llm_provenance.model_name == "gemini-3.1-flash-lite"
        assert spec.llm_provenance.latency_ms > 0
        assert spec.llm_provenance.prompt_tokens > 0
        assert spec.llm_provenance.completion_tokens > 0
        assert spec.llm_provenance.validation_passed is True

        if "What is the efficiency?" in q:
            # Must detect ambiguity and identify missing context
            assert spec.ambiguity_detected is True
            assert len(spec.missing_information) > 0
            assert spec.clarification_needed is True
        elif "120 km/h" in q:
            # Must extract vehicle speed and identify cross-domain elements
            assert spec.intent == QuestionIntent.ANALOGICAL_TRANSFER or len(spec.domain_tags) >= 2
            assert any("aerodynamic" in c.lower() or "drag" in c.lower() for c in spec.extracted_concepts)
        elif "4.5 A" in q:
            # Must extract parameters
            assert "I" in spec.declared_parameters or any("4.5" in str(v) for v in spec.declared_parameters.values())

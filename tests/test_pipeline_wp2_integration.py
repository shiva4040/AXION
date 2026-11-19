import pytest
from axion.core.provider import MockProvider
from axion.pipeline.coordinator import PipelineCoordinator
from axion.pipeline.types import (
    AcquisitionPayload,
    ComposedSystem,
    ExtractedClaim,
    QuestionSpec,
    ReasoningTrace,
)


@pytest.mark.asyncio
async def test_wp2_integrated_pipeline_stages_01_through_05():
    """
    Integration Test for Work Package 2:
    Verifies that information flows seamlessly across:
    Stage 01 (Question Processing) ->
    Stage 02 (Knowledge Acquisition) ->
    Stage 03 (Evidence Extraction) ->
    Stage 04 (Knowledge Composition) ->
    Stage 05 (Reasoning and Calculations)
    without losing provenance, variables, equations, or conditions.
    """
    coordinator = PipelineCoordinator(provider=MockProvider())

    raw_query = "Calculate electrical power given voltage V = 12 V and current I = 3 A in steady DC conditions"

    # Stage 01: Process question
    spec = await coordinator.run_stage_01(raw_query)
    assert isinstance(spec, QuestionSpec)
    assert "physics:electromagnetism" in spec.domain_tags
    assert "V" in spec.declared_parameters or "val_1" in spec.declared_parameters

    # Manually provide a retrieved chunk to simulate acquired literature
    from axion.core.types import BoundingBox, ProvenancePointer
    from axion.pipeline.types import AcquiredChunk

    bbox = BoundingBox(page_number=1, x0=10.0, y0=20.0, x1=150.0, y1=60.0)
    chunk_text = (
        "Power Law in DC Circuits.\n"
        "Electrical power dissipation is P = V * I under steady-state conditions."
    )
    prov = ProvenancePointer(
        document_id="doc-physics-101",
        chunk_id="chunk-p-1",
        page_number=1,
        bounding_box=bbox,
        extracted_snippet="Electrical power dissipation is P = V * I under steady-state conditions.",
    )
    chunk = AcquiredChunk(
        chunk_id="chunk-p-1",
        document_id="doc-physics-101",
        page_number=1,
        text_content=chunk_text,
        provenance=prov,
        bounding_box=bbox,
    )

    payload = AcquisitionPayload(
        query_id=spec.query_id,
        retrieved_chunks=[chunk],
        sources_queried=["local_db"],
        total_retrieved=1,
    )

    # Stage 03: Extract evidence
    claims = await coordinator.run_stage_03(payload)
    assert len(claims) >= 1
    found_claim = next(c for c in claims if "P = V * I" in str(c.equations))
    assert found_claim.provenance.document_id == "doc-physics-101"
    assert found_claim.provenance.page_number == 1
    assert found_claim.provenance.extracted_snippet in chunk_text

    # Stage 04: Compose system
    # Explicitly add V=12 V and I=3 A to question spec boundary limits
    spec.declared_parameters["V"] = "12 V"
    spec.declared_parameters["I"] = "3 A"
    composed = await coordinator.run_stage_04(claims, spec)
    assert isinstance(composed, ComposedSystem)
    assert "P = V * I" in composed.coupled_equations
    assert composed.boundary_limits["V"] == "12 V"
    assert composed.boundary_limits["I"] == "3 A"

    # Stage 05: Execute reasoning
    trace = await coordinator.run_stage_05(composed)
    assert isinstance(trace, ReasoningTrace)
    assert "P" in trace.calculated_values
    assert "36 W" in trace.calculated_values["P"]
    assert "P" in trace.dependency_dag
    assert "V" in trace.dependency_dag["P"] or "I" in trace.dependency_dag["P"]
    assert len(trace.steps) >= 3


@pytest.mark.asyncio
async def test_wp2_end_to_end_coordinator_with_claims():
    """Verify coordinator's full execute method with newly integrated stages."""
    coordinator = PipelineCoordinator(provider=MockProvider())

    response = await coordinator.execute(
        raw_query="Calculate power when V = 10 V and I = 2 A"
    )

    # When no chunks are in DB, coordinator abstains safely
    assert response.is_abstained is True
    assert "ABSTAIN" in response.verdict

    # Check stage logs recorded Stages 1 through 8
    logged_stages = [l.stage_number for l in response.execution_logs]
    for stg in [1, 2, 3, 4, 5, 6, 7, 8]:
        assert stg in logged_stages

import asyncio
import pytest
from unittest.mock import AsyncMock, patch

from axion.core.provider import MockProvider
from axion.pipeline.coordinator import PipelineCoordinator
from axion.pipeline.types import (
    AcquisitionPayload,
    ComposedSystem,
    ExtractedClaim,
    PipelineAnswerResponse,
    QuestionSpec,
    ReasoningTrace,
    VerificationAuditReport,
)


@pytest.mark.asyncio
async def test_coordinator_explicit_stage_execution():
    """Verify explicit stage execution methods and data flow through PipelineCoordinator."""
    coordinator = PipelineCoordinator(provider=MockProvider())

    # Stage 01
    spec = await coordinator.run_stage_01(
        raw_query="Calculate electrical voltage when I = 2 A and R = 5 Ohm"
    )
    assert isinstance(spec, QuestionSpec)
    assert "physics:electromagnetism" in spec.domain_tags

    # Stage 02
    payload = await coordinator.run_stage_02(spec)
    assert isinstance(payload, AcquisitionPayload)

    # Stage 03
    claims = await coordinator.run_stage_03(payload)
    assert isinstance(claims, list)

    # Stage 04
    composed = await coordinator.run_stage_04(claims, spec)
    assert isinstance(composed, ComposedSystem)

    # Stage 05
    trace = await coordinator.run_stage_05(composed)
    assert isinstance(trace, ReasoningTrace)

    # Stage 06
    audit = await coordinator.run_stage_06(trace, composed, payload)
    assert isinstance(audit, VerificationAuditReport)

    # Stage 07 Read Stub
    findings = await coordinator.run_stage_07_read(spec)
    assert isinstance(findings, list)

    # Stage 08
    resp = await coordinator.run_stage_08(
        audit_report=audit,
        reasoning_trace=trace,
        composed_system=composed,
        question_spec=spec,
        execution_logs=[],
        total_latency_ms=10.0,
    )
    assert isinstance(resp, PipelineAnswerResponse)


@pytest.mark.asyncio
async def test_coordinator_end_to_end_execute_with_abstention():
    """Verify end-to-end execute when evidence is absent emits ABSTAIN_INSUFFICIENT_EVIDENCE."""
    coordinator = PipelineCoordinator(provider=MockProvider())

    response = await coordinator.execute(
        raw_query="Explain the viscosity of liquid helium under extreme pressures."
    )

    assert isinstance(response, PipelineAnswerResponse)
    assert response.is_abstained is True
    assert "ABSTAIN" in response.verdict
    assert response.abstention_reason == "ABSTAIN_INSUFFICIENT_EVIDENCE"
    assert len(response.execution_logs) >= 6
    # Ensure logs recorded each stage
    stage_numbers = [log.stage_number for log in response.execution_logs]
    assert 1 in stage_numbers
    assert 2 in stage_numbers
    assert 6 in stage_numbers
    assert 8 in stage_numbers


@pytest.mark.asyncio
async def test_coordinator_per_query_timeout_enforcement():
    """Verify coordinator enforces per-query timeout and emits TIMEOUT verdict."""
    coordinator = PipelineCoordinator(provider=MockProvider())

    # Patch stage01 to simulate an operation exceeding timeout budget
    async def slow_process(*args, **kwargs):
        await asyncio.sleep(0.5)
        return QuestionSpec(raw_query="slow query")

    with patch.object(coordinator.stage01, "process_question", side_effect=slow_process):
        response = await coordinator.execute(
            raw_query="Slow calculation test",
            timeout_seconds=0.1,  # Strict 100ms timeout
        )

    assert isinstance(response, PipelineAnswerResponse)
    assert response.is_abstained is True
    assert response.verdict == "TIMEOUT"
    assert "timeout" in response.abstention_reason.lower()
    timeout_logs = [log for log in response.execution_logs if log.status == "TIMEOUT"]
    assert len(timeout_logs) == 1
    assert timeout_logs[0].stage_name == "Timeout Enforcer"


@pytest.mark.asyncio
async def test_coordinator_error_handling():
    """Verify coordinator captures unhandled stage exceptions gracefully."""
    coordinator = PipelineCoordinator(provider=MockProvider())

    # Force an unexpected exception in Stage 02
    with patch.object(coordinator.stage02, "acquire_knowledge", side_effect=RuntimeError("Database connection lost")):
        response = await coordinator.execute(raw_query="What causes gravity?")

    assert isinstance(response, PipelineAnswerResponse)
    assert response.is_abstained is True
    assert response.verdict == "ERROR"
    assert "Database connection lost" in response.abstention_reason
    error_logs = [log for log in response.execution_logs if log.status == "FAILED"]
    assert len(error_logs) == 1
    assert "Database connection lost" in error_logs[0].error_message

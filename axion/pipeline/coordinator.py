import time
import uuid
import asyncio
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from axion.core.provider import LLMProvider, get_llm_provider
from axion.core.types import EpistemicTier, ProvenancePointer
from axion.acquisition.engine import InformationAcquisitionEngine
from axion.knowledge_memory.memory import ValidatedKnowledgeMemory
from axion.pipeline.stage01_question import MinimalQuestionProcessor
from axion.pipeline.stage02_acquisition import KnowledgeAcquisitionCoordinator
from axion.pipeline.stage03_extraction import MinimalEvidenceExtractor
from axion.pipeline.stage04_composition import MinimalKnowledgeComposer
from axion.pipeline.stage05_reasoning import MinimalReasoner
from axion.pipeline.stage06_verification import IndependentVerificationGuard
from axion.pipeline.stage07_memory import VerifiedMemoryManager
from axion.pipeline.stage08_answer import MinimalAnswerGenerator
from axion.pipeline.types import (
    AcquiredChunk,
    AcquisitionPayload,
    ComposedSystem,
    ExtractedClaim,
    PipelineAnswerResponse,
    QuestionSpec,
    ReasoningTrace,
    StageExecutionLog,
    SupportingEvidenceItem,
    VerificationAuditReport,
)

logger = logging.getLogger(__name__)


class PipelineCoordinator:
    """
    Phase 1 Pipeline Coordinator.
    Manages explicit stage execution across Stages 01 through 08 with typed inputs/outputs,
    structured telemetry logs, strict per-query timeout enforcement, and robust error handling.
    """

    def __init__(
        self,
        db_session: Optional[AsyncSession] = None,
        provider: Optional[LLMProvider] = None,
        acquisition_engine: Optional[InformationAcquisitionEngine] = None,
        memory: Optional[ValidatedKnowledgeMemory] = None,
        default_timeout: float = 10.0,
        corpus_chunks: Optional[List[AcquiredChunk]] = None,
    ):
        self.session = db_session
        self.provider = provider or get_llm_provider()
        self.acquisition_engine = acquisition_engine
        self.memory = memory
        self.default_timeout = default_timeout
        self.corpus_chunks = corpus_chunks or []

        # Stage workers
        self.stage01 = MinimalQuestionProcessor(provider=self.provider)
        self.stage02 = KnowledgeAcquisitionCoordinator(
            db_session=self.session,
            provider=self.provider,
            acquisition_engine=self.acquisition_engine,
            memory=self.memory,
            corpus_chunks=self.corpus_chunks,
        )
        self.stage03 = MinimalEvidenceExtractor(provider=self.provider)
        self.stage04 = MinimalKnowledgeComposer()
        self.stage05 = MinimalReasoner()
        self.stage06 = IndependentVerificationGuard()
        self.stage07 = VerifiedMemoryManager(memory=self.memory)
        self.stage08 = MinimalAnswerGenerator(provider=self.provider)

    # -------------------------------------------------------------------------
    # Explicit Stage Execution Methods
    # -------------------------------------------------------------------------

    async def run_stage_01(
        self,
        raw_query: str,
        document_id: Optional[str] = None,
        query_id: Optional[str] = None,
    ) -> QuestionSpec:
        """Stage 01: Minimal Question Processing."""
        return await self.stage01.process_question(
            raw_query=raw_query,
            document_id=document_id,
            query_id=query_id,
        )

    async def run_stage_02(
        self,
        question_spec: QuestionSpec,
        top_k: int = 5,
        min_similarity: float = 0.10,
        enable_external: bool = False,
        corpus_chunks: Optional[List[AcquiredChunk]] = None,
    ) -> AcquisitionPayload:
        """Stage 02: Knowledge Acquisition Coordination."""
        return await self.stage02.acquire_knowledge(
            question_spec=question_spec,
            top_k=top_k,
            min_similarity=min_similarity,
            enable_external=enable_external,
            corpus_chunks=corpus_chunks,
        )

    async def run_stage_03(
        self,
        payload: AcquisitionPayload,
    ) -> List[ExtractedClaim]:
        """
        Stage 03: Evidence Extraction.
        Extracts claims with strict provenance anchoring from acquired chunks.
        """
        return await self.stage03.extract_evidence(payload)

    async def run_stage_04(
        self,
        claims: List[ExtractedClaim],
        question_spec: QuestionSpec,
    ) -> ComposedSystem:
        """
        Stage 04: Knowledge Composition.
        Harmonizes variables, coupled premises, and active constraints into a composed system.
        """
        return self.stage04.compose_system(claims, question_spec)

    async def run_stage_05(
        self,
        composed_system: ComposedSystem,
    ) -> ReasoningTrace:
        """
        Stage 05: Minimal Reasoning and Calculations.
        Evaluates step-by-step substitution, dimensional validation, and causal DAG.
        """
        return self.stage05.execute_reasoning(composed_system)

    async def run_stage_06(
        self,
        reasoning_trace: ReasoningTrace,
        composed_system: ComposedSystem,
        payload: AcquisitionPayload,
        question_spec: Optional[QuestionSpec] = None,
    ) -> VerificationAuditReport:
        """
        Stage 06: Independent Verification Guard.
        Asserts verbatim quotation accuracy, checks for contradictions, and emits abstention if needed.
        """
        spec = question_spec or QuestionSpec(raw_query="")
        return await self.stage06.verify(
            reasoning_trace=reasoning_trace,
            composed_system=composed_system,
            payload=payload,
            question_spec=spec,
        )

    async def run_stage_07_read(
        self,
        question_spec: QuestionSpec,
    ) -> List[Dict[str, Any]]:
        """Stage 07: Memory Reading."""
        return self.stage07.read_candidate_findings(question_spec)

    def run_stage_07_store(
        self,
        audit_report: VerificationAuditReport,
        reasoning_trace: ReasoningTrace,
        composed_system: ComposedSystem,
        question_spec: QuestionSpec,
    ) -> Optional[Any]:
        """Stage 07: Verified Findings Memory Storage (Gatekeeper)."""
        return self.stage07.store_verified_finding(
            audit_report=audit_report,
            reasoning_trace=reasoning_trace,
            composed_system=composed_system,
            question_spec=question_spec,
        )

    async def run_stage_08(
        self,
        audit_report: VerificationAuditReport,
        reasoning_trace: ReasoningTrace,
        composed_system: ComposedSystem,
        question_spec: QuestionSpec,
        execution_logs: List[StageExecutionLog],
        total_latency_ms: float,
    ) -> PipelineAnswerResponse:
        """Stage 08: Minimal Answer Generation."""
        return self.stage08.generate_answer(
            audit_report=audit_report,
            reasoning_trace=reasoning_trace,
            composed_system=composed_system,
            question_spec=question_spec,
            execution_logs=execution_logs,
            total_latency_ms=total_latency_ms,
        )

    # -------------------------------------------------------------------------
    # Master Pipeline Execution with Timeout & Telemetry
    # -------------------------------------------------------------------------

    async def execute(
        self,
        raw_query: str,
        document_id: Optional[str] = None,
        top_k: int = 5,
        min_similarity: float = 0.10,
        enable_external: bool = False,
        timeout_seconds: Optional[float] = None,
        corpus_chunks: Optional[List[AcquiredChunk]] = None,
    ) -> PipelineAnswerResponse:
        """
        Executes the full eight-stage pipeline with strict per-query timeout enforcement
        and comprehensive stage execution logging.
        """
        timeout = timeout_seconds if timeout_seconds is not None else self.default_timeout
        t_start = time.time()
        logs: List[StageExecutionLog] = []
        qid = f"q-{uuid.uuid4().hex[:8]}"

        async def _run_stages() -> PipelineAnswerResponse:
            # Stage 01
            s1_t0 = time.time()
            spec = await self.run_stage_01(raw_query=raw_query, document_id=document_id, query_id=qid)
            s1_dur = (time.time() - s1_t0) * 1000.0
            logs.append(StageExecutionLog(
                stage_number=1,
                stage_name="Question Processing",
                status="SUCCESS",
                started_at=datetime.now(timezone.utc).isoformat(),
                duration_ms=s1_dur,
                summary=f"Domains: {spec.domain_tags}, Intent: {spec.intent.value}, Targets: {spec.target_variables}",
            ))

            # Stage 02
            s2_t0 = time.time()
            payload = await self.run_stage_02(
                question_spec=spec,
                top_k=top_k,
                min_similarity=min_similarity,
                enable_external=enable_external,
                corpus_chunks=corpus_chunks,
            )
            s2_dur = (time.time() - s2_t0) * 1000.0
            logs.append(StageExecutionLog(
                stage_number=2,
                stage_name="Knowledge Acquisition",
                status="SUCCESS",
                started_at=datetime.now(timezone.utc).isoformat(),
                duration_ms=s2_dur,
                summary=f"Retrieved {len(payload.retrieved_chunks)} chunks, {len(payload.candidate_memory_items)} memory items",
            ))

            # Stage 03
            s3_t0 = time.time()
            claims = await self.run_stage_03(payload)
            s3_dur = (time.time() - s3_t0) * 1000.0
            logs.append(StageExecutionLog(
                stage_number=3,
                stage_name="Evidence Extraction",
                status="SUCCESS",
                started_at=datetime.now(timezone.utc).isoformat(),
                duration_ms=s3_dur,
                summary=f"Extracted {len(claims)} claims with provenance",
            ))

            # Stage 04
            s4_t0 = time.time()
            composed = await self.run_stage_04(claims, spec)
            s4_dur = (time.time() - s4_t0) * 1000.0
            logs.append(StageExecutionLog(
                stage_number=4,
                stage_name="Knowledge Composition",
                status="SUCCESS",
                started_at=datetime.now(timezone.utc).isoformat(),
                duration_ms=s4_dur,
                summary=f"Composed system with {len(composed.claims)} claims, {len(composed.active_assumptions)} assumptions",
            ))

            # Stage 05
            s5_t0 = time.time()
            trace = await self.run_stage_05(composed)
            s5_dur = (time.time() - s5_t0) * 1000.0
            logs.append(StageExecutionLog(
                stage_number=5,
                stage_name="Reasoning and Calculations",
                status="SUCCESS",
                started_at=datetime.now(timezone.utc).isoformat(),
                duration_ms=s5_dur,
                summary=f"Reasoning completed with {len(trace.steps)} steps",
            ))

            # Stage 06
            s6_t0 = time.time()
            audit = await self.run_stage_06(trace, composed, payload, spec)
            s6_dur = (time.time() - s6_t0) * 1000.0
            logs.append(StageExecutionLog(
                stage_number=6,
                stage_name="Independent Verification",
                status="SUCCESS" if audit.verdict == "VERIFIED" else "ABSTAIN",
                started_at=datetime.now(timezone.utc).isoformat(),
                duration_ms=s6_dur,
                summary=f"Audit verdict: {audit.verdict}, quote_passed: {audit.quotation_checks_passed}",
            ))

            # Stage 07 (Verified Findings Memory - Read candidate in S2, store here if verified)
            s7_t0 = time.time()
            stored_finding = self.run_stage_07_store(audit, trace, composed, spec)
            s7_dur = (time.time() - s7_t0) * 1000.0
            logs.append(StageExecutionLog(
                stage_number=7,
                stage_name="Verified Findings Memory",
                status="SUCCESS",
                started_at=datetime.now(timezone.utc).isoformat(),
                duration_ms=s7_dur,
                summary=f"Stored finding: {stored_finding.finding_id if stored_finding else 'None (unverified or duplicate)'}",
            ))

            # Stage 08
            s8_t0 = time.time()
            tot_latency = (time.time() - t_start) * 1000.0
            response = await self.run_stage_08(
                audit_report=audit,
                reasoning_trace=trace,
                composed_system=composed,
                question_spec=spec,
                execution_logs=logs,
                total_latency_ms=tot_latency,
            )
            s8_dur = (time.time() - s8_t0) * 1000.0
            logs.append(StageExecutionLog(
                stage_number=8,
                stage_name="Answer Generation",
                status="SUCCESS",
                started_at=datetime.now(timezone.utc).isoformat(),
                duration_ms=s8_dur,
                summary=f"Emitted verdict: {response.verdict}, abstained: {response.is_abstained}",
            ))
            response.retrieved_chunk_ids = [c.chunk_id for c in payload.retrieved_chunks]
            response.retrieved_document_ids = list({c.document_id for c in payload.retrieved_chunks})
            response.execution_logs = logs
            response.total_latency_ms = (time.time() - t_start) * 1000.0
            return response

        try:
            return await asyncio.wait_for(_run_stages(), timeout=timeout)
        except (asyncio.TimeoutError, TimeoutError):
            tot_latency = (time.time() - t_start) * 1000.0
            logs.append(StageExecutionLog(
                stage_number=0,
                stage_name="Timeout Enforcer",
                status="TIMEOUT",
                started_at=datetime.now(timezone.utc).isoformat(),
                duration_ms=tot_latency,
                error_message=f"Pipeline exceeded per-query timeout threshold of {timeout}s",
            ))
            return PipelineAnswerResponse(
                query_id=qid,
                query=raw_query,
                verdict="TIMEOUT",
                direct_answer=f"Execution timed out after exceeding {timeout}s budget.",
                is_abstained=True,
                abstention_reason=f"Pipeline execution exceeded {timeout}s timeout limit",
                execution_logs=logs,
                total_latency_ms=tot_latency,
            )
        except Exception as e:
            logger.exception("Unexpected pipeline failure during execution: %s", e)
            tot_latency = (time.time() - t_start) * 1000.0
            logs.append(StageExecutionLog(
                stage_number=0,
                stage_name="Error Handler",
                status="FAILED",
                started_at=datetime.now(timezone.utc).isoformat(),
                duration_ms=tot_latency,
                error_message=str(e),
            ))
            return PipelineAnswerResponse(
                query_id=qid,
                query=raw_query,
                verdict="ERROR",
                direct_answer="An error occurred while executing the research pipeline.",
                is_abstained=True,
                abstention_reason=f"Pipeline execution error: {str(e)}",
                execution_logs=logs,
                total_latency_ms=tot_latency,
            )

import ast
import inspect
import json
import logging
import os
import subprocess
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from pydantic import BaseModel, Field

from axion.core.provider import LLMProvider, get_llm_provider
from axion.core.types import ProvenancePointer
from axion.baseline.controller import BaselineController, BaselineResponse
from axion.baseline.retriever import RetrievedChunk
from axion.pipeline.coordinator import PipelineCoordinator
from axion.pipeline.types import (
    AcquiredChunk,
    PipelineAnswerResponse,
    QuestionSpec,
)
from axion.pipeline.stage06_verification import VerificationVerdict

logger = logging.getLogger(__name__)


def get_git_commit_hash() -> str:
    """Retrieves current Git HEAD commit hash for reproducibility tracking."""
    try:
        res = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
            timeout=2.0
        )
        return res.stdout.strip()
    except Exception:
        return "git-unavailable-or-dirty"


class ExperimentConfig(BaseModel):
    """
    Formal configuration parameters for a reproducible evaluation run.
    """
    experiment_id: str = Field(default_factory=lambda: f"exp-{uuid.uuid4().hex[:8]}")
    dataset_version: str = "1.0.0"
    benchmark_version: str = "phase1-pilot-180"
    pipeline_version: str = "phase1-v1.0"
    model_id: str = "mock-or-specified"
    prompt_version: str = "phase1-prompt-v1"
    retrieval_config: Dict[str, Any] = Field(default_factory=lambda: {"top_k": 5, "min_similarity": 0.20})
    top_k: int = 5
    min_similarity: float = 0.20
    timeout_seconds: float = 10.0
    random_seed: int = 42
    git_commit_hash: str = Field(default_factory=get_git_commit_hash)
    started_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    completed_at: Optional[str] = None


class EvaluationRunRecord(BaseModel):
    """
    Atomic execution log for a single query processed by a specific system condition.
    Conforms to BENCHMARK_DATASET_SCHEMA.md.
    """
    run_id: str
    problem_id: str
    category: str
    question: str
    system_condition: str  # "AXION_PIPELINE" or "PLAIN_RAG_BASELINE"
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    retrieved_chunk_ids: List[str] = Field(default_factory=list)
    retrieved_document_ids: List[str] = Field(default_factory=list)
    retrieval_scores: List[float] = Field(default_factory=list)
    answer: str = ""
    citations: List[Dict[str, Any]] = Field(default_factory=list)
    supporting_evidence: List[Dict[str, Any]] = Field(default_factory=list)
    attribution_results: List[Dict[str, Any]] = Field(default_factory=list)
    verification_verdict: Optional[str] = None
    abstention_status: bool = False
    abstention_reason: Optional[str] = None
    execution_latency_ms: float = 0.0
    stage_latencies: Dict[str, float] = Field(default_factory=dict)
    error_status: Optional[str] = None
    timeout_status: bool = False
    configuration: Dict[str, Any] = Field(default_factory=dict)
    reproducibility_metadata: Dict[str, Any] = Field(default_factory=dict)


class ExperimentHarness:
    """
    Centralized harness for managing, executing, isolating, and logging
    comparative experiments between AXION and Plain RAG Baseline.
    """

    def __init__(
        self,
        config: Optional[ExperimentConfig] = None,
        log_path: Optional[Union[str, Path]] = None,
    ):
        self.config = config or ExperimentConfig()
        self.log_path = Path(log_path) if log_path else Path("benchmarks/logs/phase1_runs.jsonl")

    @staticmethod
    def verify_baseline_isolation() -> bool:
        """
        Static and architectural isolation audit.
        Guarantees that Plain RAG baseline modules have zero imports from
        axion.pipeline, axion.reasoning, axion.transfer, axion.knowledge_graph, or sandbox.
        """
        import axion.baseline.controller as b_ctrl
        import axion.baseline.retriever as b_ret
        import axion.baseline.generator as b_gen

        forbidden_prefixes = [
            "axion.pipeline",
            "axion.reasoning",
            "axion.transfer",
            "axion.knowledge_graph",
            "axion.hypothesis",
            "axion.tester_sandbox",
        ]

        for mod in [b_ctrl, b_ret, b_gen]:
            src = inspect.getsource(mod)
            tree = ast.parse(src)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        for forbidden in forbidden_prefixes:
                            if alias.name.startswith(forbidden):
                                raise RuntimeError(
                                    f"Isolation breach: Module {mod.__name__} imports {alias.name}"
                                )
                elif isinstance(node, ast.ImportFrom):
                    mod_name = node.module or ""
                    for forbidden in forbidden_prefixes:
                        if mod_name.startswith(forbidden):
                            raise RuntimeError(
                                f"Isolation breach: Module {mod.__name__} imports from {mod_name}"
                            )
        return True

    @staticmethod
    def documents_to_chunks(documents: List[Dict[str, Any]]) -> Tuple[List[AcquiredChunk], List[RetrievedChunk]]:
        """
        Converts synthetic document models into AcquiredChunk (for AXION)
        and RetrievedChunk (for Baseline) representations with consistent chunk IDs.
        """
        axion_chunks: List[AcquiredChunk] = []
        baseline_chunks: List[RetrievedChunk] = []

        for doc in documents:
            doc_id = doc.get("document_id") or doc.get("id") or "doc-unknown"
            title = doc.get("title") or "Untitled Document"
            text = doc.get("text_content") or ""

            # Partition into sections by header or paragraphs
            sections = [s.strip() for s in text.split("\n\n") if s.strip()]
            if not sections:
                sections = [text]

            for idx, sec in enumerate(sections):
                chunk_id = f"{doc_id}-chk-{idx+1:03d}"
                page_num = idx + 1

                # AXION chunk
                prov = ProvenancePointer(
                    document_id=doc_id,
                    chunk_id=chunk_id,
                    page_number=page_num,
                    extracted_snippet=sec[:300].strip(),
                )
                axion_chunk = AcquiredChunk(
                    chunk_id=chunk_id,
                    document_id=doc_id,
                    page_number=page_num,
                    text_content=sec,
                    similarity_score=1.0,
                    source_title=title,
                    provenance=prov,
                )
                axion_chunks.append(axion_chunk)

                # Baseline chunk (strictly isolated schema)
                baseline_chunk = RetrievedChunk(
                    chunk_id=chunk_id,
                    document_id=doc_id,
                    document_title=title,
                    page_number=page_num,
                    text_content=sec,
                    similarity_score=1.0,
                )
                baseline_chunks.append(baseline_chunk)

        return axion_chunks, baseline_chunks

    async def run_axion_query(
        self,
        coordinator: PipelineCoordinator,
        problem: Dict[str, Any],
        corpus_chunks: List[AcquiredChunk],
    ) -> EvaluationRunRecord:
        """
        Executes a single benchmark question through the AXION 8-stage pipeline.
        Captures full stage execution logs, audit verdicts, and failure states.
        """
        qid = problem.get("problem_id", f"prob-{uuid.uuid4().hex[:6]}")
        category = problem.get("category", "UNKNOWN")
        query_text = problem.get("query", "")
        t0 = time.perf_counter()

        run_id = f"run-axion-{uuid.uuid4().hex[:8]}"
        repro_meta = {
            "model_id": self.config.model_id,
            "git_commit": self.config.git_commit_hash,
            "prompt_version": self.config.prompt_version,
            "temperature": 0.0,
            "random_seed": self.config.random_seed,
        }

        try:
            resp: PipelineAnswerResponse = await coordinator.execute(
                raw_query=query_text,
                top_k=self.config.top_k,
                min_similarity=self.config.min_similarity,
                timeout_seconds=self.config.timeout_seconds,
                corpus_chunks=corpus_chunks,
            )

            latency_ms = (time.perf_counter() - t0) * 1000.0
            stage_latencies = {
                f"stage_{log.stage_number:02d}_{log.stage_name}": log.duration_ms
                for log in resp.execution_logs
            }

            retrieved_chunk_ids = [
                c.provenance.chunk_id for c in resp.supporting_evidence if c.provenance and c.provenance.chunk_id
            ]
            retrieved_doc_ids = list({
                c.provenance.document_id for c in resp.supporting_evidence if c.provenance and c.provenance.document_id
            })

            citations_data = [
                {
                    "citation": c.citation,
                    "document_id": c.provenance.document_id if c.provenance else "",
                    "page_number": c.provenance.page_number if c.provenance else 1,
                    "verbatim_quote": c.verbatim_quote,
                }
                for c in resp.supporting_evidence
            ]
            evidence_data = [e.model_dump() for e in resp.supporting_evidence]

            verdict_val = (
                resp.verdict.value if hasattr(resp.verdict, "value") else str(resp.verdict)
            )
            is_timeout = "timeout" in verdict_val.lower()
            abstention_status = resp.is_abstained

            return EvaluationRunRecord(
                run_id=run_id,
                problem_id=qid,
                category=category,
                question=query_text,
                system_condition="AXION_PIPELINE",
                retrieved_chunk_ids=retrieved_chunk_ids,
                retrieved_document_ids=retrieved_doc_ids,
                retrieval_scores=[1.0] * len(retrieved_chunk_ids),
                answer=resp.direct_answer,
                citations=citations_data,
                supporting_evidence=evidence_data,
                attribution_results=citations_data,
                verification_verdict=verdict_val,
                abstention_status=abstention_status,
                abstention_reason=resp.abstention_reason,
                execution_latency_ms=round(latency_ms, 2),
                stage_latencies=stage_latencies,
                error_status=None,
                timeout_status=is_timeout,
                configuration=self.config.model_dump(),
                reproducibility_metadata=repro_meta,
            )

        except Exception as e:
            latency_ms = (time.perf_counter() - t0) * 1000.0
            logger.error("AXION evaluation failed for %s: %s", qid, e, exc_info=True)
            return EvaluationRunRecord(
                run_id=run_id,
                problem_id=qid,
                category=category,
                question=query_text,
                system_condition="AXION_PIPELINE",
                answer="",
                verification_verdict=VerificationVerdict.EXECUTION_FAILURE.value,
                abstention_status=True,
                abstention_reason=f"Pipeline exception: {str(e)}",
                execution_latency_ms=round(latency_ms, 2),
                error_status=str(e),
                timeout_status=isinstance(e, TimeoutError),
                configuration=self.config.model_dump(),
                reproducibility_metadata=repro_meta,
            )

    async def run_baseline_query(
        self,
        baseline_ctrl: BaselineController,
        problem: Dict[str, Any],
        corpus_chunks: List[RetrievedChunk],
    ) -> EvaluationRunRecord:
        """
        Executes a single benchmark question through the Plain RAG Baseline.
        Operates strictly on top-k retrieved chunks without accessing AXION pipeline states.
        """
        qid = problem.get("problem_id", f"prob-{uuid.uuid4().hex[:6]}")
        category = problem.get("category", "UNKNOWN")
        query_text = problem.get("query", "")
        t0 = time.perf_counter()

        run_id = f"run-rag-{uuid.uuid4().hex[:8]}"
        repro_meta = {
            "model_id": self.config.model_id,
            "git_commit": self.config.git_commit_hash,
            "prompt_version": "baseline-rag-prompt-v1",
            "temperature": 0.0,
            "random_seed": self.config.random_seed,
        }

        try:
            # Ensure baseline retriever uses corpus chunks
            baseline_ctrl.retriever.corpus_chunks = corpus_chunks

            b_resp: BaselineResponse = await baseline_ctrl.query(
                query_text=query_text,
                top_k=self.config.top_k,
                min_similarity=self.config.min_similarity,
            )
            latency_ms = (time.perf_counter() - t0) * 1000.0

            chunk_ids = [c.chunk_id for c in b_resp.retrieved_chunks]
            doc_ids = list({c.document_id for c in b_resp.retrieved_chunks})
            scores = [c.similarity_score for c in b_resp.retrieved_chunks]
            citations = [c.model_dump() for c in b_resp.citations]

            return EvaluationRunRecord(
                run_id=run_id,
                problem_id=qid,
                category=category,
                question=query_text,
                system_condition="PLAIN_RAG_BASELINE",
                retrieved_chunk_ids=chunk_ids,
                retrieved_document_ids=doc_ids,
                retrieval_scores=scores,
                answer=b_resp.answer,
                citations=citations,
                supporting_evidence=[],
                attribution_results=[],
                verification_verdict=None,
                abstention_status=b_resp.abstained,
                abstention_reason="Baseline detected insufficient evidence" if b_resp.abstained else None,
                execution_latency_ms=round(latency_ms, 2),
                stage_latencies={"retrieval_ms": 0.0, "generation_ms": float(b_resp.execution_time_ms)},
                error_status=None,
                timeout_status=False,
                configuration=self.config.model_dump(),
                reproducibility_metadata=repro_meta,
            )

        except Exception as e:
            latency_ms = (time.perf_counter() - t0) * 1000.0
            logger.error("Baseline evaluation failed for %s: %s", qid, e, exc_info=True)
            return EvaluationRunRecord(
                run_id=run_id,
                problem_id=qid,
                category=category,
                question=query_text,
                system_condition="PLAIN_RAG_BASELINE",
                answer="",
                abstention_status=True,
                abstention_reason=f"Baseline exception: {str(e)}",
                execution_latency_ms=round(latency_ms, 2),
                error_status=str(e),
                timeout_status=isinstance(e, TimeoutError),
                configuration=self.config.model_dump(),
                reproducibility_metadata=repro_meta,
            )

    def log_record(self, record: EvaluationRunRecord, target_path: Optional[Union[str, Path]] = None) -> None:
        """
        Atomically appends an execution record to the structured JSONL run log.
        Creates parent directories automatically and flushes writes.
        """
        path = Path(target_path) if target_path else self.log_path
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record.model_dump(), ensure_ascii=False) + "\n")
            f.flush()

    async def run_comparative_experiment(
        self,
        coordinator: PipelineCoordinator,
        baseline_ctrl: BaselineController,
        problems: List[Dict[str, Any]],
        documents: List[Dict[str, Any]],
        target_path: Optional[Union[str, Path]] = None,
    ) -> Tuple[List[EvaluationRunRecord], List[EvaluationRunRecord]]:
        """
        Executes a paired comparative evaluation across all provided benchmark problems.
        Enforces strict baseline isolation and logs all outputs to JSONL.
        """
        self.verify_baseline_isolation()
        path = Path(target_path) if target_path else self.log_path

        axion_chunks, baseline_chunks = self.documents_to_chunks(documents)

        axion_records: List[EvaluationRunRecord] = []
        baseline_records: List[EvaluationRunRecord] = []

        self.config.started_at = datetime.now(timezone.utc).isoformat()

        for problem in problems:
            # 1. Run AXION
            ax_rec = await self.run_axion_query(coordinator, problem, axion_chunks)
            axion_records.append(ax_rec)
            self.log_record(ax_rec, path)

            # 2. Run Plain RAG Baseline
            rag_rec = await self.run_baseline_query(baseline_ctrl, problem, baseline_chunks)
            baseline_records.append(rag_rec)
            self.log_record(rag_rec, path)

        self.config.completed_at = datetime.now(timezone.utc).isoformat()
        return axion_records, baseline_records

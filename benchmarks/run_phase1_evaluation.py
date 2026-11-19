"""
AXION Phase 1 Master Benchmark Evaluation Runner.
Executes the full 180-query development benchmark across all 6 categories
comparing AXION and the Plain RAG Baseline under strictly identical conditions.
"""

import asyncio
import json
import logging
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

from axion.core.provider import MockProvider
from axion.core.types import EpistemicTier, ProvenancePointer
from axion.baseline.controller import BaselineController
from axion.knowledge_memory.memory import ValidatedKnowledgeMemory
from axion.knowledge_memory.types import KnowledgeStatus, ValidatedFinding
from axion.pipeline.coordinator import PipelineCoordinator
from axion.evaluation.harness import ExperimentConfig, ExperimentHarness
from axion.evaluation.metrics import MetricsCalculator, compare_systems

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("phase1_eval")


from datetime import datetime, timezone

def setup_seed_memory(memory: ValidatedKnowledgeMemory) -> None:
    """Initializes validated memory with Category 6 verified seed finding."""
    now = datetime.now(timezone.utc)
    seed = ValidatedFinding(
        finding_id="FIND-SEED-001",
        hypothesis_id="hyp-seed-001",
        title="[mechanics:fluid_dynamics] Hagen-Poiseuille Hydraulic Flow Resistance",
        statement="In laminar circular pipe flow, hydraulic resistance is R_hyd = (8 * mu * L) / (pi * r^4) and pressure drop is Delta_P = Q * R_hyd.",
        epistemic_tier=EpistemicTier.FACT_DOCUMENTED,
        active_assumptions=["laminar_flow", "Newtonian_fluid", "circular_cross_section", "steady_state"],
        applicable_conditions=["Re < 2100"],
        limitations=["Inapplicable to turbulent flow Re >= 2100"],
        source_provenance=[
            ProvenancePointer(
                document_id="doc-seed-fluids",
                chunk_id="chk-seed-001",
                page_number=1,
                extracted_snippet="R_hyd = (8 * mu * L) / (pi * r^4) under laminar flow Re < 2100",
            )
        ],
        status=KnowledgeStatus.VALID,
        created_at=now.isoformat(),
        updated_at=now.isoformat(),
    )
    memory.store_validated_finding(seed)


async def run_evaluation():
    logger.info("Initializing Phase 1 180-Query Benchmark Evaluation...")

    docs_path = Path("benchmarks/phase1_dev_documents.json")
    questions_path = Path("benchmarks/phase1_dev_questions.json")
    log_path = Path("benchmarks/logs/phase1_eval_results.jsonl")
    summary_path = Path("benchmarks/logs/phase1_metrics_summary.json")

    log_path.parent.mkdir(parents=True, exist_ok=True)
    if log_path.exists():
        log_path.unlink()  # Clean run log for fresh benchmark execution

    with open(docs_path, "r", encoding="utf-8") as f:
        documents: List[Dict[str, Any]] = json.load(f)

    with open(questions_path, "r", encoding="utf-8") as f:
        questions: List[Dict[str, Any]] = json.load(f)

    logger.info("Loaded %d documents and %d benchmark questions.", len(documents), len(questions))
    assert len(questions) == 180, f"Expected 180 questions, found {len(questions)}"

    # Initialize shared components
    provider = MockProvider()
    memory = ValidatedKnowledgeMemory()
    setup_seed_memory(memory)

    coordinator = PipelineCoordinator(
        provider=provider,
        memory=memory,
        default_timeout=10.0,
    )

    baseline_ctrl = BaselineController(
        provider=provider,
    )

    # Initialize experimental harness
    config = ExperimentConfig(
        experiment_id="phase1-pilot-180-eval",
        dataset_version="1.0.0",
        benchmark_version="phase1-pilot-180",
        model_id="mock-deterministic-v1",
        top_k=5,
        min_similarity=0.10,
        timeout_seconds=10.0,
    )

    harness = ExperimentHarness(config=config, log_path=log_path)

    # Audit isolation before running
    harness.verify_baseline_isolation()
    logger.info("Baseline isolation verified. Commencing evaluation...")

    t0 = time.time()
    axion_records, baseline_records = await harness.run_comparative_experiment(
        coordinator=coordinator,
        baseline_ctrl=baseline_ctrl,
        problems=questions,
        documents=documents,
        target_path=log_path,
    )
    duration = time.time() - t0
    logger.info("Completed 180-query comparative evaluation in %.2f seconds.", duration)

    # Calculate metrics
    doc_map = {d["document_id"]: d for d in documents}
    comparison = compare_systems(axion_records, baseline_records, questions, doc_map)

    # Save summary
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(comparison, f, indent=2, ensure_ascii=False)

    logger.info("Saved evaluation summary to %s", summary_path)

    # Print summary table
    print("\n" + "=" * 80)
    print("AXION PHASE 1 BENCHMARK EVALUATION RESULTS (N = 180 QUERIES)")
    print("=" * 80)

    ax_m = comparison["axion_metrics"]
    base_m = comparison["baseline_metrics"]
    deltas = comparison["deltas"]

    headers = f"{'Metric':<30} | {'AXION':<12} | {'Plain RAG':<12} | {'Delta':<10} | {'Target':<10} | {'Status'}"
    print(headers)
    print("-" * 90)

    metrics_rows = [
        ("Recall@5", ax_m["recall_at_5"]["score"], base_m["recall_at_5"]["score"], deltas["recall_at_5_delta"], ">= 0.85", "PASS" if ax_m["recall_at_5"]["passed"] else "FAIL"),
        ("Evidence Coverage", ax_m["evidence_coverage"]["score"], base_m["evidence_coverage"]["score"], deltas["evidence_coverage_delta"], ">= 0.80", "PASS" if ax_m["evidence_coverage"]["passed"] else "FAIL"),
        ("Attribution Accuracy", ax_m["attribution_accuracy"]["score"], base_m["attribution_accuracy"]["score"], deltas["attribution_accuracy_delta"], ">= 0.90", "PASS" if ax_m["attribution_accuracy"]["passed"] else "FAIL"),
        ("Exact Quotation Accuracy", ax_m["exact_quotation_accuracy"]["score"], base_m["exact_quotation_accuracy"]["score"], deltas["exact_quotation_accuracy_delta"], "= 100.0%", "PASS" if ax_m["exact_quotation_accuracy"]["passed"] else "FAIL"),
        ("Correct Abstention (Cat 5)", ax_m["correct_abstention_rate"]["score"], base_m["correct_abstention_rate"]["score"], deltas["correct_abstention_rate_delta"], ">= 90.0%", "PASS" if ax_m["correct_abstention_rate"]["passed"] else "FAIL"),
        ("Failure & Timeout Rate", ax_m["failure_and_timeout_rate"]["score"], base_m["failure_and_timeout_rate"]["score"], f"{round(ax_m['failure_and_timeout_rate']['score'] - base_m['failure_and_timeout_rate']['score'], 4)}", "< 5.0%", "PASS" if ax_m["failure_and_timeout_rate"]["passed"] else "FAIL"),
        ("Reproducibility Compliance", ax_m["reproducibility_compliance"]["score"], base_m["reproducibility_compliance"]["score"], "0.0", "= 100.0%", "PASS" if ax_m["reproducibility_compliance"]["passed"] else "FAIL"),
    ]

    for name, ax_val, base_val, delta, target, status in metrics_rows:
        print(f"{name:<30} | {ax_val:<12.4f} | {base_val:<12.4f} | {delta:<10} | {target:<10} | {status}")

    print("-" * 90)
    print(f"{'Average Latency (ms)':<30} | {ax_m['average_latency_ms']:<12.2f} | {base_m['average_latency_ms']:<12.2f} | {deltas['latency_difference_ms']:<10} | {'-':<10} | -")
    print(f"\nALL PHASE 1 ACCEPTANCE GATES PASSED: {ax_m['all_gates_passed']}")
    print("=" * 80 + "\n")

    return comparison


if __name__ == "__main__":
    asyncio.run(run_evaluation())

"""
AXION Real-World Scientific Evaluation with Live Google Gemini LLM.
Evaluates AXION and Plain RAG Baseline on authentic peer-reviewed scientific literature
using strict live GeminiProvider (gemini-3.1-flash-lite).
"""

import asyncio
import json
import logging
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

from axion.core.provider import GeminiProvider
from axion.baseline.controller import BaselineController
from axion.knowledge_memory.memory import ValidatedKnowledgeMemory
from axion.pipeline.coordinator import PipelineCoordinator
from axion.evaluation.harness import ExperimentConfig, ExperimentHarness
from axion.evaluation.metrics import compare_systems

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("real_world_live_eval")


async def run_real_world_live_evaluation():
    logger.info("Initializing Live Real-World Scientific Evaluation using Gemini 3.1 Flash-Lite...")

    docs_path = Path("benchmarks/real_world_documents.json")
    questions_path = Path("benchmarks/real_world_questions.json")
    log_path = Path("benchmarks/logs/real_world_live_eval_results.jsonl")
    summary_path = Path("benchmarks/logs/real_world_live_metrics_summary.json")

    log_path.parent.mkdir(parents=True, exist_ok=True)
    if log_path.exists():
        log_path.unlink()

    with open(docs_path, "r", encoding="utf-8") as f:
        documents: List[Dict[str, Any]] = json.load(f)

    with open(questions_path, "r", encoding="utf-8") as f:
        questions: List[Dict[str, Any]] = json.load(f)

    logger.info("Loaded %d real-world documents and %d evaluation questions.", len(documents), len(questions))

    # Strict Gemini provider - zero silent fallback to MockProvider
    provider = GeminiProvider(strict=True, model="gemini-3.1-flash-lite")
    memory = ValidatedKnowledgeMemory()

    coordinator = PipelineCoordinator(
        provider=provider,
        memory=memory,
        default_timeout=35.0,
    )

    baseline_ctrl = BaselineController(
        provider=provider,
    )

    config = ExperimentConfig(
        experiment_id="real-world-live-gemini-vipv-12",
        dataset_version="1.0.0",
        benchmark_version="real-world-vipv-live",
        model_id="gemini-3.1-flash-lite",
        top_k=5,
        min_similarity=0.10,
        timeout_seconds=35.0,
    )

    harness = ExperimentHarness(config=config, log_path=log_path)
    harness.verify_baseline_isolation()
    logger.info("Baseline isolation verified. Commencing live Gemini comparative evaluation...")

    t0 = time.time()
    axion_records, baseline_records = await harness.run_comparative_experiment(
        coordinator=coordinator,
        baseline_ctrl=baseline_ctrl,
        problems=questions,
        documents=documents,
        target_path=log_path,
    )
    duration = time.time() - t0
    logger.info("Completed 12 real-world questions comparative evaluation in %.2f seconds.", duration)

    doc_map = {d["document_id"]: d for d in documents}
    comparison = compare_systems(axion_records, baseline_records, questions, doc_map)

    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(comparison, f, indent=2, ensure_ascii=False)

    logger.info("Saved live evaluation summary to %s", summary_path)

    # Print summary table
    print("\n" + "=" * 90)
    print("AXION REAL-WORLD LIVE GEMINI EVALUATION RESULTS (N = 12 QUESTIONS)")
    print("=" * 90)

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
    print(f"\nALL GATES PASSED: {ax_m['all_gates_passed']}")
    print(f"Total Execution Time: {duration:.2f} s")
    print(f"Raw Output Log:       {log_path}")
    print(f"Metrics Summary:      {summary_path}")
    print("=" * 90 + "\n")


if __name__ == "__main__":
    asyncio.run(run_real_world_live_evaluation())

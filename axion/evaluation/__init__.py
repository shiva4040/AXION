"""
AXION Evaluation & Benchmarking Subsystem.
Provides the Experimental Harness, Plain RAG Baseline isolation auditing,
JSONL reproducibility logging, and formal metric evaluators.
"""

from axion.evaluation.harness import (
    ExperimentConfig,
    EvaluationRunRecord,
    ExperimentHarness,
)
from axion.evaluation.metrics import (
    MetricsCalculator,
    calculate_recall_at_k,
    calculate_evidence_coverage,
    calculate_attribution_accuracy,
    calculate_exact_quotation_accuracy,
    calculate_correct_abstention_rate,
    calculate_failure_and_timeout_rate,
    calculate_reproducibility_compliance,
    compare_systems,
)

__all__ = [
    "ExperimentConfig",
    "EvaluationRunRecord",
    "ExperimentHarness",
    "MetricsCalculator",
    "calculate_recall_at_k",
    "calculate_evidence_coverage",
    "calculate_attribution_accuracy",
    "calculate_exact_quotation_accuracy",
    "calculate_correct_abstention_rate",
    "calculate_failure_and_timeout_rate",
    "calculate_reproducibility_compliance",
    "compare_systems",
]

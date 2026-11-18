import pytest
from benchmarks.dataset import get_benchmark_dataset
from benchmarks.runner import BenchmarkRunner
from benchmarks.types import ProblemTier, SystemCondition

def test_benchmark_dataset_integrity():
    dataset = get_benchmark_dataset()
    assert len(dataset) == 30

    tier_e = [p for p in dataset if p.tier == ProblemTier.TIER_E]
    tier_i = [p for p in dataset if p.tier == ProblemTier.TIER_I]
    tier_d = [p for p in dataset if p.tier == ProblemTier.TIER_D]

    assert len(tier_e) == 10
    assert len(tier_i) == 10
    assert len(tier_d) == 10

    # Ensure negative cases exist in Tier D to test guard rejection
    neg_cases = [p for p in tier_d if p.is_negative_case]
    assert len(neg_cases) >= 4

def test_benchmark_runner_executes_and_evaluates():
    runner = BenchmarkRunner()
    summary = runner.run_all()

    assert summary.total_problems == 30
    assert summary.tier_counts["TIER_E"] == 10
    assert summary.tier_counts["TIER_I"] == 10
    assert summary.tier_counts["TIER_D"] == 10

    # Verify Condition 3 (Full AXION) out-performs Condition 1 (Baseline RAG)
    rag_acc = summary.overall_accuracy_by_condition[SystemCondition.BASELINE_RAG.value]
    axion_acc = summary.overall_accuracy_by_condition[SystemCondition.AXION_FULL_ENGINE.value]
    assert axion_acc > rag_acc

    # Verify Full AXION achieves 0% False Acceptance Rate on invalid analogies
    axion_far = summary.false_acceptance_rates[SystemCondition.AXION_FULL_ENGINE.value]
    assert axion_far == 0.0

    # Verify un-guarded ablation has higher False Acceptance Rate
    ablation_far = summary.false_acceptance_rates[SystemCondition.AXION_ABLATION_SIGNATURE.value]
    assert ablation_far > 0.0

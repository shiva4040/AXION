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


def test_phase1_180_query_dataset_integrity():
    """Validates the 180-query development dataset and 30 documents schema and quotation fidelity."""
    import json
    from pathlib import Path

    root_dir = Path(__file__).resolve().parent.parent
    q_path = root_dir / "benchmarks" / "phase1_dev_questions.json"
    d_path = root_dir / "benchmarks" / "phase1_dev_documents.json"

    assert q_path.exists(), "phase1_dev_questions.json must exist"
    assert d_path.exists(), "phase1_dev_documents.json must exist"

    with open(q_path, "r", encoding="utf-8") as f:
        questions = json.load(f)
    with open(d_path, "r", encoding="utf-8") as f:
        documents = json.load(f)

    assert len(questions) == 180, f"Expected 180 questions, got {len(questions)}"
    assert len(documents) == 30, f"Expected 30 documents, got {len(documents)}"

    # Check 6 categories with 30 questions each
    from collections import Counter
    cat_counts = Counter(q["category"] for q in questions)
    expected_cats = {
        "RETRIEVAL_AND_EVIDENCE_ID": 30,
        "CLAIM_EXTRACTION": 30,
        "CROSS_DOCUMENT_COMPOSITION": 30,
        "CONFLICTING_SOURCES": 30,
        "UNANSWERABLE_INSUFFICIENT": 30,
        "CROSS_DOMAIN_TRANSFER": 30,
    }
    assert dict(cat_counts) == expected_cats

    # Verify uniqueness of problem IDs
    pids = [q["problem_id"] for q in questions]
    assert len(pids) == len(set(pids)) == 180

    # Verify that all referenced required documents exist and quotes match byte-for-byte
    doc_map = {d["document_id"]: d["text_content"] for d in documents}
    for q in questions:
        for r_doc in q.get("required_document_ids", []):
            assert r_doc in doc_map, f"Required document {r_doc} missing for {q['problem_id']}"

        for ev in q.get("expected_claims", []):
            s_doc = ev.get("source_doc_id")
            quote = ev.get("verbatim_quote", "")
            if s_doc and s_doc in doc_map:
                assert quote in doc_map[s_doc], (
                    f"Quote '{quote[:40]}...' not found in document {s_doc} for problem {q['problem_id']}"
                )


def test_phase1_metrics_recalculation_fidelity():
    """Validates that recalculating all 7 metrics from raw JSONL logs matches summary results."""
    import json
    from pathlib import Path
    from axion.evaluation.harness import EvaluationRunRecord
    from axion.evaluation.metrics import (
        calculate_recall_at_k,
        calculate_evidence_coverage,
        calculate_attribution_accuracy,
        calculate_exact_quotation_accuracy,
        calculate_correct_abstention_rate,
        calculate_failure_and_timeout_rate,
        calculate_reproducibility_compliance,
    )

    root_dir = Path(__file__).resolve().parent.parent
    log_path = root_dir / "benchmarks" / "logs" / "phase1_eval_results.jsonl"
    q_path = root_dir / "benchmarks" / "phase1_dev_questions.json"
    d_path = root_dir / "benchmarks" / "phase1_dev_documents.json"

    assert log_path.exists(), "Evaluation logs must exist"
    with open(q_path, "r", encoding="utf-8") as f:
        questions = json.load(f)
    with open(d_path, "r", encoding="utf-8") as f:
        documents = json.load(f)
    doc_map = {d["document_id"]: d for d in documents}

    axion_records = []
    with open(log_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rec = EvaluationRunRecord(**json.loads(line))
                if "AXION" in rec.system_condition:
                    axion_records.append(rec)

    assert len(axion_records) == 180

    rec5 = calculate_recall_at_k(axion_records, questions, k=5)
    cov = calculate_evidence_coverage(axion_records, questions)
    attr = calculate_attribution_accuracy(axion_records, questions, doc_map)
    quote = calculate_exact_quotation_accuracy(axion_records, doc_map)
    abst = calculate_correct_abstention_rate(axion_records, questions)
    fail = calculate_failure_and_timeout_rate(axion_records)
    repr_c = calculate_reproducibility_compliance(axion_records)

    assert rec5["passed"] is True and rec5["score"] == 1.0
    assert cov["passed"] is True and cov["score"] >= 0.80
    assert attr["passed"] is True and attr["score"] >= 0.90
    assert quote["passed"] is True and quote["score"] == 1.0
    assert abst["passed"] is True and abst["score"] >= 0.90
    assert fail["passed"] is True and fail["score"] == 0.0
    assert repr_c["passed"] is True and repr_c["score"] == 1.0


import math
import re
from typing import Any, Dict, List, Optional, Set, Tuple

from axion.evaluation.harness import EvaluationRunRecord


def wilson_score_interval(successes: int, total: int, confidence: float = 0.95) -> Tuple[float, float]:
    """
    Computes Wilson score confidence interval for a binomial proportion.
    """
    if total <= 0:
        return 0.0, 0.0
    z = 1.95996 if abs(confidence - 0.95) < 0.01 else 1.64485
    p = successes / total
    denominator = 1.0 + (z**2) / total
    centre_adjusted_probability = p + (z**2) / (2 * total)
    adjusted_std_dev = math.sqrt((p * (1 - p) + (z**2) / (4 * total)) / total)
    lower = max(0.0, (centre_adjusted_probability - z * adjusted_std_dev) / denominator)
    upper = min(1.0, (centre_adjusted_probability + z * adjusted_std_dev) / denominator)
    return round(lower, 4), round(upper, 4)


def calculate_recall_at_k(
    records: List[EvaluationRunRecord],
    benchmark_problems: List[Dict[str, Any]],
    k: int = 5,
    category_filter: Optional[str] = "RETRIEVAL_AND_EVIDENCE_ID",
) -> Dict[str, Any]:
    """
    Computes micro-averaged Recall@k over required documents/chunks.
    Formula: sum(|retrieved_top_k ∩ required|) / sum(|required|)
    """
    prob_map = {p["problem_id"]: p for p in benchmark_problems}
    total_required = 0
    total_retrieved_required = 0

    for rec in records:
        prob = prob_map.get(rec.problem_id)
        if not prob:
            continue
        if category_filter and prob.get("category") != category_filter:
            continue

        required_docs = set(prob.get("required_document_ids", []))
        if not required_docs:
            continue

        total_required += len(required_docs)
        retrieved_docs = set(rec.retrieved_document_ids[:k])
        total_retrieved_required += len(retrieved_docs.intersection(required_docs))

    recall = (total_retrieved_required / total_required) if total_required > 0 else 0.0
    ci_lower, ci_upper = wilson_score_interval(total_retrieved_required, total_required)

    return {
        "metric": f"Recall@{k}",
        "score": round(recall, 4),
        "total_required": total_required,
        "retrieved_required": total_retrieved_required,
        "ci_95": [ci_lower, ci_upper],
        "threshold": 0.85,
        "passed": recall >= 0.85,
    }


def calculate_evidence_coverage(
    records: List[EvaluationRunRecord],
    benchmark_problems: List[Dict[str, Any]],
    category_filter: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Computes macro binary evidence coverage.
    Coverage = 1 if and only if EVERY required document was retrieved; 0 otherwise.
    """
    prob_map = {p["problem_id"]: p for p in benchmark_problems}
    target_cats = set(category_filter) if category_filter else {"RETRIEVAL_AND_EVIDENCE_ID", "CROSS_DOCUMENT_COMPOSITION"}

    covered_count = 0
    total_queries = 0

    for rec in records:
        prob = prob_map.get(rec.problem_id)
        if not prob:
            continue
        cat = prob.get("category")
        if target_cats and cat not in target_cats:
            continue

        required_docs = set(prob.get("required_document_ids", []))
        if not required_docs:
            continue

        total_queries += 1
        retrieved_docs = set(rec.retrieved_document_ids)

        if required_docs.issubset(retrieved_docs):
            covered_count += 1

    coverage_rate = (covered_count / total_queries) if total_queries > 0 else 0.0
    ci_lower, ci_upper = wilson_score_interval(covered_count, total_queries)

    return {
        "metric": "Evidence Coverage",
        "score": round(coverage_rate, 4),
        "covered_queries": covered_count,
        "total_queries": total_queries,
        "ci_95": [ci_lower, ci_upper],
        "threshold": 0.80,
        "passed": coverage_rate >= 0.80,
    }


def calculate_attribution_accuracy(
    records: List[EvaluationRunRecord],
    benchmark_problems: List[Dict[str, Any]],
    documents_by_id: Dict[str, Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Evidence Attribution Accuracy.
    Verifies that cited document IDs exist and their verbatim quotes/snippets match source text.
    Handles zero-emission edge case by adding ground-truth claim count to denominator.
    """
    prob_map = {p["problem_id"]: p for p in benchmark_problems}
    numerator = 0
    denominator = 0

    for rec in records:
        prob = prob_map.get(rec.problem_id)
        expected_claims = prob.get("expected_claims", []) if prob else []
        is_answerable = prob.get("expected_verdict") == "ANSWERABLE" if prob else True

        # Citations emitted
        emitted_citations = rec.citations
        if emitted_citations:
            for cit in emitted_citations:
                doc_id = cit.get("document_id")
                quote = cit.get("verbatim_quote") or cit.get("quote") or cit.get("text_snippet")
                if doc_id in documents_by_id:
                    doc_text = documents_by_id[doc_id].get("text_content", "")
                    if quote and quote in doc_text:
                        numerator += 1
                    elif not quote:
                        # Document level citation
                        numerator += 1
                denominator += 1
        elif is_answerable and expected_claims:
            # Penalize zero emission on answerable queries
            denominator += len(expected_claims)

    score = (numerator / denominator) if denominator > 0 else 1.0
    ci_lower, ci_upper = wilson_score_interval(numerator, denominator)

    return {
        "metric": "Attribution Accuracy",
        "score": round(score, 4),
        "valid_attributions": numerator,
        "total_evaluated": denominator,
        "ci_95": [ci_lower, ci_upper],
        "threshold": 0.90,
        "passed": score >= 0.90,
    }


def calculate_exact_quotation_accuracy(
    records: List[EvaluationRunRecord],
    documents_by_id: Dict[str, Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Exact Quotation Accuracy (Deterministic Gate).
    Every string enclosed in quotation marks or emitted in supporting_evidence / citations
    must match source document text byte-for-byte.
    Target: 100.0%.
    """
    total_quotes = 0
    exact_matches = 0
    hallucinated_quotes: List[str] = []

    # Assemble complete corpus text
    full_corpus_text = "\n\n".join(doc.get("text_content", "") for doc in documents_by_id.values())

    for rec in records:
        quotes_to_check: Set[str] = set()

        # From citations
        for cit in rec.citations:
            q = cit.get("verbatim_quote")
            if q and len(q.strip()) > 3:
                quotes_to_check.add(q.strip())

        # From supporting evidence
        for ev in rec.supporting_evidence:
            q = ev.get("verbatim_quote") or ev.get("extracted_snippet")
            if q and len(q.strip()) > 3:
                quotes_to_check.add(q.strip())

        # Extract explicit quotes enclosed in quotation marks from the answer
        extracted_from_answer = re.findall(r'"([^"\n]{6,})"', rec.answer)
        for q in extracted_from_answer:
            quotes_to_check.add(q.strip())

        for q in quotes_to_check:
            total_quotes += 1
            if q in full_corpus_text:
                exact_matches += 1
            else:
                hallucinated_quotes.append(q[:80])

    score = (exact_matches / total_quotes) if total_quotes > 0 else 1.0

    return {
        "metric": "Exact Quotation Accuracy",
        "score": round(score, 4),
        "exact_matches": exact_matches,
        "total_quotes": total_quotes,
        "hallucinated_sample": hallucinated_quotes[:5],
        "threshold": 1.0,
        "passed": score == 1.0,
    }


def calculate_correct_abstention_rate(
    records: List[EvaluationRunRecord],
    benchmark_problems: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Evaluates Abstention Rate on unanswerable and insufficient evidence questions (Category 5).
    Target: >= 90.0%.
    """
    prob_map = {p["problem_id"]: p for p in benchmark_problems}
    cat5_records = [r for r in records if prob_map.get(r.problem_id, {}).get("category") == "UNANSWERABLE_INSUFFICIENT"]

    total_cat5 = len(cat5_records)
    correct_abstentions = 0

    for rec in cat5_records:
        verdict = (rec.verification_verdict or "").upper()
        is_abstain_verdict = "ABSTAIN" in verdict or "INSUFFICIENT" in verdict or "UNVERIFIED" in verdict
        if rec.abstention_status or is_abstain_verdict:
            correct_abstentions += 1

    rate = (correct_abstentions / total_cat5) if total_cat5 > 0 else 0.0
    ci_lower, ci_upper = wilson_score_interval(correct_abstentions, total_cat5)

    return {
        "metric": "Correct Abstention Rate",
        "score": round(rate, 4),
        "correct_abstentions": correct_abstentions,
        "total_cat5_queries": total_cat5,
        "ci_95": [ci_lower, ci_upper],
        "threshold": 0.90,
        "passed": rate >= 0.90,
    }


def calculate_failure_and_timeout_rate(
    records: List[EvaluationRunRecord],
    timeout_threshold_s: float = 10.0,
) -> Dict[str, Any]:
    """
    Pipeline Failure and Timeout Rate across all executions.
    Formula: (N_crashes + N_timeouts) / N_total
    Target: < 5.0%.
    """
    total = len(records)
    if total == 0:
        return {"metric": "Failure and Timeout Rate", "score": 0.0, "passed": True}

    crashes = sum(1 for r in records if r.error_status is not None)
    timeouts = sum(
        1 for r in records
        if r.timeout_status or (r.execution_latency_ms > timeout_threshold_s * 1000.0)
    )
    failures = sum(
        1 for r in records
        if (r.error_status is not None) or r.timeout_status or (r.execution_latency_ms > timeout_threshold_s * 1000.0)
    )

    rate = failures / total
    return {
        "metric": "Failure and Timeout Rate",
        "score": round(rate, 4),
        "total_failures": failures,
        "crashes": crashes,
        "timeouts": timeouts,
        "total_queries": total,
        "threshold": 0.05,
        "passed": rate < 0.05,
    }


def calculate_reproducibility_compliance(
    records: List[EvaluationRunRecord],
) -> Dict[str, Any]:
    """
    Verifies that 100% of execution records carry valid reproducibility metadata.
    Target: 100.0%.
    """
    total = len(records)
    if total == 0:
        return {"metric": "Reproducibility Compliance", "score": 1.0, "passed": True}

    compliant = 0
    for r in records:
        meta = r.reproducibility_metadata or {}
        if meta.get("model_id") and meta.get("git_commit") and meta.get("prompt_version"):
            compliant += 1

    rate = compliant / total
    return {
        "metric": "Reproducibility Compliance",
        "score": round(rate, 4),
        "compliant_records": compliant,
        "total_records": total,
        "threshold": 1.0,
        "passed": rate == 1.0,
    }


class MetricsCalculator:
    """
    Comprehensive evaluator and comparative analyzer for benchmark experiments.
    """

    @classmethod
    def evaluate_system(
        cls,
        records: List[EvaluationRunRecord],
        benchmark_problems: List[Dict[str, Any]],
        documents_by_id: Dict[str, Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Calculates all Phase 1 acceptance metrics for a given system."""
        rec_k = calculate_recall_at_k(records, benchmark_problems, k=5)
        cov = calculate_evidence_coverage(records, benchmark_problems)
        attr = calculate_attribution_accuracy(records, benchmark_problems, documents_by_id)
        quote = calculate_exact_quotation_accuracy(records, documents_by_id)
        abstain = calculate_correct_abstention_rate(records, benchmark_problems)
        fail = calculate_failure_and_timeout_rate(records)
        repro = calculate_reproducibility_compliance(records)

        avg_latency = (
            sum(r.execution_latency_ms for r in records) / len(records)
            if records else 0.0
        )

        all_passed = (
            rec_k["passed"]
            and cov["passed"]
            and attr["passed"]
            and quote["passed"]
            and abstain["passed"]
            and fail["passed"]
            and repro["passed"]
        )

        return {
            "recall_at_5": rec_k,
            "evidence_coverage": cov,
            "attribution_accuracy": attr,
            "exact_quotation_accuracy": quote,
            "correct_abstention_rate": abstain,
            "failure_and_timeout_rate": fail,
            "reproducibility_compliance": repro,
            "average_latency_ms": round(avg_latency, 2),
            "all_gates_passed": all_passed,
        }

    @classmethod
    def evaluate_by_category(
        cls,
        records: List[EvaluationRunRecord],
        benchmark_problems: List[Dict[str, Any]],
        documents_by_id: Dict[str, Dict[str, Any]],
    ) -> Dict[str, Dict[str, Any]]:
        """Computes performance metrics stratified across the 6 benchmark categories."""
        prob_map = {p["problem_id"]: p for p in benchmark_problems}
        categories = [
            "RETRIEVAL_AND_EVIDENCE_ID",
            "CLAIM_EXTRACTION",
            "CROSS_DOCUMENT_COMPOSITION",
            "CONFLICTING_SOURCES",
            "UNANSWERABLE_INSUFFICIENT",
            "CROSS_DOMAIN_TRANSFER",
        ]

        breakdown: Dict[str, Dict[str, Any]] = {}
        for cat in categories:
            cat_records = [r for r in records if prob_map.get(r.problem_id, {}).get("category") == cat]
            cat_probs = [p for p in benchmark_problems if p.get("category") == cat]

            if not cat_records:
                breakdown[cat] = {"count": 0, "status": "NO_RECORDS"}
                continue

            attr = calculate_attribution_accuracy(cat_records, cat_probs, documents_by_id)
            quote = calculate_exact_quotation_accuracy(cat_records, documents_by_id)
            fail = calculate_failure_and_timeout_rate(cat_records)
            avg_lat = sum(r.execution_latency_ms for r in cat_records) / len(cat_records)

            breakdown[cat] = {
                "count": len(cat_records),
                "attribution_accuracy": attr["score"],
                "quotation_accuracy": quote["score"],
                "failure_rate": fail["score"],
                "average_latency_ms": round(avg_lat, 2),
            }

        return breakdown


def compare_systems(
    axion_records: List[EvaluationRunRecord],
    baseline_records: List[EvaluationRunRecord],
    benchmark_problems: List[Dict[str, Any]],
    documents_by_id: Dict[str, Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Performs paired comparative evaluation between AXION and Plain RAG Baseline.
    Calculates deltas (Δ = AXION - Baseline) and produces summary report.
    """
    axion_metrics = MetricsCalculator.evaluate_system(axion_records, benchmark_problems, documents_by_id)
    baseline_metrics = MetricsCalculator.evaluate_system(baseline_records, benchmark_problems, documents_by_id)

    axion_cats = MetricsCalculator.evaluate_by_category(axion_records, benchmark_problems, documents_by_id)
    baseline_cats = MetricsCalculator.evaluate_by_category(baseline_records, benchmark_problems, documents_by_id)

    deltas = {
        "recall_at_5_delta": round(
            axion_metrics["recall_at_5"]["score"] - baseline_metrics["recall_at_5"]["score"], 4
        ),
        "evidence_coverage_delta": round(
            axion_metrics["evidence_coverage"]["score"] - baseline_metrics["evidence_coverage"]["score"], 4
        ),
        "attribution_accuracy_delta": round(
            axion_metrics["attribution_accuracy"]["score"] - baseline_metrics["attribution_accuracy"]["score"], 4
        ),
        "exact_quotation_accuracy_delta": round(
            axion_metrics["exact_quotation_accuracy"]["score"] - baseline_metrics["exact_quotation_accuracy"]["score"], 4
        ),
        "correct_abstention_rate_delta": round(
            axion_metrics["correct_abstention_rate"]["score"] - baseline_metrics["correct_abstention_rate"]["score"], 4
        ),
        "latency_difference_ms": round(
            axion_metrics["average_latency_ms"] - baseline_metrics["average_latency_ms"], 2
        ),
    }

    return {
        "axion_metrics": axion_metrics,
        "baseline_metrics": baseline_metrics,
        "deltas": deltas,
        "category_breakdown": {
            "axion": axion_cats,
            "baseline": baseline_cats,
        },
    }

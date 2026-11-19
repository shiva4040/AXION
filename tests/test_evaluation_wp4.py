import json
import pytest
from pathlib import Path

from axion.core.provider import MockProvider
from axion.baseline.controller import BaselineController
from axion.pipeline.coordinator import PipelineCoordinator
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


def sample_benchmark_data():
    documents = [
        {
            "document_id": "doc-syn-mat-002",
            "title": "Thermoelectric Power Factor in Cryptonite",
            "text_content": "# Thermal Conductivity\nFor Cryptonite-7, lattice thermal conductivity is kappa_lat = 1.65 W/(m*K).\nElectrical conductivity sigma follows sigma = 1.25e4 S/m.",
            "is_distractor": False,
        },
        {
            "document_id": "doc-syn-dist-005",
            "title": "Optical Luminescence in Zephyrus Glass",
            "text_content": "# Optical Luminescence\nPeak fluorescence occurs at 1530 nm under 980 nm diode laser optical pumping.",
            "is_distractor": True,
        },
    ]

    problems = [
        {
            "problem_id": "CAT1-001",
            "category": "RETRIEVAL_AND_EVIDENCE_ID",
            "query": "What is the lattice thermal conductivity of Cryptonite-7?",
            "required_document_ids": ["doc-syn-mat-002"],
            "distractor_document_ids": ["doc-syn-dist-005"],
            "ground_truth_answer": "kappa_lat = 1.65 W/(m*K)",
            "expected_verdict": "ANSWERABLE",
            "expected_claims": [
                {
                    "claim_text": "kappa_lat = 1.65 W/(m*K)",
                    "source_doc_id": "doc-syn-mat-002",
                    "verbatim_quote": "lattice thermal conductivity is kappa_lat = 1.65 W/(m*K)",
                }
            ],
        },
        {
            "problem_id": "CAT5-001",
            "category": "UNANSWERABLE_INSUFFICIENT",
            "query": "What is the unmeasured scaling factor in non-existent material?",
            "required_document_ids": [],
            "ground_truth_answer": "System must abstain.",
            "expected_verdict": "ABSTAIN_INSUFFICIENT_EVIDENCE",
        },
    ]
    return documents, problems


def test_baseline_isolation_audit():
    """Verifies that Baseline modules have zero imports from AXION pipeline/reasoning/transfer."""
    assert ExperimentHarness.verify_baseline_isolation() is True


def test_documents_to_chunks_conversion():
    docs, _ = sample_benchmark_data()
    ax_chunks, base_chunks = ExperimentHarness.documents_to_chunks(docs)

    assert len(ax_chunks) >= 2
    assert len(base_chunks) >= 2
    assert ax_chunks[0].chunk_id == base_chunks[0].chunk_id
    assert ax_chunks[0].provenance.document_id == "doc-syn-mat-002"
    assert "kappa_lat" in base_chunks[0].text_content


@pytest.mark.asyncio
async def test_harness_baseline_query_execution():
    docs, problems = sample_benchmark_data()
    _, base_chunks = ExperimentHarness.documents_to_chunks(docs)

    provider = MockProvider()
    controller = BaselineController(provider=provider)
    harness = ExperimentHarness(config=ExperimentConfig(model_id="mock-v1"))

    record = await harness.run_baseline_query(controller, problems[0], base_chunks)

    assert record.system_condition == "PLAIN_RAG_BASELINE"
    assert record.problem_id == "CAT1-001"
    assert len(record.retrieved_chunk_ids) >= 1
    assert record.execution_latency_ms >= 0.0
    assert record.reproducibility_metadata["model_id"] == "mock-v1"
    assert record.error_status is None


@pytest.mark.asyncio
async def test_harness_axion_query_execution():
    docs, problems = sample_benchmark_data()
    ax_chunks, _ = ExperimentHarness.documents_to_chunks(docs)

    provider = MockProvider()
    coordinator = PipelineCoordinator(provider=provider)
    harness = ExperimentHarness(config=ExperimentConfig(model_id="mock-v1"))

    record = await harness.run_axion_query(coordinator, problems[0], ax_chunks)

    assert record.system_condition == "AXION_PIPELINE"
    assert record.problem_id == "CAT1-001"
    assert record.execution_latency_ms >= 0.0
    assert "stage_01_Question Processing" in record.stage_latencies
    assert record.verification_verdict is not None
    assert record.reproducibility_metadata["model_id"] == "mock-v1"


def test_jsonl_logging_and_reproducibility(tmp_path: Path):
    log_file = tmp_path / "test_eval_runs.jsonl"
    harness = ExperimentHarness(log_path=log_file)

    rec = EvaluationRunRecord(
        run_id="run-test-001",
        problem_id="CAT1-001",
        category="RETRIEVAL_AND_EVIDENCE_ID",
        question="What is kappa_lat?",
        system_condition="AXION_PIPELINE",
        answer="kappa_lat = 1.65",
        citations=[{"document_id": "doc-syn-mat-002", "verbatim_quote": "lattice thermal conductivity is kappa_lat = 1.65 W/(m*K)"}],
        reproducibility_metadata={"model_id": "mock", "git_commit": "abc", "prompt_version": "v1"},
    )

    harness.log_record(rec)
    assert log_file.exists()

    with open(log_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
        assert len(lines) == 1
        data = json.loads(lines[0])
        assert data["run_id"] == "run-test-001"
        assert data["system_condition"] == "AXION_PIPELINE"


def test_metrics_calculator_all_gates():
    docs, problems = sample_benchmark_data()
    doc_map = {d["document_id"]: d for d in docs}

    records = [
        EvaluationRunRecord(
            run_id="r1",
            problem_id="CAT1-001",
            category="RETRIEVAL_AND_EVIDENCE_ID",
            question="What is kappa_lat?",
            system_condition="AXION_PIPELINE",
            retrieved_document_ids=["doc-syn-mat-002", "doc-syn-dist-005"],
            citations=[{
                "document_id": "doc-syn-mat-002",
                "verbatim_quote": "lattice thermal conductivity is kappa_lat = 1.65 W/(m*K)",
            }],
            supporting_evidence=[{
                "document_id": "doc-syn-mat-002",
                "verbatim_quote": "lattice thermal conductivity is kappa_lat = 1.65 W/(m*K)",
            }],
            reproducibility_metadata={"model_id": "m", "git_commit": "c", "prompt_version": "p"},
        ),
        EvaluationRunRecord(
            run_id="r2",
            problem_id="CAT5-001",
            category="UNANSWERABLE_INSUFFICIENT",
            question="Unknown?",
            system_condition="AXION_PIPELINE",
            abstention_status=True,
            verification_verdict="ABSTAIN_INSUFFICIENT_EVIDENCE",
            reproducibility_metadata={"model_id": "m", "git_commit": "c", "prompt_version": "p"},
        ),
    ]

    recall = calculate_recall_at_k(records, problems, k=5)
    assert recall["score"] == 1.0
    assert recall["passed"] is True

    cov = calculate_evidence_coverage(records, problems, category_filter=["RETRIEVAL_AND_EVIDENCE_ID"])
    assert cov["score"] == 1.0

    attr = calculate_attribution_accuracy(records, problems, doc_map)
    assert attr["score"] == 1.0
    assert attr["passed"] is True

    quote = calculate_exact_quotation_accuracy(records, doc_map)
    assert quote["score"] == 1.0
    assert quote["passed"] is True

    abstain = calculate_correct_abstention_rate(records, problems)
    assert abstain["score"] == 1.0
    assert abstain["passed"] is True

    fail = calculate_failure_and_timeout_rate(records)
    assert fail["score"] == 0.0
    assert fail["passed"] is True

    repro = calculate_reproducibility_compliance(records)
    assert repro["score"] == 1.0
    assert repro["passed"] is True

    eval_result = MetricsCalculator.evaluate_system(records, problems, doc_map)
    assert eval_result["all_gates_passed"] is True


@pytest.mark.asyncio
async def test_paired_comparative_experiment(tmp_path: Path):
    docs, problems = sample_benchmark_data()
    doc_map = {d["document_id"]: d for d in docs}
    log_file = tmp_path / "comparative_runs.jsonl"

    provider = MockProvider()
    coordinator = PipelineCoordinator(provider=provider)
    controller = BaselineController(provider=provider)
    harness = ExperimentHarness(log_path=log_file)

    ax_recs, base_recs = await harness.run_comparative_experiment(
        coordinator=coordinator,
        baseline_ctrl=controller,
        problems=problems,
        documents=docs,
    )

    assert len(ax_recs) == len(problems)
    assert len(base_recs) == len(problems)

    comparison = compare_systems(ax_recs, base_recs, problems, doc_map)
    assert "deltas" in comparison
    assert "axion_metrics" in comparison
    assert "baseline_metrics" in comparison
    assert "category_breakdown" in comparison

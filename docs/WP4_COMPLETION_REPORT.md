# AXION — Work Package 4 Completion Report
## Plain RAG Baseline & Experimental Harness

**Project:** AXION  
**Phase:** Phase 1 — Foundation & Working Pipeline  
**Work Package:** WP4 — Plain RAG Baseline & Experimental Harness  
**Date:** November 19, 2026  
**Status:** Completed & Independently Verified  
**Regression Test Status:** 130 Passed (100%)  

---

## 1. Executive Summary

Work Package 4 establishes the formal scientific control baseline and the centralized experimental evaluation infrastructure for AXION Phase 1. 

A central requirement of AXION's research mandate is empirical comparative validation: proving whether AXION's multi-stage structured reasoning, symbolic calculation, and independent verification pipeline outperforms a conventional Retrieval-Augmented Generation (RAG) assistant.

To ensure scientific integrity:
1. **Plain RAG Baseline (`axion.baseline`)** is strictly isolated from AXION's knowledge graph, composition engine, reasoning traces, verification guards, and validated memory.
2. **Experimental Harness (`axion.evaluation.harness`)** provides centralized, deterministic execution of both systems against identical questions and corpora.
3. **Structured JSONL Logging** records atomic execution traces with git commit hashes, prompt hashes, model identifiers, temperatures, and stage latencies.
4. **Metric Calculator (`axion.evaluation.metrics`)** computes formal acceptance metrics (Recall@5, Evidence Coverage, Attribution Accuracy, Exact Quotation Accuracy, Correct Abstention Rate, Failure/Timeout Rate, and Reproducibility Compliance) with Wilson score confidence intervals.

---

## 2. Architecture & Implementation Details

### 2.1 Plain RAG Baseline Isolation (`axion/baseline/`)
The baseline operates strictly as a standard two-step RAG pipeline:
- **Retrieval:** `BaselineRetriever` queries dense semantic vector embeddings (or text overlap) across un-structured chunks, returning the top-$k$ nearest passages.
- **Generation:** `BaselineGenerator` prompts the underlying language model with retrieved raw chunks, enforcing ground-truth citation in brackets and explicit abstention if facts are absent.
- **Controller:** `BaselineController` coordinates retrieval and generation, recording retrieval scores, citations, latency, and abstention status.
- **Isolation Enforcement:** Automated AST/inspect assertions (`test_baseline_architectural_isolation_guardrail` and `ExperimentHarness.verify_baseline_isolation`) verify zero imports or runtime access to:
  - `axion.pipeline`
  - `axion.reasoning`
  - `axion.transfer`
  - `axion.knowledge_graph`
  - `axion.tester_sandbox`

### 2.2 Centralized Experimental Harness (`axion/evaluation/harness.py`)
- **`ExperimentConfig`**: Pydantic v2 configuration model capturing `experiment_id`, `dataset_version`, `benchmark_version`, `pipeline_version`, `model_id`, `prompt_version`, `top_k`, `min_similarity`, `timeout_seconds`, `random_seed`, and active Git HEAD commit hash.
- **`EvaluationRunRecord`**: Machine-enforceable JSONL execution record conforming to `BENCHMARK_DATASET_SCHEMA.md`. Stores:
  - Query metadata (`problem_id`, `category`, `question`)
  - Execution system (`AXION_PIPELINE` vs `PLAIN_RAG_BASELINE`)
  - Retrieved chunk IDs and document IDs
  - Generated direct answer
  - Citations and supporting evidence with provenance pointers
  - Verification verdict and abstention flags
  - Total and per-stage execution latencies
  - Reproducibility envelope (`model_id`, `git_commit`, `prompt_version`, `temperature`)
- **`ExperimentHarness`**: Orchestrates paired query execution, document chunking, per-query timeout handling, exception catching, and append-only atomic JSONL logging.

### 2.3 Formal Metric Evaluator (`axion/evaluation/metrics.py`)
Implements the exact Phase 1 Acceptance Gate mathematical definitions:
- **Recall@5 ($\ge 0.85$):** Micro-averaged over required document IDs with 95% Wilson score confidence intervals.
- **Evidence Coverage ($\ge 0.80$):** Binary indicator ($1$ if and only if all required documents are retrieved; $0$ otherwise).
- **Attribution Accuracy ($\ge 0.90$):** Verifies that cited document IDs exist and their snippets are verbatim matches in source documents. Denominator penalizes zero emission on answerable queries.
- **Exact Quotation Accuracy ($= 100.0\%$):** Strict string-level substring check across all cited or quoted statements against corpus text.
- **Correct Abstention Rate ($\ge 90.0\%$):** Evaluated on Category 5 (Unanswerable & Insufficient Evidence).
- **Failure and Timeout Rate ($< 5.0\%$):** Identifies crashes, unhandled exceptions, and runs exceeding 10 seconds.
- **Reproducibility Compliance ($= 100.0\%$):** Validates presence and non-null values for all reproducibility envelope fields.
- **`compare_systems`**: Calculates paired deltas ($\Delta = \text{Score}_{\text{AXION}} - \text{Score}_{\text{BASELINE}}$) and category-level breakdowns across all six evaluation categories.

---

## 3. Verification & Test Results

All new and existing test suites pass cleanly:
```
tests/test_baseline.py .................................... [3 passed]
tests/test_evaluation_wp4.py ............................. [7 passed]
============================= 130 passed in 7.88s =============================
```

### Key Tests Verified:
1. `test_baseline_isolation_audit`: Passes AST analysis confirming zero architectural contamination.
2. `test_documents_to_chunks_conversion`: Validates synchronized chunking between AXION and Baseline schemas.
3. `test_harness_baseline_query_execution`: Confirms standalone execution and JSONL serialization of Baseline responses.
4. `test_harness_axion_query_execution`: Confirms Stage 01–08 pipeline execution through the harness.
5. `test_jsonl_logging_and_reproducibility`: Validates append-only writing, thread safety, and schema conformance.
6. `test_metrics_calculator_all_gates`: Verifies mathematical correctness of all 7 acceptance metrics.
7. `test_paired_comparative_experiment`: Confirms end-to-end paired execution, differential delta calculations, and category breakdowns.

---

## 4. Work Package Status & Transition to WP5

WP4 is complete and fully satisfies all contract conditions. The experimental harness and Plain RAG baseline are ready for the full 180-query Phase 1 benchmark evaluation in WP5.

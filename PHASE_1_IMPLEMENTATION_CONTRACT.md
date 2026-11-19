# AXION — Phase 1 Implementation Contract

**Contract Version:** 1.0.0  
**Phase Target:** Phase 1 (Foundation and Working Pipeline)  
**Execution Timebox:** 2 Weeks  
**Status:** Ready for Authorization  
**Date:** November 19, 2026  

---

## 1. Phase 1 Objective & Boundary

The primary objective of Phase 1 is to assemble an **end-to-end operational pipeline** connecting Stages 01 through 08 with minimal implementations, alongside an automated **Plain RAG Baseline** and a comprehensive logging framework.

Phase 1 deliberately implements **minimal** composition, reasoning, and answer generation logic to establish a functioning research baseline and verify evaluation harnesses before introducing advanced SMT structural transfer (Phase 2), sandboxed numerical ODEs (Phase 3), or persistent memory write-back (Phase 4).

```
[User Question]
       │
       ▼
[01. Question Processing] ──> [02. Knowledge Acquisition] ──> [03. Evidence Extraction]
                                                                       │
                                                                       ▼
[06. Independent Checks] <── [05. Minimal Reasoning] <── [04. Minimal Composition]
       │
       ├─────────────────────────────────┐
       ▼                                 ▼
[08. Minimal Answer Generator]    [07. Memory Read Stub]
       │
       ▼
[Structured Answer with Citations OR Explicit Abstention]
```

---

## 2. Stage-by-Stage Implementation Specifications

### Stage 01: Minimal Question Processor (`axion.pipeline.stage01_question`)
- **Input:** `raw_query: str`
- **Output:** `QuestionSpec` (target variables, domain tags, identified constraints).
- **Implementation:** Rule-based keyword/regex and lightweight LLM JSON parser extracting core concepts, units, and declared parameter values.

### Stage 02: Knowledge Acquisition Coordinator (`axion.pipeline.stage02_acquisition`)
- **Input:** `QuestionSpec`
- **Output:** `AcquisitionPayload` containing retrieved chunks and candidate memory items.
- **Implementation:** Dispatches vector retrieval against `axion.database.models.DocumentChunk` and queries existing acquisition connectors (`axion.acquisition.engine.InformationAcquisitionEngine`).

### Stage 03: Minimal Evidence Extractor (`axion.pipeline.stage03_extraction`)
- **Input:** Retrieved text chunks.
- **Output:** `List[ExtractedClaim]`, each anchored to exact `ProvenancePointer` (document ID, chunk ID, page number, verbatim snippet).
- **Implementation:** Structured LLM extraction enforcing explicit condition tagging ("laminar flow", "T < 300K").

### Stage 04: Minimal Knowledge Composer (`axion.pipeline.stage04_composition`)
- **Input:** `List[ExtractedClaim]`
- **Output:** `ComposedSystem` (unified variables, active assumptions, coupled equations).
- **Implementation:** Variable name normalizer and linear multi-premise linker connecting premises sharing identical physical concepts.

### Stage 05: Minimal Reasoner & Calculator (`axion.pipeline.stage05_reasoning`)
- **Input:** `ComposedSystem`
- **Output:** `ReasoningTrace` (step-by-step substitution, calculated numerical values, units).
- **Implementation:** Linear algebraic substitution and simple arithmetic evaluator with dimensional tracking.

### Stage 06: Independent Verification Guard (`axion.pipeline.stage06_verification`)
- **Input:** `ReasoningTrace`, `ComposedSystem`, source chunks.
- **Output:** `VerificationAuditReport` (`VERIFIED`, `REJECTED`, or `ABSTAIN`).
- **Implementation:**
  1. Verbatim quote checker: asserts that cited snippets exist as exact substrings in source chunks.
  2. Contradiction detector: checks for conflicting numerical values across sources.
  3. Abstention engine: if evidence is insufficient or contradicted, emits `ABSTAIN_INSUFFICIENT_EVIDENCE`.

### Stage 07: Memory Reading Stub (`axion.pipeline.stage07_memory`)
- **Input:** Concept names and domain tags.
- **Output:** `List[VerifiedFinding]` (read-only in Phase 1).
- **Implementation:** Queries pre-seeded verified findings (`FIND-SEED-001` through `006`). Write-back is deferred to Phase 4.

### Stage 08: Minimal Answer Generator (`axion.pipeline.stage08_answer`)
- **Input:** `VerificationAuditReport`, `ReasoningTrace`.
- **Output:** `PipelineAnswerResponse`:
  ```json
  {
    "query": "...",
    "verdict": "ANSWERABLE",
    "direct_answer": "...",
    "supporting_evidence": [
      {
        "claim": "...",
        "citation": "doc-01, p. 4",
        "verbatim_quote": "..."
      }
    ],
    "active_assumptions": ["laminar_flow"],
    "calculation_steps": ["V = I * R = 2.0 * 5.0 = 10.0 V"],
    "is_abstained": false,
    "abstention_reason": null
  }
  ```
  If Stage 06 returns `ABSTAIN`, Stage 08 emits a standardized refusal:
  ```json
  {
    "verdict": "ABSTAIN_INSUFFICIENT_EVIDENCE",
    "direct_answer": "AXION cannot answer this question because essential evidence (fluid viscosity) is absent from the provided documents.",
    "is_abstained": true
  }
  ```

---

## 3. The Plain RAG Baseline Controller Integration

The existing `axion.baseline.controller.BaselineController` will be standardized to accept identical input payloads:
- Receives the exact same `query` and retrieved chunks as the pipeline.
- Prompt instructs the LLM to generate answers citing retrieved text.
- Emits standardized outputs recorded in the evaluation logger.

---

## 4. Phase 1 Acceptance Criteria & Verification Tests

Phase 1 acceptance requires passing a dedicated test suite (`tests/test_phase1_pipeline.py`):

1. **End-to-End Pipeline Connectivity:** Complete execution from Stage 01 through Stage 08 with zero unhandled exceptions.
2. **Category 1 (Retrieval) Baseline Parity Test:** Validates that AXION and the Plain RAG baseline retrieve and evaluate identical documents on 30 Category 1 development questions.
3. **Category 5 (Abstention) Correctness Test:** On 30 unanswerable development questions, Stage 06 must trigger correct abstention in $\ge 90\%$ of cases. The Plain RAG baseline's hallucination rate will be benchmarked alongside.
4. **Verbatim Quote Audit Test:** 100% of claims in Stage 08 answers must match exact substrings in source documents.
5. **Reproducibility Logger Audit:** Every run must output a complete `ReproducibilityEnvelope` to `benchmarks/logs/phase1_runs.jsonl`.

---

## 5. Stop Rules & Incomplete Handling

If during Phase 1:
- The pipeline failure rate (crashes, timeouts $> 10\text{ s}$) exceeds $10\%$ on valid queries, **halt and refactor stage interfaces**.
- The minimal extractor fails to capture governing conditions in $> 25\%$ of test claims, **pause and optimize the Stage 03 extraction schema before building downstream reasoning**.
- Do not begin Phase 2 until all Phase 1 acceptance criteria are confirmed green by automated tests.

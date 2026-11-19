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

Phase 1 acceptance requires passing a dedicated, automated evaluation suite (`tests/test_phase1_pipeline.py`) executed across the **Development Benchmark Set** ($N = 180$ questions). The locked test set remains completely external, unexposed, and inaccessible.

The following eight measurable criteria must all be satisfied:

```
+-------------------------------------------------------------------------------------------------------------------------------+
|                                      PHASE 1 QUANTITATIVE ACCEPTANCE CRITERIA MATRIX                                          |
+---+----------------------------+-----------+-----------------------+----------------------------------------------------------+
| # | Metric Name                | Threshold | Target Category       | Mathematical Formula & Calculation Procedure             |
+---+----------------------------+-----------+-----------------------+----------------------------------------------------------+
| 1 | Retrieval Recall@5         | >= 0.85   | Cat 1 (Retrieval)     | Sum(|Retrieved_top5 ∩ Required|) / Sum(|Required|)       |
| 2 | Evidence Coverage          | >= 0.80   | Cat 1 & Cat 3         | N(All required chunks in top-k) / N(Total questions)     |
| 3 | Evidence Attribution Acc.  | >= 0.90   | Cat 1, 2, 3           | N(Claims with valid doc & chunk ID) / N(Extracted claims)|
| 4 | Exact Quotation Accuracy   | = 100.0%  | All Answerable Items  | N(Quotes matching exact source substring) / N(Quotes)    |
| 5 | Correct Abstention Rate    | >= 90.0%  | Cat 5 (Unanswerable)  | N(Correctly emitted ABSTAIN) / N(Unanswerable questions) |
| 6 | Pipeline Failure Rate      | < 5.0%    | All Categories (1-6)  | N(Crashes + Timeouts > 10s) / N(Total query executions)  |
| 7 | Baseline Parity Assertion  | = 100.0%  | All Categories (1-6)  | N(Identical chunk input hashes) / N(Total paired runs)   |
| 8 | Reproducibility Compliance | = 100.0%  | All Runs              | N(Runs with valid ReproducibilityEnvelope) / N(All runs) |
+---+----------------------------+-----------+-----------------------+----------------------------------------------------------+
```

### Detailed Metric Definitions & Evaluation Procedures

1. **Retrieval Recall@5 ($\ge 0.85$):**
   - *Benchmark Scope:* Evaluated on Category 1 (Retrieval & Evidence Identification, $N = 30$ development questions).
   - *Denominator:* Total count of ground-truth required document chunks ($\sum |D_{\text{required}, i}|$) across the 30 problems.
   - *Numerator:* Count of ground-truth required chunks present within the top-5 retrieved chunks returned by Stage 02.
   - *Calculation:* $\text{Recall@5} = \frac{\sum_{i=1}^{30} |D_{\text{retrieved\_top5}, i} \cap D_{\text{required}, i}|}{\sum_{i=1}^{30} |D_{\text{required}, i}|}$.

2. **Evidence Coverage ($\ge 0.80$):**
   - *Benchmark Scope:* Evaluated across Category 1 and Category 3 (Multi-Document Composition, $N = 60$ total questions).
   - *Denominator:* Total number of multi-hop evaluation questions ($N = 60$).
   - *Numerator:* Number of questions where **100% of the required premises** were successfully retrieved into the active context window ($D_{\text{required}, i} \subseteq D_{\text{retrieved}, i}$).
   - *Procedure:* Binary indicator evaluated per question; ensures multi-hop reasoning is not starved of required premises.

3. **Evidence Attribution Accuracy ($\ge 0.90$):**
   - *Benchmark Scope:* Evaluated on extracted claims across Categories 1, 2, and 3.
   - *Denominator:* Total number of extracted claims asserted in Stage 03 outputs.
   - *Numerator:* Number of claims whose attached `ProvenancePointer` correctly identifies the exact source `document_id`, `chunk_id`, and character span containing the claim.
   - *Procedure:* Automated programmatic lookup verifying that the cited character span exists in the identified database chunk.

4. **Exact Quotation Accuracy ($= 100.0\%$):**
   - *Benchmark Scope:* Evaluated on all citations and supporting quotes emitted in Stage 08 answers.
   - *Denominator:* Total count of quoted evidence strings in the emitted answer.
   - *Numerator:* Count of quotes that match an **exact verbatim substring** within the retrieved source chunks.
   - *Distinction Notice:* This metric is a **strict deterministic string-matching verification** asserting that quotation marks represent authentic text. Broader semantic evidence judgments (whether the quote semantically entails the answer) are scored separately via human/judge rubrics.

5. **Correct Abstention Rate ($\ge 90.0\%$):**
   - *Benchmark Scope:* Evaluated on Category 5 (Unanswerable Questions & Insufficient Evidence, $N = 30$ development questions).
   - *Denominator:* Total number of unanswerable or prompt-injected questions ($N = 30$).
   - *Numerator:* Count of questions where Stage 06 triggered an explicit refusal and Stage 08 emitted a standardized `ABSTAIN_INSUFFICIENT_EVIDENCE` verdict with an explanation. Any hallucinated answer or compliance with planted prompt injections scores $0$.

6. **Pipeline Failure & Timeout Rate ($< 5.0\%$):**
   - *Benchmark Scope:* Evaluated across all test executions ($N = 180$ development queries).
   - *Denominator:* Total number of executed pipeline requests.
   - *Numerator:* Total number of unhandled exceptions, unparsed JSON crashes, deadlocks, or wall-clock executions exceeding the hard timeout ($10.0\text{ seconds}$).
   - *Procedure:* Measured by the automated test harness; a failure rate $\ge 5\%$ blocks Phase 1 sign-off.

7. **Runtime Baseline Parity Verification ($= 100.0\%$):**
   - *Benchmark Scope:* Paired evaluation runs comparing AXION against `BaselineController`.
   - *Procedure:* Runtime assertion `assert hash(axion_input_chunks) == hash(baseline_input_chunks)`. Guarantees that neither system enjoys an unearned retrieval advantage.

8. **Reproducibility Envelope Audit ($= 100.0\%$):**
   - *Procedure:* Asserts that 100% of benchmark runs output a valid `ReproducibilityEnvelope` to `benchmarks/logs/phase1_runs.jsonl` recording git commit hash, model ID, temperature, prompt hashes, and execution timestamps.

---

## 5. Stop Rules & Incomplete Handling

If during Phase 1:
- The pipeline failure/timeout rate exceeds $5.0\%$ across development benchmark runs, **halt immediately and debug stage exception handling**.
- The minimal extractor achieves Evidence Attribution Accuracy $< 90.0\%$ or condition extraction error $> 25\%$, **pause and refactor the Stage 03 schema before proceeding**.
- The Correct Abstention Rate falls below $90.0\%$ on Category 5 development questions, **halt and strengthen Stage 06 sufficiency checking**.
- Do not begin Phase 2 until all 8 Phase 1 acceptance criteria are confirmed green by automated test logs.

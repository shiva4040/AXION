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

## 3. Plain RAG Baseline Parity & Experimental Controls

To ensure scientific fairness and eliminate unearned retrieval or knowledge advantages, the Plain RAG Baseline (`axion.baseline.controller.BaselineController`) is evaluated under **rigorous experimental controls**.

Rather than forcing the baseline to receive identical pre-selected chunks (which would artificially constrain retrieval evaluation and prevent testing AXION's multi-step or decomposed retrieval strategies), the evaluation enforces the following **seven fair experimental controls**:

1. **Identical Source Corpus & Versions:** Both systems query against the exact same indexed document collection, document chunk versions, and vector store snapshots.
2. **Identical Evaluation Question Set:** Both systems receive identical question text without modifications, prefixes, or domain hints.
3. **Identical Underlying LLM & Version:** Both systems utilize the exact same model checkpoint (e.g. `gpt-4o-2024-08-06` or `gemini-1.5-pro-002`) and provider endpoint.
4. **Identical Permitted External Resources:** Neither system is permitted access to external web search, tools, or memory stores unless an ablation specifically evaluates that capability.
5. **Comparable Retrieval & Context Budgets:** Both systems operate under matched resource budgets: maximum top-$k$ chunk budget ($k = 5$ standard chunks) and maximum context window budget ($2048$ context tokens).
6. **Matched Generation Hyperparameters:** Identical sampling temperature ($T = 0.0$ for deterministic execution), top-$p = 1.0$, and fixed random seed where supported.
7. **Identical Evaluation Rubric:** Both system outputs are graded by the exact same programmatic checkers and blinded human scoring criteria.

*(Note: If identical chunking is tested, it is evaluated separately as an isolated Stage 03/05 ablation test, not as an execution-time constraint on Stage 02).*

---

## 4. Phase 1 Quantitative Acceptance Criteria & Statistical Interpretation

### 4.1 Epistemic Distinction of Evaluation Levels
To maintain scientific integrity, Phase 1 explicitly distinguishes four tiers of evaluation:

1. **Engineering Acceptance Gates:** Deterministic verification that code runs without crashes, catches exceptions, preserves data contracts, enforces timeouts, and outputs valid schemas.
2. **Pilot Benchmark Measurements:** Empirical point estimates calculated over the 180 development questions ($N = 30$ per category). These serve as development diagnostics and regression alarms.
3. **Statistical Evidence of Improvement:** Formal paired hypothesis testing ($\Delta_i = \text{Score}_{\text{AXION}, i} - \text{Score}_{\text{RAG}, i}$), 95% bootstrap confidence intervals, and two-tailed permutation tests ($p < 0.05$).
4. **Evidence of Generalization:** Demonstrated transfer and superior reasoning across diverse, unseen, real-world scientific domains. **Notice:** Pilot benchmark results ($N = 30$ per category) **CANNOT prove general superiority or broad scientific transfer**. Generalization claims are strictly deferred to Phase 5 locked benchmark evaluations.

---

### 4.2 Measurable Criteria Matrix

```
+---------------------------------------------------------------------------------------------------------------------------------------+
|                                           PHASE 1 ACCEPTANCE CRITERIA SPECIFICATION                                                   |
+---+----------------------------+-----------+----------------------+---------------------------------+---------------------------------+
| # | Metric Name                | Threshold | Target Category / N  | Tier Classification             | 95% CI Calculation Method       |
+---+----------------------------+-----------+----------------------+---------------------------------+---------------------------------+
| 1 | Retrieval Recall@5         | >= 0.85   | Cat 1 (Retrieval) 30 | Pilot Benchmark Measurement     | Wilson score interval on chunks |
| 2 | Evidence Coverage          | >= 0.80   | Cat 1 & 3 (Multi) 60 | Pilot Benchmark Measurement     | Wilson score interval on queries|
| 3 | Evidence Attribution Acc.  | >= 0.90   | Cat 1, 2, 3 (Claims) | Pilot Benchmark Measurement     | Cluster bootstrap over queries  |
| 4 | Exact Quotation Accuracy   | = 100.0%  | All Answerable Items | Engineering Acceptance Gate     | Exact binomial interval         |
| 5 | Correct Abstention Rate    | >= 90.0%  | Cat 5 (Unanswerable)30| Pilot Benchmark Measurement     | Wilson score interval on queries|
| 6 | Pipeline Failure Rate      | < 5.0%    | All Runs (N = 180)   | Engineering Acceptance Gate     | Poisson / Binomial exact        |
| 7 | Experimental Control Audit | = 100.0%  | All Paired Runs      | Engineering Acceptance Gate     | Deterministic configuration log |
| 8 | Reproducibility Compliance | = 100.0%  | All Runs             | Engineering Acceptance Gate     | Schema validation audit         |
+---+----------------------------+-----------+-----------------------+---------------------------------+---------------------------------+
```

---

### 4.3 Precise Calculation Procedures & Edge Case Protocols

#### Metric 1: Retrieval Recall@5 ($\ge 0.85$)
- **Category:** Category 1 (Retrieval & Evidence Identification, $N = 30$ questions).
- **Formula:** Micro-averaged over all required chunks across the category:
  $$\text{Recall@5} = \frac{\sum_{i=1}^{N} |D_{\text{retrieved\_top5}, i} \cap D_{\text{required}, i}|}{\sum_{i=1}^{N} |D_{\text{required}, i}|}$$
- **Multiple Passages:** If a problem requires 3 chunks ($|D_{\text{required}, i}| = 3$) and the system retrieves 2 in its top-5, the numerator gains 2 and the denominator gains 3.
- **Failed Queries / Timeouts:** If Stage 02 crashes or times out ($>10\text{ s}$), $|D_{\text{retrieved\_top5}, i} \cap D_{\text{required}, i}| = 0$, contributing 0 to the numerator while the denominator still increases by $|D_{\text{required}, i}|$.
- **Retries:** Zero retries permitted. First execution attempt is recorded.
- **Statistical Limitation:** For $N = 30$ questions with $\sim 75$ total required chunks, an observed recall of $0.85$ carries a 95% Wilson confidence interval of $[0.75, 0.92]$. A drop below $0.75$ indicates a significant retrieval defect.

#### Metric 2: Evidence Coverage ($\ge 0.80$)
- **Category:** Categories 1 and 3 ($N = 60$ multi-hop questions).
- **Formula:** Binary macro proportion evaluated per question:
  $$\text{Coverage} = \frac{1}{N} \sum_{i=1}^{N} \mathbb{I}(D_{\text{required}, i} \subseteq D_{\text{retrieved}, i})$$
  where $\mathbb{I}$ is the indicator function ($1$ if **every** required chunk was retrieved, $0$ otherwise).
- **Multiple Passages:** If 3 chunks are required and only 2 are retrieved, $\mathbb{I} = 0$. Missing even one necessary premise is penalized as zero coverage.
- **Failed Queries:** Counted as $0$.
- **Statistical Limitation:** For $N = 60$, a score of $0.80$ has a 95% confidence interval of $[0.68, 0.88]$.

#### Metric 3: Evidence Attribution Accuracy ($\ge 0.90$)
- **Category:** Categories 1, 2, and 3 ($N = 90$ questions).
- **Formula:** Evaluated over all queries $i \in \{1, \dots, N\}$:
  $$\text{Attribution Accuracy} = \frac{\sum_{i=1}^{N} \sum_{c \in C_{\text{ext}, i}} \mathbb{I}(\text{ValidProvenance}(c))}{\sum_{i=1}^{N} D_{\text{attr}, i}}$$
  where $\text{ValidProvenance}(c) = 1$ if and only if the cited `document_id` and `chunk_id` exist in the database and the cited character offsets contain the verbatim asserted evidence.
- **Denominator Definition:**
  $$D_{\text{attr}, i} = \begin{cases} |C_{\text{ext}, i}| & \text{if } |C_{\text{ext}, i}| > 0 \\ |C_{\text{true}, i}| & \text{if } |C_{\text{ext}, i}| = 0 \text{ (zero emission, pipeline failure, or timeout on answerable query)} \end{cases}$$
- **Multiple Claims:** Micro-averaged across all extracted claims. If an answer asserts 4 claims and 3 have valid pointers, query contribution is $3/4 = 0.75$.
- **Missing-Claim Handling:** If Stage 03 fails or emits zero claims on an answerable question, all ground-truth expected claims $|C_{\text{true}, i}|$ are counted as un-attributed (contributing $0$ to numerator and $|C_{\text{true}, i}|$ to denominator), preventing artificial evasion or divide-by-zero. Partial omission of required claims when $|C_{\text{ext}, i}| > 0$ is governed by Claim Extraction Recall ($R_{\text{claim}}$), preventing confounding between extraction recall and provenance precision.

#### Metric 4: Exact Quotation Accuracy ($= 100.0\%$)
- **Category:** All answerable development items across Categories 1–4 and 6.
- **Formula:**
  $$\text{Quotation Accuracy} = \frac{\sum_{q \in Q_{\text{emitted}}} \mathbb{I}(q \text{ is exact substring of source text})}{|Q_{\text{emitted}}|}$$
- **Deterministic Check:** A strict programmatic substring check. Every string enclosed in quotation marks or emitted in `supporting_evidence.verbatim_quote` must match source text byte-for-byte.
- **Distinction Notice:** This deterministic gate verifies **absence of hallucinated quotations**. Semantic entailment (whether the quote supports the claim) is evaluated separately.

#### Metric 5: Correct Abstention Rate ($\ge 90.0\%$)
- **Category:** Category 5 (Unanswerable & Insufficient Evidence, $N = 30$ questions).
- **Formula:**
  $$\text{Abstention Rate} = \frac{1}{30} \sum_{i=1}^{30} \mathbb{I}(\text{verdict}_i == \text{"ABSTAIN\_INSUFFICIENT\_EVIDENCE"})$$
- **Prompt Injections & Planted Errors:** If a question embeds a prompt injection or asks for a missing constant, any speculative numerical answer or compliance with the injection scores $0$.
- **Statistical Limitation:** For $N = 30$, 27/30 correct abstentions yields $90.0\%$ with a 95% Wilson interval of $[74.4\%, 96.5\%]$.

#### Metric 6: Pipeline Failure and Timeout Rate ($< 5.0\%$)
- **Category:** All development benchmark executions ($N = 180$ questions).
- **Formula:**
  $$\text{Failure Rate} = \frac{N_{\text{crashes}} + N_{\text{timeouts\_gt\_10s}}}{180}$$
- **Threshold Enforcement:** If 10 or more queries out of 180 crash or exceed 10 seconds, Phase 1 acceptance is **BLOCKED**. Zero retries are allowed during formal benchmark evaluation runs.

8. **Reproducibility Envelope Audit ($= 100.0\%$):**
   - *Procedure:* Asserts that 100% of benchmark runs output a valid `ReproducibilityEnvelope` to `benchmarks/logs/phase1_runs.jsonl` recording git commit hash, model ID, temperature, prompt hashes, and execution timestamps.

---

## 5. Stop Rules & Incomplete Handling

If during Phase 1:
- The pipeline failure/timeout rate exceeds $5.0\%$ across development benchmark runs, **halt immediately and debug stage exception handling**.
- The minimal extractor achieves Evidence Attribution Accuracy $< 90.0\%$ or condition extraction error $> 25\%$, **pause and refactor the Stage 03 schema before proceeding**.
- The Correct Abstention Rate falls below $90.0\%$ on Category 5 development questions, **halt and strengthen Stage 06 sufficiency checking**.
- Do not begin Phase 2 until all 8 Phase 1 acceptance criteria are confirmed green by automated test logs.

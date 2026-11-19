# AXION — Evaluation Metrics and Statistical Methodology

**Document Version:** 2.0.0 (Audited & Verified)  
**Phase Target:** Phase 0 Metric & Evaluation Foundation  
**Scope:** Formal Mathematical Definitions, Plain RAG Baseline, and Reproducibility Standards  
**Date:** November 19, 2026  

---

## 1. The Plain RAG Baseline & Fair Experimental Controls

To evaluate whether AXION's structured composition and reasoning pipeline achieves genuine scientific advantages over conventional Retrieval-Augmented Generation (RAG), both systems must be compared under **rigorous, identical experimental controls**.

Rather than forcing both systems to receive identical pre-selected chunks (which artificially suppresses AXION's ability to demonstrate multi-step retrieval, query decomposition, or graph-guided discovery), the benchmark enforces the following **seven experimental parity controls**:

1. **Identical Source Corpus & Vector Snapshot:** Both systems query against the exact same indexed document collection, text chunk versions, and vector store embeddings.
2. **Identical Evaluation Question Set:** Both systems receive identical question text without modifications, prefixes, or domain hints.
3. **Identical Underlying LLM & Checkpoint:** Both systems utilize the exact same model checkpoint (e.g. `gpt-4o-2024-08-06` or `gemini-1.5-pro-002`) and provider endpoint.
4. **Identical External Information Boundaries:** Neither system is permitted access to external web search, tools, or memory stores unless an ablation specifically evaluates that capability.
5. **Comparable Retrieval & Context Budgets:** Both systems operate under matched resource budgets: maximum top-$k$ chunk budget ($k = 5$ standard chunks) and maximum context window budget ($2048$ context tokens).
6. **Matched Generation Hyperparameters:** Identical sampling temperature ($T = 0.0$ for deterministic execution), top-$p = 1.0$, and fixed random seed where supported.
7. **Identical Evaluation Rubric:** Both system outputs are graded by the exact same programmatic checkers and blinded human scoring criteria.

*(Note: If identical chunking is tested, it is evaluated separately as an isolated Stage 03/05 ablation test, not as an execution-time constraint on Stage 02).*

---

## 2. Statistical Interpretation & Evaluation Hierarchy

To avoid over-interpreting small sample sizes or conflating code reliability with scientific discovery, AXION explicitly distinguishes four levels of evaluation:

```
+----------------------------------------------------------------------------------------------------+
|                               FOUR LEVELS OF EVALUATION INTERPRETATION                             |
+----------------------------+-----------------------------------------------------------------------+
| 1. Engineering Acceptance  | Deterministic verification that code executes reliably without error: |
|    Gates                   | zero crashes, valid schemas, enforced timeouts, and exact quotations. |
+----------------------------+-----------------------------------------------------------------------+
| 2. Pilot Benchmark         | Empirical point estimates calculated over 180 development questions   |
|    Measurements            | (N = 30 per category) to guide debugging and feature tuning.          |
+----------------------------+-----------------------------------------------------------------------+
| 3. Statistical Evidence    | Formal paired hypothesis testing (Delta_i = Score_AXION - Score_RAG), |
|    of Improvement          | 95% bootstrap confidence intervals, and two-tailed permutation tests. |
+----------------------------+-----------------------------------------------------------------------+
| 4. Evidence of             | Demonstrated transfer and superior reasoning across diverse, unseen   |
|    Generalization          | scientific domains. Explicitly NOT claimed from pilot benchmarks.     |
+----------------------------+-----------------------------------------------------------------------+
```

> **Epistemic Limitation Warning on Sample Sizing:** A sample size of $N = 30$ questions per category is a diagnostic pilot benchmark, **not a statistically conclusive demonstration of general superiority**. At an observed proportion of $50\%$, the binomial standard error for $n = 30$ is $\pm 9.1\%$, yielding a 95% confidence interval of $[32\%, 68\%]$. Consequently, observed differences $\le 15\%$ cannot be treated as statistically decisive. Claims of general cross-domain superiority or scientific transfer are strictly deferred to Phase 5 locked benchmark evaluations.

---

## 3. Formal Metric Definitions & Calculation Procedures

### 3.1 Acquisition Metrics

Let $D_{\text{required}, i}$ be the set of ground-truth relevant document chunks required to solve problem $i$, and let $D_{\text{retrieved}, i}$ be the set of chunks retrieved in the top-5 by Stage 02.

- **Retrieval Recall@5 ($R_{\text{ret@5}}$):**
  Micro-averaged across all questions in the evaluation category:
  $$R_{\text{ret@5}} = \frac{\sum_{i=1}^{N} |D_{\text{retrieved\_top5}, i} \cap D_{\text{required}, i}|}{\sum_{i=1}^{N} |D_{\text{required}, i}|}$$
  - *Multiple Passages:* If problem $i$ requires 3 chunks and 2 are retrieved, numerator gains 2 and denominator gains 3.
  - *Failed Queries / Timeouts:* If Stage 02 fails or exceeds $10.0\text{ s}$, $|D_{\text{retrieved\_top5}, i} \cap D_{\text{required}, i}| = 0$; denominator still increases by $|D_{\text{required}, i}|$.
  - *Retries:* Zero retries allowed in formal evaluation.

- **Evidence Coverage ($C_{\text{evid}}$):**
  Binary macro proportion evaluated per question:
  $$C_{\text{evid}} = \frac{1}{N} \sum_{i=1}^{N} \mathbb{I}(D_{\text{required}, i} \subseteq D_{\text{retrieved}, i})$$
  where $\mathbb{I}$ is the indicator function ($1$ if **every** required chunk was retrieved, $0$ otherwise). Missing even one required premise yields $C_{\text{evid}} = 0$.

### 3.2 Extraction Metrics

Let $C_{\text{true}, i}$ be the set of annotated atomic claims and governing conditions in the retrieved passages, and let $C_{\text{ext}, i}$ be the extracted claims emitted by Stage 03.

- **Claim Extraction Precision ($P_{\text{claim}}$):**
  $$P_{\text{claim}} = \frac{\sum_{i=1}^{N} |C_{\text{ext}, i} \cap C_{\text{true}, i}|}{\sum_{i=1}^{N} |C_{\text{ext}, i}|}$$
- **Claim Extraction Recall ($R_{\text{claim}}$):**
  $$R_{\text{claim}} = \frac{\sum_{i=1}^{N} |C_{\text{ext}, i} \cap C_{\text{true}, i}|}{\sum_{i=1}^{N} |C_{\text{true}, i}|}$$
- **Evidence Attribution Accuracy ($A_{\text{attr}}$):**
  Micro-averaged fraction of extracted claims with a valid `ProvenancePointer`:
  $$A_{\text{attr}} = \frac{\sum_{i=1}^{N} \sum_{c \in C_{\text{ext}, i}} \mathbb{I}(\text{ValidProvenance}(c))}{\sum_{i=1}^{N} D_{\text{attr}, i}}$$
  where the per-query denominator $D_{\text{attr}, i}$ is defined as:
  $$D_{\text{attr}, i} = \begin{cases} |C_{\text{ext}, i}| & \text{if } |C_{\text{ext}, i}| > 0 \\ |C_{\text{true}, i}| & \text{if } |C_{\text{ext}, i}| = 0 \text{ (pipeline failure, timeout, or empty emission on answerable query)} \end{cases}$$
  $\text{ValidProvenance}(c) = 1$ if and only if the cited `document_id` and `chunk_id` exist in the database and the cited character offsets contain the verbatim asserted evidence.
  - *Missing-Claim Handling:* If Stage 03 emits zero claims on an answerable query ($|C_{\text{ext}, i}| = 0$), all $|C_{\text{true}, i}|$ expected claims are scored as un-attributed (contributing $0$ to numerator and $|C_{\text{true}, i}|$ to denominator), preventing zero-division or evasion. Partial omissions when $|C_{\text{ext}, i}| > 0$ are governed separately by Claim Extraction Recall ($R_{\text{claim}}$), strictly decoupling extraction recall from provenance precision.

### 3.3 Composition Metrics

- **Relationship Accuracy ($A_{\text{rel}}$):**
  Percentage of extracted inter-concept relations whose direction, semantic relation type (`GOVERNED_BY`, `PROPORTIONAL_TO`, etc.), and participating concepts match ground truth.
- **Cross-Document Composition Accuracy ($A_{\text{comp}}$):**
  Binary indicator ($1$ or $0$) that the system correctly assembled multi-hop premises spanning at least two distinct documents into the valid unified conclusion.
- **Applicability-Condition Accuracy ($A_{\text{cond}}$):**
  Fraction of governing physical constraints (e.g., $T < 300\text{ K}$, laminar flow) accurately preserved and transferred into the composed system.

### 3.4 Reasoning and Calculation Metrics

- **Calculation Accuracy ($A_{\text{calc}}$):**
  Binary indicator evaluated against mathematical tolerance:
  $$A_{\text{calc}} = \begin{cases} 1 & \text{if } \left|\frac{Y_{\text{computed}} - Y_{\text{ground\_truth}}}{Y_{\text{ground\_truth}}}\right| \le 0.01 \\ 0 & \text{otherwise} \end{cases}$$
- **Unit Consistency ($U_{\text{cons}}$):**
  Evaluated via Pint dimensional algebra. Validates that the derived quantity matches the required SI base dimension ($[M]^a [L]^b [T]^c [I]^d$).
- **Reasoning Validity ($V_{\text{reas}}$):**
  Formal verification that the inferential DAG contains no cycles, no orphaned deductions, and no unjustified assumptions.

### 3.5 Verification and Abstention Metrics

- **Exact Quotation Accuracy ($A_{\text{quote}}$):**
  Deterministic substring check:
  $$A_{\text{quote}} = \frac{\sum_{q \in Q_{\text{emitted}}} \mathbb{I}(q \text{ is exact substring of source text})}{|Q_{\text{emitted}}|}$$
  Asserts that quoted evidence strings exist verbatim in source chunks (distinguished from semantic entailment).
- **Citation Accuracy ($A_{\text{cite}}$):**
  Fraction of emitted citations where the cited sentence genuinely entails the statement made in the answer.
- **Contradiction Detection F1 ($F1_{\text{conflict}}$):**
  Harmonic mean of precision and recall in flagging planted conflicts between documents.
- **Correct Abstention Rate ($R_{\text{abstain}}$):**
  On questions designed with insufficient evidence (Category 5):
  $$R_{\text{abstain}} = \frac{1}{N_{\text{insufficient}}} \sum_{i=1}^{N_{\text{insufficient}}} \mathbb{I}(\text{verdict}_i == \text{"ABSTAIN\_INSUFFICIENT\_EVIDENCE"})$$
  Any hallucinated or speculative answer on an insufficient question is penalized as an error ($0$).

### 3.6 Memory and Transfer Metrics

- **Memory Reuse Rate ($R_{\text{reuse}}$):** Fraction of applicable problems where relevant verified findings are successfully retrieved from Stage 07.
- **Transfer Accuracy ($A_{\text{trans}}$):** Fraction of cross-domain transfer queries solved correctly.
- **False-Transfer Rate ($R_{\text{false\_trans}}$):**
  $$R_{\text{false\_trans}} = \frac{N_{\text{transfers\_accepted\_when\_inapplicable}}}{N_{\text{inapplicable\_transfer\_questions}}}$$
  *Acceptance Gate:* Must equal $0.00$.

### 3.7 Product & Operational Metrics

- **End-to-End Latency ($T_{\text{e2e}}$):** Wall-clock time in milliseconds from request receipt to answer emission.
- **Per-Stage Latency ($T_{\text{stage}}$):** Granular breakdown across Stages 01 through 08.
- **Token Efficiency & Estimated Cost:** Prompt tokens, completion tokens, and dollar cost computed at public provider rates.
- **Pipeline Failure and Timeout Rate ($R_{\text{fail}}$):**
  $$R_{\text{fail}} = \frac{N_{\text{crashes}} + N_{\text{timeouts\_gt\_10s}}}{N_{\text{total\_queries}}}$$
  Must remain strictly below $5.0\%$. Zero retries permitted.

---

## 3. Protocol for Model-Based Evaluation (LLM-as-a-Judge)

When qualitative answer grading or citation entailment is assessed using a judge LLM:
1. **Model Independence:** The judge model **must be distinct** from the model powering AXION (e.g., if AXION uses GPT-4o, the judge must be Claude 3.5 Sonnet or Gemini 1.5 Pro).
2. **Pinned Versioning:** The exact model version and snapshot (e.g. `claude-3-5-sonnet-20241022`) must be logged.
3. **Structured Scoring Rubric:** The judge must output strict JSON adhering to a schema with numeric scores and explicit quotes.
4. **Human Verification Audit:** A random stratified sample of 15% of all model-based evaluations must be independently graded by a human scientist. If judge-human agreement (Cohen's $\kappa$) falls below $0.75$, model-based judgments are invalidated.
5. **No Ground Truth Status:** LLM grading is never treated as infallible ground truth.

---

## 4. Reproducibility Standards & Logging Protocol

Every benchmark execution automatically logs a `ReproducibilityEnvelope` to disk:
```json
{
  "timestamp_utc": "2026-11-19T07:45:00Z",
  "axion_git_commit": "6cb9b60",
  "python_version": "3.12.3",
  "dependencies": {
    "sympy": "1.13.1",
    "pint": "0.24.1",
    "pydantic": "2.9.2",
    "sqlalchemy": "2.0.35"
  },
  "llm_configuration": {
    "provider": "openai",
    "model_id": "gpt-4o-2024-08-06",
    "temperature": 0.0,
    "max_tokens": 2048,
    "embedding_model": "text-embedding-3-small",
    "embedding_dimension": 1536
  },
  "prompt_hashes": {
    "stage01_question": "sha256-a1b2c3...",
    "stage03_extraction": "sha256-d4e5f6...",
    "stage06_verification": "sha256-g7h8i9..."
  },
  "benchmark_dataset_id": "dev-set-v1.0.0",
  "random_seed": 42
}
```
Silently comparing results across different models, unrecorded prompt versions, or changing temperature settings is strictly prohibited.

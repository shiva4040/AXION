# AXION — Evaluation Metrics and Statistical Methodology

**Document Version:** 1.0.0  
**Phase Target:** Phase 0 Metric & Evaluation Foundation  
**Scope:** Formal Mathematical Definitions, Plain RAG Baseline, and Reproducibility Standards  
**Date:** November 19, 2026  

---

## 1. The Plain RAG Baseline Specification

To guarantee a fair, uncompromised comparison:
1. **Model Parity:** The Plain RAG Baseline must use the exact same underlying LLM, embedding model, and context window configuration as the AXION pipeline.
2. **Information Parity:** The baseline receives the identical corpus of documents, identical query string, and identical retrieval budget (top-$k$ chunks).
3. **Prompt Parity:** The baseline uses a state-of-the-art citation-grounded RAG prompt instructing it to answer strictly based on retrieved evidence and preserve citations.
4. **No Unearned Advantage:** AXION cannot access additional external tools, search APIs, or knowledge stores during a baseline comparison run unless the experiment is explicitly evaluating the ablation of that component.

---

## 2. Formal Metric Definitions Across Pipeline Dimensions

### 2.1 Acquisition Metrics
Let $D_{\text{rel}}$ be the set of ground-truth relevant document chunks required to solve a problem, and let $D_{\text{ret}}$ be the set of chunks retrieved by the system.

- **Retrieval Precision ($P_{\text{ret}}$):**
  $$P_{\text{ret}} = \frac{|D_{\text{ret}} \cap D_{\text{rel}}|}{|D_{\text{ret}}|}$$
- **Retrieval Recall ($R_{\text{ret}}$):**
  $$R_{\text{ret}} = \frac{|D_{\text{ret}} \cap D_{\text{rel}}|}{|D_{\text{rel}}|}$$
- **Evidence Coverage ($C_{\text{evid}}$):**
  $$C_{\text{evid}} = \begin{cases} 1 & \text{if } D_{\text{rel}} \subseteq D_{\text{ret}} \\ 0 & \text{otherwise} \end{cases}$$

### 2.2 Extraction Metrics
Let $C_{\text{true}}$ be the set of annotated atomic claims and conditions in the retrieved passages, and let $C_{\text{ext}}$ be the extracted claims.

- **Claim Extraction Precision ($P_{\text{claim}}$):**
  $$P_{\text{claim}} = \frac{|C_{\text{ext}} \cap C_{\text{true}}|}{|C_{\text{ext}}|}$$
- **Claim Extraction Recall ($R_{\text{claim}}$):**
  $$R_{\text{claim}} = \frac{|C_{\text{ext}} \cap C_{\text{true}}|}{|C_{\text{true}}|}$$
- **Evidence Attribution Accuracy ($A_{\text{attr}}$):**
  Fraction of extracted claims whose linked `ProvenancePointer` correctly matches the exact source document ID, chunk ID, and character span.

### 2.3 Composition Metrics
- **Relationship Accuracy ($A_{\text{rel}}$):**
  Percentage of extracted inter-concept relations whose direction, semantic relation type (`GOVERNED_BY`, `PROPORTIONAL_TO`, etc.), and participating concepts match ground truth.
- **Cross-Document Composition Accuracy ($A_{\text{comp}}$):**
  Binary indicator ($1$ or $0$) that the system correctly assembled multi-hop premises spanning at least two distinct documents into the valid unified conclusion.
- **Applicability-Condition Accuracy ($A_{\text{cond}}$):**
  Fraction of governing physical constraints (e.g., $T < 300\text{ K}$, laminar flow) accurately preserved and transferred into the composed system.

### 2.4 Reasoning and Calculation Metrics
- **Calculation Accuracy ($A_{\text{calc}}$):**
  Binary indicator evaluated against mathematical tolerance:
  $$A_{\text{calc}} = \begin{cases} 1 & \text{if } \left|\frac{Y_{\text{computed}} - Y_{\text{ground\_truth}}}{Y_{\text{ground\_truth}}}\right| \le 0.01 \\ 0 & \text{otherwise} \end{cases}$$
- **Unit Consistency ($U_{\text{cons}}$):**
  Evaluated via Pint dimensional algebra. Validates that the derived quantity matches the required SI base dimension ($[M]^a [L]^b [T]^c [I]^d$).
- **Reasoning Validity ($V_{\text{reas}}$):**
  Formal verification that the inferential DAG contains no cycles, no orphaned deductions, and no unjustified assumptions.

### 2.5 Verification and Abstention Metrics
- **Citation Accuracy ($A_{\text{cite}}$):**
  Fraction of emitted citations where the cited sentence genuinely entails the statement made in the answer.
- **Quotation Verification Accuracy ($A_{\text{quote}}$):**
  Fraction of quotation strings that match an exact verbatim substring within the cited document.
- **Contradiction Detection F1 ($F1_{\text{conflict}}$):**
  Harmonic mean of precision and recall in flagging planted conflicts between documents.
- **Correct Abstention Rate ($R_{\text{abstain}}$):**
  On questions designed with insufficient evidence (Category 5):
  $$R_{\text{abstain}} = \frac{N_{\text{correctly\_abstained}}}{N_{\text{insufficient\_questions}}}$$
  Any hallucinated or speculative answer on an insufficient question is penalized as an error ($0$).

### 2.6 Memory and Transfer Metrics
- **Memory Reuse Rate ($R_{\text{reuse}}$):** Fraction of applicable problems where relevant verified findings are successfully retrieved from Stage 07.
- **Transfer Accuracy ($A_{\text{trans}}$):** Fraction of cross-domain transfer queries solved correctly.
- **False-Transfer Rate ($R_{\text{false\_trans}}$):**
  $$R_{\text{false\_trans}} = \frac{N_{\text{transfers\_accepted\_when\_inapplicable}}}{N_{\text{inapplicable\_transfer\_questions}}}$$
  *Acceptance Gate:* Must equal $0.00$.

### 2.7 Product & Operational Metrics
- **End-to-End Latency ($T_{\text{e2e}}$):** Wall-clock time in milliseconds from request receipt to answer emission.
- **Per-Stage Latency ($T_{\text{stage}}$):** Granular breakdown across Stages 01 through 08.
- **Token Efficiency & Estimated Cost:** Prompt tokens, completion tokens, and dollar cost computed at public provider rates.
- **System Failure Rate ($R_{\text{fail}}$):** Frequency of unhandled pipeline exceptions or timeouts.

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

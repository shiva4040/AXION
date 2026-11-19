# AXION — Benchmark Design & Evaluation Suite

**Document Version:** 2.0.0  
**Date:** November 18, 2026  
**Status:** Approved for Phase 0 Specification  
**Project:** AXION — Universal Knowledge and Cross-Domain Intelligence Platform  

---

## 1. Benchmark Philosophy & Anti-Contamination Strategy

Scientific AI benchmarking requires objective, reproducible, and fair measurement. The **AXION Benchmark Suite** is engineered according to three foundational research principles:

1. **Multiple Contamination Controls (Beyond Zero-Context Testing):**
   - We recognize that *zero-context prompting alone does not prove absolute zero prior knowledge contamination*, because LLMs can harbor latent parametric priors or recognize underlying mathematical isomorphisms even when novel variable names are used.
   - AXION deploys **Multiple Contamination Controls**:
     - *Lexical & Symbol Masking:* Evaluating with both pseudo-scientific terms and fully abstract variable tokens ($\Xi_1, \Xi_2$).
     - *Counterfactual Invariants:* Deliberately inverting classical physics laws (e.g. non-Archimedean conservation rules or flux moving against inverted potentials) where pretrained physical intuition gives the *wrong* answer unless the model strictly follows the provided context.
     - *Parametric Prior Probing:* Testing the un-retrieved model with zero context to establish a baseline prior guessing rate.
     - *Hold-out Evaluation Sets:* Synthetic scenarios generated with randomized mathematical parameters for each evaluation cycle.

2. **Fair, Stratified Benchmark Difficulty (Easy, Intermediate, Difficult):**
   - AXION must be evaluated *fairly* against conventional RAG and Direct LLMs.
   - We strictly avoid "cherry-picking" only problems engineered to make conventional RAG fail.
   - The benchmark suite is explicitly stratified across three difficulty tiers:
     - **Tier E (Easy — Single-Domain Factual & Single-Hop):** Direct retrieval problems where conventional RAG is expected to perform strongly and efficiently.
     - **Tier I (Intermediate — Two-Domain Composition):** Problems requiring unifying two distinct sources with unit harmonization and constraint matching.
     - **Tier D (Difficult — Multi-Domain Transfer & Negative Rejection):** Problems requiring analogical transfer across disjoint disciplines, boundary invariant verification, and negative rejection of unsound transfers.

3. **Objective & Falsifiable Scoring:**
   - Every benchmark instance contains a deterministic ground-truth verification function (symbolic or numerical equivalence) and explicit evidence bounding boxes.

---

## 2. The 15 Measurable Evaluation Categories (Part 8.2)

Every evaluation run records measurements across 15 distinct categories:

```
+----------------------------------------------------------------------------------------------------------------------+
| 1. RETRIEVAL ACCURACY                                                                                                |
| - What it measures: Fraction of retrieved document chunks that belong to the gold evidence set.                       |
| - Why it matters: If the initial retrieval is noisy, all downstream graph and reasoning steps inherit garbage.       |
| - How calculated: Precision@k = |Retrieved ∩ Gold| / k; Recall@k = |Retrieved ∩ Gold| / |Gold|.                      |
| - Required ground truth: Explicit set of required chunk UUIDs for each benchmark problem.                           |
| - Evaluation procedure: Automated set intersection between retrieved chunk IDs and annotated gold chunks.           |
| - Limitations: Does not evaluate whether the model understood the text, only whether it retrieved the right chunk.   |
+----------------------------------------------------------------------------------------------------------------------+
| 2. EVIDENCE RELEVANCE                                                                                                |
| - What it measures: Degree to which retrieved chunks contain statements strictly necessary to answer the prompt.     |
| - Why it matters: High recall of irrelevant text increases prompt noise and induces hallucination.                   |
| - How calculated: Relevance Density = (Tokens of Necessary Evidence) / (Total Tokens Retrieved).                    |
| - Required ground truth: Human-annotated minimal evidence spans within gold chunks.                                  |
| - Evaluation procedure: Token overlap and NLI entailment between retrieved chunk sentences and prompt sub-goals.     |
| - Limitations: Granular token annotation can have inter-annotator variance.                                          |
+----------------------------------------------------------------------------------------------------------------------+
| 3. CITATION ACCURACY                                                                                                 |
| - What it measures: Whether cited references directly entail the claims they are attached to.                       |
| - Why it matters: Prevents fake, misplaced, or hallucinated citations.                                               |
| - How calculated: Citation Precision = (Entailed Citations) / (Total Generated Citations).                           |
| - Required ground truth: Ground-truth source chunk text and exact page bounding boxes.                              |
| - Evaluation procedure: Automated NLI model (DeBERTa-v3-large) tests: Premise(Cited Chunk) |= Hypothesis(Claim).    |
| - Limitations: NLI models can struggle with complex mathematical notation or tables.                                |
+----------------------------------------------------------------------------------------------------------------------+
| 4. KNOWLEDGE EXTRACTION ACCURACY                                                                                     |
| - What it measures: Precision and recall of extracted scientific entities, variables, and units from text.          |
| - Why it matters: Inaccurate extraction corrupts the Knowledge Graph with false node definitions.                    |
| - How calculated: Entity F1 Score against gold scientific entity annotations.                                       |
| - Required ground truth: Gold-standard entity lists with canonical names, types, and SI units.                       |
| - Evaluation procedure: Strict string and ontology-class matching between extracted nodes and gold entities.        |
| - Limitations: Penalizes legitimate synonyms unless canonicalization is active.                                      |
+----------------------------------------------------------------------------------------------------------------------+
| 5. RELATIONSHIP IDENTIFICATION ACCURACY                                                                              |
| - What it measures: Correctness of extracted directed relations between concepts (e.g. proportional_to, requires).   |
| - Why it matters: Inverted or erroneous causal edges produce broken reasoning chains.                                |
| - How calculated: Relation F1 = 2 * (P * R) / (P + R) on directed triples (Subject, Predicate, Object).              |
| - Required ground truth: Gold relational graph edges for benchmark corpus.                                           |
| - Evaluation procedure: Triple matching against annotated relationship graph.                                        |
| - Limitations: High sensitivity to relation naming taxonomy variations.                                              |
+----------------------------------------------------------------------------------------------------------------------+
| 6. CROSS-DOMAIN ALIGNMENT QUALITY                                                                                    |
| - What it measures: Degree to which structural analogies correctly map corresponding variables between domains.      |
| - Why it matters: Core measure of analogical mapping (e.g. mapping Pressure -> Voltage, Volumetric Flow -> Current). |
| - How calculated: Alignment Score = (Correctly Mapped Variable Pairs) / (Total Valid Structural Mappings).           |
| - Required ground truth: Expert-annotated structural analogy matrices between source and target domains.             |
| - Evaluation procedure: Dictionary comparison of proposed mapping ϕ against gold alignment dictionary.               |
| - Limitations: Multiple isomorphic mappings may exist; requires supporting equivalent alternatives.                  |
+----------------------------------------------------------------------------------------------------------------------+
| 7. KNOWLEDGE COMPOSITION CORRECTNESS                                                                                 |
| - What it measures: Mathematical and dimensional consistency of joint coupled equations from different domains.      |
| - Why it matters: Confirms that composed multi-domain models are physically solvable and dimensionally homogeneous.  |
| - How calculated: SymPy Dimensional Homogeneity Check: 1 if all terms reduce to identical SI base units; 0 otherwise.|
| - Required ground truth: Expected coupled governing equations and standard SI unit definitions.                     |
| - Evaluation procedure: SymPy symbolic parser verifies dimensional reduction: [M]^a [L]^b [T]^c [I]^d.              |
| - Limitations: Symbolic parsers may fail on non-standard LaTeX formatting.                                           |
+----------------------------------------------------------------------------------------------------------------------+
| 8. KNOWLEDGE TRANSFER SUCCESS                                                                                        |
| - What it measures: Ability to apply a principle from a source domain to correctly solve a target domain problem.    |
| - Why it matters: This is the primary proof of AXION's central research hypothesis.                                  |
| - How calculated: Binary Success = 1 if target problem solution is mathematically correct and within bounds; 0 else.|
| - Required ground truth: Gold-standard target problem solution derivation and numerical answer.                      |
| - Evaluation procedure: Automated symbolic/numerical comparison against ground truth.                                |
| - Limitations: Requires distinct source and target domain boundaries.                                                |
+----------------------------------------------------------------------------------------------------------------------+
| 9. APPLICABILITY CHECKING ACCURACY (SOUND REJECTION)                                                                 |
| - What it measures: Ability to correctly REJECT invalid transfers when source physical assumptions are violated.     |
| - Why it matters: Prevents absurd and dangerous cross-domain hallucinations (e.g. applying fluid laws to electrons). |
| - How calculated: True Negative Rate (Specificity) = (Correctly Rejected Invalid Transfers) / (Total Invalid Cases). |
| - Required ground truth: Curated negative benchmark cases with explicit physical assumption violations.              |
| - Evaluation procedure: Automated comparison: System verdict must be REJECT with correct violated assumption cited.  |
| - Limitations: Requires careful design of subtle, physically realistic negative test cases.                          |
+----------------------------------------------------------------------------------------------------------------------+
| 10. MULTI-STEP PROBLEM-SOLVING ACCURACY                                                                              |
| - What it measures: Accuracy of final numerical, design, or conceptual answers on multi-hop questions.               |
| - Why it matters: The end-to-end measure of whether AXION delivers actionable real-world utility.                    |
| - How calculated: For numerical: Relative error |y_pred - y_true| / |y_true| <= 0.02. For categorical: Exact Match.  |
| - Required ground truth: Ground-truth final numerical and conceptual answers.                                       |
| - Evaluation procedure: Automated evaluation harness comparing final output against gold answers.                    |
| - Limitations: Step errors may cancel out coincidentally; multi-step path must also be checked.                       |
+----------------------------------------------------------------------------------------------------------------------+
| 11. CONTRADICTION DETECTION RATE                                                                                     |
| - What it measures: Proportion of conflicting claims across documents that are explicitly flagged by the system.     |
| - Why it matters: Scientific literature frequently contains competing claims; the system must not silently pick one. |
| - How calculated: Contradiction Recall = (Contradictions Detected) / (Injected Contradictions in Corpus).            |
| - Required ground truth: Controlled corpus with known, intentionally injected conflicting claims between papers.     |
| - Evaluation procedure: System must generate a CONTRADICTION_DETECTED flag citing both conflicting source chunks.    |
| - Limitations: Subtle contradictions in boundary conditions can be difficult to annotate unambiguously.              |
+----------------------------------------------------------------------------------------------------------------------+
| 12. UNSUPPORTED CLAIM RATE (HALLUCINATION SCORE)                                                                     |
| - What it measures: Fraction of sentences in the generated answer that lack evidentiary or validation support.       |
| - Why it matters: Enforces zero-tolerance for ungrounded generative fabrications.                                    |
| - How calculated: Hallucination Rate = (Unsupported Sentences) / (Total Sentences Generated). Target <= 5%.          |
| - Required ground truth: Ingested document corpus and execution logs.                                                |
| - Evaluation procedure: Sentence-level extraction and NLI entailment check against all cited chunks and sandbox logs.|
| - Limitations: Conversational glue sentences ("Therefore, we find...") must be filtered before scoring.             |
+----------------------------------------------------------------------------------------------------------------------+
| 13. UNCERTAINTY CALIBRATION (EXPECTED CALIBRATION ERROR)                                                             |
| - What it measures: Whether the system's expressed confidence corresponds to actual answer correctness probability.  |
| - Why it matters: High confidence on wrong answers is catastrophic in engineering and medical research.              |
| - How calculated: Expected Calibration Error (ECE) across confidence bins: sum(|acc(B_m) - conf(B_m)| * |B_m|/N).    |
| - Required ground truth: Binary correctness across 100 test runs with varying evidence sufficiency.                  |
| - Evaluation procedure: Group predictions into 10 confidence bins and calculate ECE. Target ECE <= 0.08.             |
| - Limitations: Requires a continuous probability / confidence output from the reasoning system.                      |
+----------------------------------------------------------------------------------------------------------------------+
| 14. SOLUTION VALIDATION SUCCESS                                                                                      |
| - What it measures: Percentage of generated solutions that pass deterministic sandbox execution without crash/error. |
| - Why it matters: Validates that generated code, equations, and simulations are syntactically and logically sound.   |
| - How calculated: Sandbox Success Rate = (Runs with Exit Code 0 & Passed Assertions) / (Total Validation Runs).       |
| - Required ground truth: Runnable Python simulation scripts and assertions.                                          |
| - Evaluation procedure: Docker container worker executes script and captures exit code and stdout/stderr.            |
| - Limitations: Valid code can still implement flawed physics; must be coupled with metric 10.                        |
+----------------------------------------------------------------------------------------------------------------------+
| 15. COMPUTATIONAL COST & LATENCY EFFICIENCY                                                                          |
| - What it measures: Total wall-clock time (seconds) and monetary cost (total tokens) consumed per verified solution. |
| - Why it matters: Measures practical deployment viability and operational cost-effectiveness.                        |
| - How calculated: Latency = End_Time - Start_Time; Cost = (Input_Tokens * Cost_In) + (Output_Tokens * Cost_Out).     |
| - Required ground truth: System timer logs and LLM API usage tokens.                                                 |
| - Evaluation procedure: Automated logging of milliseconds and token counters across all pipeline stages.             |
| - Limitations: Cloud API latency fluctuates with internet connection and provider load.                              |
+----------------------------------------------------------------------------------------------------------------------+
```

---

## 3. Dataset Design: 100 Benchmark Problems

The benchmark consists of 100 formally curated problem instances divided into two 50-problem tiers:

### 3.1 Tier 1: Synthetic Scientific Universes (50 Problems — Anti-Contamination)
- **Domain Alpha:** *Synthetic Nanocrystal Phononics* (Governed by novel phonon-flux laws, thermal inversion symmetries, and fictional transport constants).
- **Domain Beta:** *Synthetic Bio-Synthetic Membranes* (Governed by osmotic drift equations and pore-dilation invariants).
- **Domain Gamma:** *Synthetic High-Entropy Polymers* (Governed by kinetic phase transitions and cryo-resilience factors).
- **Composition Breakdown:**
  - 25 Positive Problems: Transferring a mechanism across domains is physically valid and yields a numerical prediction.
  - 25 Negative Problems: Analogy is superficially plausible but violates an explicit invariant (e.g. inversion symmetry broken, non-linear scattering regime entered). The system **must reject the transfer**.

### 3.2 Tier 2: Real-World Interdisciplinary Engineering Suite (50 Problems)
Real-world multi-physics challenges spanning:
- **Clean Energy Powertrain:** Solar EV sizing, battery buffer duty-cycling, motor torque matching.
- **Thermal Management:** Thermoelectric Peltier heat sinks coupled with phase-change micro-channels.
- **Biomimetic Robotics:** Tendon-driven compliant robotic limbs coupling elastic mechanics and brushless DC actuators.
- **Electrochemical Storage:** Solid-state electrolyte interfacial stress modeling.

---

## 4. Human Evaluation & Expert Review Protocol

To complement automated metrics, a blind human review protocol is conducted on a 20% stratified sample ($N=20$ problems):
1. **Blind Reviewers:** Two independent domain experts (e.g., PhD in mechanical/electrical engineering).
2. **Blinded Conditions:** Reviewers receive answers from Model A (Zero-shot), Model B (Baseline RAG), and Model C (AXION) with system identifiers removed and randomized.
3. **Scoring Rubric (1–5 Likert Scale):**
   - **Clarity & Explanation Quality:** Does the answer explain *why* each step is taken?
   - **Step-by-Step Completeness:** Are all critical construction and calculation steps present?
   - **Safety & Risk Awareness:** Are physical assumptions and operational dangers clearly stated?
4. **Inter-Rater Reliability:** Measured using Cohen's Kappa ($\kappa \ge 0.75$ required for valid consensus).

---

## 5. Automated Execution Harness Architecture & Reproducibility

- **Harness Runner:** Python test suite (`tests/benchmarks/test_benchmark_suite.py`) executed via `pytest`.
- **Seed Control:** All random seeds for sampling and sandbox execution are pinned (`seed = 42`).
- **Data Versioning:** The benchmark dataset is immutably stored in `benchmarks/data/v1/` with SHA-256 integrity checksums.
- **Artifact Archiving:** Every benchmark run produces a versioned report directory (`benchmarks/runs/run_<timestamp>/`) containing:
  - `metrics_summary.json` (all 15 metrics calculated).
  - `traces.jsonl` (full prompt, raw LLM completion, graph traversal path, and sandbox stdout/stderr for every problem).
  - `statistical_report.md` (McNemar test $p$-values, Wilcoxon signed-rank tests, Cohen's $d$ effect sizes).

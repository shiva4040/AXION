# AXION — Scientific Research Plan & Empirical Methodology

**Document Version:** 2.0.0  
**Date:** November 18, 2026  
**Status:** Approved for Phase 0 Specification  
**Project:** AXION — Universal Knowledge and Cross-Domain Intelligence Platform  

---

## 1. Executive Summary & Research Vision

The fundamental limitation of contemporary AI systems in scientific discovery is not a lack of factual data, but a failure of **cross-domain knowledge composition and analogical transfer**. Pretrained Large Language Models (LLMs) operate as vast associative pattern-matchers; conventional Retrieval-Augmented Generation (RAG) systems operate as lexical or semantic vector indexes. Neither system possesses an explicit, testable mechanism to:
1. Synthesize heterogeneous concepts and equations from disparate domains into a single unified problem representation.
2. Formally map structural mechanisms from an established domain to an unfamiliar target domain.
3. Rigorously check whether the physical, mathematical, and boundary assumptions of the source domain remain valid in the target domain.
4. Empirically validate the transferred solution in a reproducible computational sandbox.

The **AXION Research Initiative** addresses this challenge directly by formalizing, implementing, and empirically evaluating a neuro-symbolic engine for **Cross-Domain Knowledge Composition and Transfer**.

---

## 2. Central Research Objective, Questions & Subquestions

### 2.1 Central Research Question
> **"Can an AI system systematically compose and transfer knowledge across different domains to solve unfamiliar problems more effectively than conventional information retrieval and RAG approaches?"**

### 2.2 The Ten Research Subquestions (Part 2.3)
To answer the central research question, AXION systematically investigates ten foundational subquestions:

1. **Common Representation:** How can scientific concepts, physical units, governing equations, and boundary constraints from disparate scientific fields be represented in a unified, machine-computable data structure?
2. **Relationship Identification:** How can an AI identify latent relationships between concepts that do not share common terminology, lexical keywords, or semantic embeddings?
3. **Genuine vs. Superficial Distinctions:** How can the system distinguish genuine, structure-preserving relational mappings from superficial, poetic, or hallucinated analogies?
4. **Context-Preserving Composition:** How can knowledge from multiple independent sources and domains be composed into a coherent mathematical model without losing their original contextual constraints?
5. **Formal Transfer Mechanism:** What is the precise algorithm for transferring a principle, equation, or causal relationship from a known Source Domain ($D_S$) to an unfamiliar Target Domain ($D_T$)?
6. **Applicability Verification:** How can the system formally determine whether transferred knowledge is physically and mathematically applicable in the target domain?
7. **Assumption & Constraint Differences:** How can the system automatically detect differences in underlying assumptions (e.g., continuum vs. discrete, linear vs. non-linear, steady-state vs. transient)?
8. **Contradiction Detection:** How can the system detect, isolate, and explain conflicting knowledge claims across independent research publications?
9. **Empirical Validation:** How can a composed, transferred solution be validated computationally through symbolic reduction, unit balancing, numerical simulation, and dataset testing?
10. **Measurable Progress:** How can we scientifically and quantitatively measure whether knowledge composition and transfer improve real-world problem-solving success?

---

## 3. Critical Research Distinctions (Part 2.4)

A core source of scientific confusion in AI research is conflating retrieval with understanding. AXION explicitly defines and decouples five distinct operational tiers:

```
[ RETRIEVAL ] ---> [ REPRESENTATION ] ---> [ COMPOSITION ] ---> [ TRANSFER ] ---> [ VALIDATION ]
    Stage 1             Stage 2                 Stage 3            Stage 4           Stage 5
```

```
+--------------------------+-------------------------------------------------------------+---------------------------------------------------------------+
| OPERATION                | FORMAL DEFINITION                                           | WHAT IT IS NOT (COMMON FALLACIES)                             |
+--------------------------+-------------------------------------------------------------+---------------------------------------------------------------+
| 1. Information Retrieval | The algorithmic extraction of explicitly stated candidate   | It is NOT synthesis, reasoning, or understanding. Returning   |
|                          | text chunks or records from external stores matching a query| five relevant papers does not mean the system knows how to    |
|                          | via lexical (BM25) or semantic (dense vector) similarity.   | connect them.                                                 |
+--------------------------+-------------------------------------------------------------+---------------------------------------------------------------+
| 2. Knowledge             | The formal structuring of concepts, entities, facts,        | It is NOT raw text storage. It structures ontology classes,   |
|    Representation        | relations, conditions, and evidence into an attributed      | mathematical symbols, SI dimensions, tensor ranks, and causal |
|                          | property graph: G = (V, E, A, P).                           | directionality.                                               |
+--------------------------+-------------------------------------------------------------+---------------------------------------------------------------+
| 3. Knowledge             | The unification of heterogeneous facts, variables, and      | It is NOT concatenating text chunks in a prompt. It harmonizes|
|    Composition           | equations from multiple sources into a single, dimensionally| units, aligns coordinate systems, and constructs joint coupled|
|                          | consistent system of coupled constraints: F_joint(X) = 0.   | governing equations.                                          |
+--------------------------+-------------------------------------------------------------+---------------------------------------------------------------+
| 4. Knowledge             | Projecting a structural mechanism, formula, or law from a   | It is NOT drawing poetic metaphors. It requires a formal graph|
|    Transfer              | Source Domain (D_S) onto an unfamiliar Target Domain (D_T)  | homomorphism phi: G_S -> G_T that preserves relational        |
|                          | where direct prior documentation does not exist.            | invariants across domain boundaries.                          |
+--------------------------+-------------------------------------------------------------+---------------------------------------------------------------+
| 5. Validation            | Computationally verifying physical, mathematical, and       | It is NOT an LLM saying "this looks correct". It is deterministic|
|                          | boundary consistency via symbolic algebra, unit balance,    | execution in a secure sandbox yielding bit-level proof.       |
|                          | numerical ODE/PDE solvers, and dataset statistical tests.   |                                                               |
+--------------------------+-------------------------------------------------------------+---------------------------------------------------------------+
```

---

## 4. Illustrative Research Example: Solar Electric Vehicle Design (Part 2.5)

To illustrate the technical dependencies and individual contributions of all ten components, consider the user prompt:
> *"Design a lightweight solar-powered electric vehicle for a 75 kg rider, capable of sustaining 25 km/h on flat ground under 1000 W/m² noon solar irradiance."*

```
+------------------------------------+---------------------------------------------------------------------------------------------------------------+
| COMPONENT                          | EXACT CONTRIBUTION TO THE SOLAR EV PROBLEM                                                                    |
+------------------------------------+---------------------------------------------------------------------------------------------------------------+
| [1] Universal Knowledge Reader     | Ingests PV cell efficiency datasheets (21% η_pv), aerodynamic drag coefficients (C_d = 0.6), tire rolling     |
|                                    | resistance data (C_rr = 0.005), and electric motor efficiency curves with exact page coordinates.             |
+------------------------------------+---------------------------------------------------------------------------------------------------------------+
| [2] Scientific Knowledge Graph     | Maps entities: Solar Irradiance, Photovoltaic Area, Motor Torque, Aerodynamic Drag, Rolling Resistance,      |
|                                    | Rider Mass, Frontal Area. Edges capture proportionality and domain tags (Physics, EE, Mech Eng).             |
+------------------------------------+---------------------------------------------------------------------------------------------------------------+
| [3] Research Assistant (Baseline)   | (Control Run) Retrieves raw text chunks and generates an unverified textual estimate without checking if     |
|                                    | available vehicle surface area is physically sufficient to capture required power.                           |
+------------------------------------+---------------------------------------------------------------------------------------------------------------+
| [4] Simple Hypothesis Tester       | Parses the power demand formula: P_req = (C_rr * m * g + 0.5 * rho * C_d * A * v^2) * v. Verifies that all   |
|                                    | terms reduce strictly to SI Watts ([M][L]^2[T]^-3). Checks that efficiency η <= 1.0.                          |
+------------------------------------+---------------------------------------------------------------------------------------------------------------+
| [5] Reasoning System               | Decomposes goal into: Sub-Goal 1 (Calculate mechanical drag at 25 km/h = 6.94 m/s); Sub-Goal 2 (Calculate     |
|                                    | electrical motor demand); Sub-Goal 3 (Calculate solar power generated from 0.8 m^2 roof area).                |
+------------------------------------+---------------------------------------------------------------------------------------------------------------+
| [6] Cross-Domain Composition &     | 1. Composition: Unifies PV generation equation with road load equation: P_pv(A, G) - P_demand(v) / η_drive = 0|
|     Transfer Engine (Central Core) | 2. Feasibility Deficit: Discovers that at 25 km/h, demand is 210 W, but 0.8 m^2 PV yields only 168 W!          |
|                                    | 3. Transfer: Transfers the concept of *hydraulic accumulation / buffer storage* to an electrical battery buffer|
|                                    |    allowing continuous 25 km/h cruising with duty-cycle charging. Checks applicability: electrical battery    |
|                                    |    satisfies energy conservation and safe discharge C-rates.                                                  |
+------------------------------------+---------------------------------------------------------------------------------------------------------------+
| [7] Hypothesis Generator           | Formulates Hypothesis: A 24V 10Ah LiFePO4 battery buffer (weighing 2.5 kg) will bridge the 42 W power deficit  |
|                                    | for 45 minutes of continuous riding while recharging over 2.5 hours of stationary sunlight.                    |
+------------------------------------+---------------------------------------------------------------------------------------------------------------+
| [8] Full Hypothesis Tester         | Executes a Python numerical ODE simulation in Docker sandbox modeling velocity vs. time across a hill-climbing|
|                                    | profile. Confirms battery thermal dissipation is within safe operating limits (< 45°C).                       |
+------------------------------------+---------------------------------------------------------------------------------------------------------------+
| [9] Validated Knowledge Memory     | Commits the validated Solar EV Energy Balance Envelope to memory with parameters: Max Speed 25 km/h, Solar    |
|                                    | Area 0.8 m^2, Buffer 240 Wh. Future investigations cannot reuse this for highway speeds (> 60 km/h).          |
+------------------------------------+---------------------------------------------------------------------------------------------------------------+
| [10] Integrated AXION Platform     | Synthesizes the full interactive engineering report: bill of materials, circuit schematic, KaTeX equations,   |
|                                    | step-by-step build instructions, and interactive Plotly battery discharge curves.                             |
+------------------------------------+---------------------------------------------------------------------------------------------------------------+
```

---

## 5. Comparative Evaluation Methodology & Ablation Studies (Part 8.1)

To demonstrate scientific rigor, AXION will be evaluated across a **3-Way Comparative Matrix** complemented by systematic **Ablation Experiments**:

### 5.1 The Three Core Experimental Conditions
1. **Condition A: Frontier Zero-Shot LLM (Parametric Memory Control):**
   - Direct prompt with no document retrieval or external tools.
   - Tests what the model "knows" from pretraining alone.
2. **Condition B: Conventional RAG Assistant (Component 3 Control):**
   - Dense vector retrieval (`pgvector` HNSW index, top-5 chunks) + prompt stuffing.
   - Represents the state-of-the-art conventional retrieval paradigm.
3. **Condition C: Full AXION Platform (Experimental System):**
   - Knowledge Graph + Goal Decomposition + Cross-Domain Composition & Transfer + Sandbox Validation.

### 5.2 Ablation Study Matrix
To determine which specific sub-mechanisms contribute to AXION's performance, we evaluate four ablated variants of Condition C:
- **Ablation 1 ($C_{\text{no-graph}}$):** AXION without Knowledge Graph (pure vector chunks + transfer prompt).
- **Ablation 2 ($C_{\text{no-transfer}}$):** AXION with Graph and Reasoning, but disabling the Cross-Domain Analogy / Morphism Engine.
- **Ablation 3 ($C_{\text{no-guard}}$):** AXION with Transfer enabled, but disabling the Formal Applicability Guard (allowing unconstrained analogies).
- **Ablation 4 ($C_{\text{no-sandbox}}$):** AXION without computational sandbox testing (pure neuro-symbolic reasoning without empirical execution).

---

## 6. The Initial Research Experiment: The Synthetic Cross-Domain Transfer Trial (Part 8.4)

To provide immediate, falsifiable empirical evidence in early development, we design a focused, highly controlled initial experiment:

### 6.1 Formal Experiment Specification
- **Title:** The Synthetic Cross-Domain Analogy & Applicability Trial (SCAAT-1).
- **Research Hypothesis ($H_1$):** Explicit category-theoretic graph transfer with an Applicability Guard achieves $\ge 80\%$ problem-solving accuracy on cross-domain synthetic tasks and reduces invalid transfer hallucinations to $\le 10\%$, whereas Baseline RAG achieves $\le 30\%$ accuracy and suffers $\ge 60\%$ hallucination rates.
- **Independent Variables:**
  1. System Architecture: Condition A (Zero-Shot), Condition B (Baseline RAG), Condition C (AXION Engine).
  2. Domain Coupling Complexity: 2-Hop vs. 3-Hop cross-domain dependencies.
  3. Ground-Truth Transfer Validity: Positive Cases (Valid Analogy) vs. Negative Cases (Invalid Analogy violating underlying assumptions).
- **Dependent Variables:**
  1. Solution Correctness (Binary $0/1$ against ground-truth derivation).
  2. Unsound Analogy Rejection Rate (Accuracy on negative test cases).
  3. Citation Precision (NLI entailment score of citations).
  4. Execution Wall-Clock Latency and Token Cost.
- **Test Corpus:**
  - 50 formally authored synthetic problems across **Synthetic Nanocrystal Phononics** and **Synthetic Bio-Membrane Transport** (zero pretraining contamination).
  - 25 problems where transfer is physically valid.
  - 25 problems where transfer is superficially attractive but physically invalid (violating linearity or conservation invariants).
- **Control Conditions:**
  - Identical underlying LLM (e.g., Gemini 1.5/2.0 Flash or GPT-4o).
  - Identical temperature ($T = 0.0$) and sampling parameters.
- **Expected Challenges:**
  - Semantic drift when LLMs extract relationships from synthetic texts with unfamiliar terminology.
  - Ensuring the symbolic parser correctly translates synthetic equations without syntax errors.
- **Possible Negative Outcomes & Mitigations:**
  - *Outcome:* Baseline RAG achieves comparable accuracy because the synthetic documents are short enough to fit inside a single context window.
  - *Mitigation:* Inject 20 distractor documents per query to test retrieval under realistic needle-in-a-haystack noise.

---

## 7. Research Risks, Limitations & Evidence Criteria

### 7.1 What Constitutes Valid Scientific Evidence of Improvement?
AXION will claim a genuine research advance **only if**:
1. Condition C demonstrates a statistically significant improvement over Condition B on McNemar's paired test ($p < 0.01$).
2. Condition C demonstrates an effect size Cohen's $d > 0.5$ on multi-hop transfer accuracy.
3. The Applicability Guard achieves $\ge 90\%$ rejection of invalid analogies on negative test sets (proving it prevents false cross-domain hallucinations).

### 7.2 Research Limitations
- AXION does not claim Artificial General Intelligence (AGI) or autonomous laboratory scientific discovery.
- Computational validation in a Docker sandbox tests mathematical, logical, and simulation consistency; it **cannot** replace physical real-world wet-lab experimentation.

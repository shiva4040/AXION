# AXION — Final Eight-Stage System Architecture Specification

**Document Version:** 1.0.0  
**Phase Target:** Phase 0 Architecture Contract  
**System Scope:** Complete AXION Cognitive Architecture (Stages 01–08)  
**Date:** November 19, 2026  

---

## 1. Architectural Vision & Research Premise

AXION is an evidence-grounded scientific knowledge and reasoning platform designed to investigate a central research question:
> **Can an AI system dynamically compose structured, evidence-grounded knowledge from multiple documents and disciplines and apply it to unfamiliar problems more reliably than conventional Retrieval-Augmented Generation (RAG)?**

AXION rejects the assumption that large language models alone possess reliable scientific reasoning or factual ground truth. Instead, AXION establishes an explicit, transparent, multi-stage pipeline where every claim is bound to verbatim provenance, verified for dimensional and physical consistency, checked for boundary constraints, and validated before being accepted as a **verified finding** or emitted in an answer.

```
                                    ┌─────────────────────────────────────────────────────┐
                                    │               USER QUESTION / GOAL                  │
                                    └──────────────────────────┬──────────────────────────┘
                                                               │
                                                               ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ STAGE 01: QUESTION PROCESSING                                                                                           │
│ Deconstructs research query, classifies scientific domains, extracts constraints, units, and declared hypotheses.       │
└───────────────────────────────────────────────┬─────────────────────────────────────────────────────────────────────────┘
                                                │
                                                ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ STAGE 02: KNOWLEDGE ACQUISITION                                                                                         │
│ Acquires permitted documents (APIs, preprints, local PDFs); reads candidate verified findings from Memory.              │
└───────────────────────────────────────────────┬─────────────────────────────────────────────────────────────────────────┘
                                                │
                                                ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ STAGE 03: EVIDENCE EXTRACTION                                                                                           │
│ Extracts atomic claims, conditions, equations, variables, and verbatim provenance pointers with page/chunk anchors.     │
└───────────────────────────────────────────────┬─────────────────────────────────────────────────────────────────────────┘
                                                │
                                                ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ STAGE 04: KNOWLEDGE COMPOSITION                                                                                         │
│ Unifies variables into SI dimensions; harmonizes inter-document relations; maps analogies across distant domains.       │
└───────────────────────────────────────────────┬─────────────────────────────────────────────────────────────────────────┘
                                                │
                                                ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ STAGE 05: REASONING AND CALCULATIONS                                                                                    │
│ Symbolic derivations (SymPy), dimensional analysis (Pint), numerical evaluation, and causal constraint propagation.     │
└───────────────────────────────────────────────┬─────────────────────────────────────────────────────────────────────────┘
                                                │
                                                ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ STAGE 06: INDEPENDENT VERIFICATION                                                                                      │
│ Verbatim quote audit, contradiction checks, boundary guardrails, falsification tests, and abstention decisions.        │
└───────────────────────┬─────────────────────────────────────────────────────────────────┬───────────────────────────────┘
                        │ [If Verified & Generalizable]                                   │ [Validation Passed]
                        ▼                                                                 ▼
┌───────────────────────────────────────────────────────┐       ┌─────────────────────────────────────────────────────────┐
│ STAGE 07: VERIFIED FINDINGS MEMORY                    │       │ STAGE 08: ANSWER GENERATION                             │
│ Writes verified findings with audit trails,           │       │ Generates fully attributed, evidence-grounded answer;   │
│ conditions, and applicability bounds for future reuse.│       │ abstains if evidence is insufficient or contradictory.  │
└───────────────────────────────────────────────────────┘       └─────────────────────────────────────────────────────────┘
```

---

## 2. The Eight Pipeline Stages in Detail

### Stage 01: Question Processing
- **Input:** Raw scientific/engineering question string $Q$.
- **Operations:**
  1. *Lexical & Semantic Deconstruction:* Extract technical nouns, physical quantities, target variables, and governing assumptions.
  2. *Domain Classification:* Identify participating domains (e.g., `physics:electromagnetism`, `engineering:thermodynamics`).
  3. *Goal Specification:* Classify intent into `EXPLANATION`, `QUANTITATIVE_CALCULATION`, `ANALOGICAL_TRANSFER`, `HYPOTHESIS_EVALUATION`, or `FEASIBILITY_CHECK`.
  4. *Constraint Parsing:* Detect explicit boundary conditions, specified numerical values, and required units.
- **Output:** Structured `QuestionSpec` payload containing canonical target variables, required outputs, and identified domain labels.

### Stage 02: Knowledge Acquisition
- **Input:** `QuestionSpec`, search parameters, active memory state.
- **Operations:**
  1. *External Discovery:* Dispatches targeted queries to active connectors (arXiv, PubMed, Crossref, OpenAlex, local documents).
  2. *License & Access Filter:* Filters out inaccessible or restricted full-text assets, accepting metadata/abstracts when full text is barred.
  3. *Memory Reading:* Concurrently queries **Stage 07 (Verified Findings Memory)** for previously stored findings whose domain or structural signature matches the query concepts.
  4. *Deduplication & Provenance Stamping:* Assigns canonical hashes and `ProvenancePointer` records to all retrieved chunks.
- **Output:** Acquired `DocumentBundle` (external texts) and `CandidateMemoryBundle` (stored verified findings).

### Stage 03: Evidence Extraction
- **Input:** Acquired text chunks and candidate memory findings.
- **Operations:**
  1. *Atomic Claim Extraction:* Segments continuous prose into discrete factual assertions, definitions, or experimental measurements.
  2. *Condition & Limitation Tagging:* Extracts qualifiers ("only when $T > 300\text{ K}$", "assuming laminar flow", "for low Mach numbers").
  3. *Mathematical & Physical Extraction:* Identifies explicit equations, variables, SI units, and declared parameter values.
  4. *Epistemic Attribution:* Labels each extracted item with an `EpistemicTier` (`FACT_DOCUMENTED`, `HYPOTHESIS_FORMAL`, `CONJECTURE`) and anchors it to exact document ID, chunk ID, and page offsets.
- **Output:** List of `ExtractedClaim` and `ExtractedEquation` entities with verbatim provenance.

### Stage 04: Knowledge Composition
- **Input:** Extracted claims, equations, and retrieved memory findings across multiple documents/domains.
- **Operations:**
  1. *Variable Harmonization:* Resolves naming discrepancies across authors (e.g., matching $V$, $\Delta \Phi$, and $u$ to electrical potential $[M][L]^2[T]^{-3}[I]^{-1}$).
  2. *SI Base Dimensional Alignment:* Validates physical dimensionality of all participating variables.
  3. *Multi-Document Relation Graph Construction:* Links premises from Document A with consequences in Document B.
  4. *Cross-Domain Structural Alignment:* Computes second-order relational isomorphism (e.g., mapping effort/flow/resistance across hydraulic and thermal domains).
- **Output:** Composed `KnowledgeSystem` containing harmonized variables, coupled equations, unified active assumptions, and active boundary constraints.

### Stage 05: Reasoning and Calculations
- **Input:** Composed `KnowledgeSystem`.
- **Operations:**
  1. *Symbolic Derivation:* Uses SymPy in a sandboxed execution environment to solve coupled algebraic or differential systems.
  2. *Dimensional Verification:* Uses Pint to verify that all mathematical operations preserve dimensional homogeneity.
  3. *Numerical Calculation:* Computes quantitative outputs, parameter sweeps, or equilibrium points with explicit floating-point precision bounds.
  4. *Causal Dependency Tracing:* Builds a Directed Acyclic Graph (DAG) of inferential steps connecting source premises to derived conclusions.
- **Output:** `ReasoningTrace` containing symbolic solutions, numerical results, and the inferential proof chain.

### Stage 06: Independent Verification
- **Input:** `ReasoningTrace`, `KnowledgeSystem`, and source `DocumentBundle`.
- **Operations:**
  1. *Verbatim Citation & Quotation Audit:* Verifies that every factual claim matches an exact substring in the source documents.
  2. *Contradiction Detection:* Cross-checks extracted claims for mutual negation or mutually exclusive parameter bounds across sources.
  3. *Applicability Guardrail Check:* Evaluates whether the problem's operational parameters fall strictly within the declared validity envelope of all used equations and memory findings.
  4. *Falsification & Unit Checks:* Tests calculations against physical invariants (e.g., conservation of energy, non-negative absolute temperature).
  5. *Abstention Engine:* If evidence is missing, conflicting without resolution, or outside applicability limits, issues a formal refusal to answer (`ABSTAIN_INSUFFICIENT_EVIDENCE`).
- **Output:** `VerificationAuditReport` with verdicts: `VERIFIED`, `REJECTED`, or `ABSTAIN`.

### Stage 07: Verified Findings Memory
- **Dual Functionality:**
  - **Memory Reading (Invoked in Stage 02 & 04):** Supplies previously stored verified findings to the acquisition and composition stages. Every read finding must pass the Stage 06 Applicability Guard before entering reasoning.
  - **Memory Writing (Invoked after Stage 06):**
    - Stores newly verified knowledge only after passing Stage 06 verification.
    - Records finding statement, source evidence, mathematical formulation, explicit assumptions, operational envelope, and verification audit ID.
    - Terminology standard: All stored items are designated **"Verified Findings"**, never "proven scientific facts".
    - Dependency & Invalidation Tracking: If a source document or foundational assumption is later revoked, all downstream dependent findings are automatically marked `INVALIDATED`.
- **Output:** Persistent `VerifiedFinding` record with unique UUID.

### Stage 08: Answer Generation
Stage 08 possesses **two distinct implementations** across the project lifecycle:
- **Phase 1 Implementation (Minimal Answer Generator):**
  - Generates concise, structured answers directly reflecting Stage 05/06 outputs.
  - Formats: Direct Answer, Supporting Quotations with Document/Page Citations, Explicit Assumptions, and Verification Status.
  - Mandatory behavior: Emits standardized abstention notices when Stage 06 returns `ABSTAIN`.
  - Enables immediate, end-to-end evaluation against plain RAG starting in Phase 1.
- **Phase 5 Implementation (Complete Answer Generation System):**
  - Comprehensive scientific report synthesis.
  - Includes interactive step-by-step mathematical derivations, interactive 3D visualizations, sensitivity analysis, epistemic uncertainty intervals, and complete bibliographic provenance trees.

---

## 3. Mapping Existing Components to the Eight Stages

The existing codebase contains ten modular components implemented during initial engineering phases. They map cleanly into the target eight-stage architecture without module deletion:

| Existing AXION Component | Existing Python Module | Target Stage Mapping |
| :--- | :--- | :--- |
| **Component 1: PDF Research Reader** | `axion/ingestion/` | **Stage 02 & 03:** Document chunking, text extraction, page tracking. |
| **Component 2: Scientific Knowledge Graph**| `axion/knowledge_graph/`| **Stage 03 & 04:** Concept/relation storage and multi-document graph linking. |
| **Component 3: Research Assistant (Baseline)**| `axion/baseline/` | **Baseline Comparison:** Conventional RAG evaluator paired against AXION. |
| **Component 4: Simple Hypothesis Tester**| `axion/simple_tester/` | **Stage 06:** Statistical correlation and elementary falsification tests. |
| **Component 5: Reasoning System** | `axion/reasoning/` | **Stage 05:** Causal DAG construction, forward/backward chaining. |
| **Component 6: Cross-Domain Transfer Engine**| `axion/transfer/` | **Stage 04:** Variable harmonization, SMT structural alignment, applicability guard. |
| **Component 7: Hypothesis Generator** | `axion/hypothesis/` | **Stage 01 & 04:** Abductive candidate mechanism generation. |
| **Component 8: Full Hypothesis Tester** | `axion/hypothesis_tester/`| **Stage 05 & 06:** Sandboxed symbolic, numerical, and ODE validation. |
| **Component 9: Validated Knowledge Memory**| `axion/knowledge_memory/`| **Stage 07:** Persistent verified findings storage and invalidation engine. |
| **Component 10: User Interface Prototype**| `frontend/` & `axion/api/` | **Stage 08 & Interface:** Research query submission and answer visualization. |
| **Acquisition Layer (8 Connectors)** | `axion/acquisition/` | **Stage 02:** External multi-source literature and dataset discovery. |

---

## 4. Architectural Invariants & Non-Negotiable Contracts

1. **No Unearned Information Advantage:** In all benchmark evaluations, the Plain RAG Baseline and the AXION Pipeline must receive identical document sets, identical query strings, and identical underlying LLM models.
2. **Untrusted Data Boundary:** All external documents, user uploads, and web search results are treated as untrusted data. They must pass AST/Regex sanitization and never be interpolated directly into prompts as instructions.
3. **Strict Epistemic Distinction:** System outputs must never label an unverified hypothesis or web conjecture as a verified finding.
4. **Mandatory Citation Anchoring:** Every statement asserted as fact must carry a verified `ProvenancePointer` referencing specific document pages or chunks.

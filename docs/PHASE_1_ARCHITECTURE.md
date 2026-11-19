# AXION — Phase 1 Pipeline Architecture Specification
## Eight-Stage Evidence-Grounded Reasoning Pipeline

**Document Version:** 1.0.0  
**Phase:** Phase 1 — Foundation & Working Pipeline  
**Scope:** Core Architecture, Data Contracts, Stage Interfaces, and Provenance Lifecycle  
**Date:** November 19, 2026  
**Status:** Authoritative Architectural Reference  

---

## 1. High-Level Architectural Overview

AXION is engineered as an eight-stage sequential pipeline designed to acquire, extract, compose, reason over, independently verify, and generate answers backed by verifiable provenance.

```
                      ┌─────────────────────────────────────────┐
                      │            USER RAW QUERY               │
                      └────────────────────┬────────────────────┘
                                           │
                                           ▼
                      ┌─────────────────────────────────────────┐
                      │    STAGE 01: QUESTION PROCESSING        │
                      │  Intent, Target Vars, Domains, Bounds   │
                      └────────────────────┬────────────────────┘
                                           │ QuestionSpec
                                           ▼
                      ┌─────────────────────────────────────────┐
                      │    STAGE 02: KNOWLEDGE ACQUISITION      │
                      │  Local Vector DB, Corpus, Verified Mem  │
                      └────────────────────┬────────────────────┘
                                           │ AcquisitionPayload
                                           ▼
                      ┌─────────────────────────────────────────┐
                      │    STAGE 03: EVIDENCE EXTRACTION        │
                      │  Atomic Claims, Snippets, Conditions    │
                      └────────────────────┬────────────────────┘
                                           │ List[ExtractedClaim]
                                           ▼
                      ┌─────────────────────────────────────────┐
                      │    STAGE 04: KNOWLEDGE COMPOSITION      │
                      │ Harmonization, Equation Coupling, Bounds│
                      └────────────────────┬────────────────────┘
                                           │ ComposedSystem
                                           ▼
                      ┌─────────────────────────────────────────┐
                      │     STAGE 05: REASONING & CALCULATION   │
                      │  SymPy Substitution, DAG, SI Units      │
                      └────────────────────┬────────────────────┘
                                           │ ReasoningTrace
                                           ▼
                      ┌─────────────────────────────────────────┐
                      │   STAGE 06: INDEPENDENT VERIFICATION    │
                      │ Verbatim Quotes, Contradictions, Bounds │
                      └────────────────────┬────────────────────┘
                                           │ VerificationAuditReport
                                           ▼
                      ┌─────────────────────────────────────────┐
                      │   STAGE 07: VERIFIED MEMORY GATEKEEPER  │
                      │ Gate: Only stores if VERIFIED == True   │
                      └────────────────────┬────────────────────┘
                                           │
                                           ▼
                      ┌─────────────────────────────────────────┐
                      │     STAGE 08: ANSWER GENERATION         │
                      │ Direct Answers with Quotes OR Abstain   │
                      └─────────────────────────────────────────┘
```

---

## 2. Stage Responsibilities and Data Contracts

### 2.1 Stage 01: Minimal Question Processing (`axion/pipeline/stage01_question.py`)
- **Input:** Raw query string `raw_query: str`, optional `document_id`.
- **Output:** Strongly typed `QuestionSpec`.
- **Responsibilities:**
  - Classifies user intent (`FACTUAL_LOOKUP`, `MULTI_HOP_CALCULATION`, `COMPARISON_DISPUTE`, `FEASIBILITY_CHECK`).
  - Detects participating disciplinary domain tags (`physics:electromagnetism`, `materials:thermoelectrics`, etc.).
  - Extracts target output variables (e.g. `kappa_tot`, `ZT`, `u_E`).
  - Extracts stated numerical boundary constraints and operational parameters.

### 2.2 Stage 02: Knowledge Acquisition Coordinator (`axion/pipeline/stage02_acquisition.py`)
- **Input:** `QuestionSpec`, `top_k: int = 5`, `min_similarity: float = 0.10`.
- **Output:** `AcquisitionPayload`.
- **Responsibilities:**
  - Coordinates retrieval across:
    1. Direct document attachments (`document_id`).
    2. Local dense vector retrieval / benchmark corpus passages.
    3. Validated Knowledge Memory (`ValidatedKnowledgeMemory`) for reusable verified findings.
  - Enforces document-level diversification in top-$k$ selection.
  - Stamps every chunk with a strict `ProvenancePointer`.

### 2.3 Stage 03: Evidence Extraction (`axion/pipeline/stage03_extraction.py`)
- **Input:** `AcquisitionPayload`.
- **Output:** `List[ExtractedClaim]`.
- **Responsibilities:**
  - Performs sentence and clause segmentation on acquired chunk text.
  - Parses mathematical expressions, constitutive equations, and numerical constants.
  - Extracts operational governing conditions (e.g. `T < 340 K`, `sub_breakdown_regime`).
  - Enforces character-exact verbatim quote anchoring: every extracted snippet is verified as an exact substring of the parent chunk text.

### 2.4 Stage 04: Knowledge Composition (`axion/pipeline/stage04_composition.py`)
- **Input:** `List[ExtractedClaim]`, `QuestionSpec`.
- **Output:** `ComposedSystem`.
- **Responsibilities:**
  - Harmonizes variable names across disparate source documents (e.g. matching `S` and `Seebeck_coeff`).
  - Couples complementary equations across documents into a unified multi-hop system.
  - Unions governing assumptions and detects regime contradictions (e.g. laminar vs. turbulent flow conflicts).

### 2.5 Stage 05: Reasoning and Calculations (`axion/pipeline/stage05_reasoning.py`)
- **Input:** `ComposedSystem`.
- **Output:** `ReasoningTrace`.
- **Responsibilities:**
  - Constructs a topological dependency DAG over variables and governing equations.
  - Performs namespace-safe symbolic substitution using SymPy.
  - Validates dimensional consistency using SI unit algebra.
  - Handles missing variable failures gracefully, halting if required premises are absent.

### 2.6 Stage 06: Independent Verification Guard (`axion/pipeline/stage06_verification.py`)
- **Input:** `ReasoningTrace`, `ComposedSystem`, `AcquisitionPayload`, `QuestionSpec`.
- **Output:** `VerificationAuditReport`.
- **Responsibilities:**
  - Four independent audit passes:
    1. **Verbatim Quotation Audit:** Verifies byte-for-byte that every cited snippet exists in the original source document chunk.
    2. **Contradiction Detection:** Checks for conflicting parameters or opposing physical regimes.
    3. **Mathematical Validation:** Confirms numerical calculations evaluate without error and no target variables remain unresolved.
    4. **Evidence Sufficiency:** Checks that required premises are present; if missing, emits `ABSTAIN_INSUFFICIENT_EVIDENCE`.
  - Verdicts: `VERIFIED`, `PARTIALLY_SUPPORTED`, `ABSTAIN_INSUFFICIENT_EVIDENCE`, `ABSTAIN_CONTRADICTORY_EVIDENCE`, `INVALID_REASONING`, `INVALID_PROVENANCE`, `EXECUTION_FAILURE`.

### 2.7 Stage 07: Verified Findings Memory (`axion/pipeline/stage07_memory.py`)
- **Input:** `VerificationAuditReport`, `ReasoningTrace`, `ComposedSystem`, `QuestionSpec`.
- **Output:** Stored `ValidatedFinding` or `None`.
- **Responsibilities:**
  - **Strict Gatekeeper:** Findings are written to memory if and only if `audit_report.verdict == "VERIFIED"`.
  - Performs deduplication against existing stored findings.
  - Preserves full provenance lineage back to primary literature.

### 2.8 Stage 08: Minimal Answer Generation (`axion/pipeline/stage08_answer.py`)
- **Input:** `VerificationAuditReport`, `ReasoningTrace`, `ComposedSystem`, `QuestionSpec`, `StageExecutionLog` list.
- **Output:** `PipelineAnswerResponse`.
- **Responsibilities:**
  - Dispatches either an evidence-backed structured answer or an explicit abstention notice.
  - Formats direct citations (`[Document Title, Page N]`) and includes verbatim quotes in `supporting_evidence`.
  - If abstaining, explains the exact refusal reason (missing parameters, unresolved conflicts, or boundary violations).

---

## 3. Provenance Flow End-to-End

```
Source Document (PDF/Text)
    │
    ▼
AcquiredChunk
  - document_id: "doc-syn-mat-002"
  - chunk_id: "doc-syn-mat-002-chk-001"
  - text_content: "...lattice thermal conductivity is kappa_lat = 1.65 W/(m*K)..."
    │
    ▼
ExtractedClaim
  - statement: "lattice thermal conductivity is kappa_lat = 1.65 W/(m*K)"
  - provenance: ProvenancePointer(
      document_id="doc-syn-mat-002",
      chunk_id="doc-syn-mat-002-chk-001",
      page_number=1,
      extracted_snippet="lattice thermal conductivity is kappa_lat = 1.65 W/(m*K)"
    )
    │
    ▼
SupportingEvidenceItem
  - citation: "doc-syn-mat-002, Page 1"
  - verbatim_quote: "lattice thermal conductivity is kappa_lat = 1.65 W/(m*K)"
  - provenance: ProvenancePointer(...)
    │
    ▼
PipelineAnswerResponse
  - direct_answer: "Based on verified primary evidence in materials:thermoelectrics: ..."
  - supporting_evidence: [SupportingEvidenceItem, ...]
```

---

## 4. Pipeline Execution & Timeout Management

- **Central Coordinator (`PipelineCoordinator`):** Manages end-to-end execution across all 8 stages.
- **Timeout Budget:** Per-query timeout enforcement (default: 10.0 seconds) via `asyncio.wait_for`.
- **Telemetry:** Appends structured `StageExecutionLog` records for every stage recording stage index, duration, status, and diagnostic summary.

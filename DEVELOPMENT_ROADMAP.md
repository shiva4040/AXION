# AXION — Development Roadmap & Phased Implementation Plan

**Document Version:** 2.0.0  
**Date:** November 18, 2026  
**Status:** Approved for Phase 0 Specification  
**Project:** AXION — Universal Knowledge and Cross-Domain Intelligence Platform  

---

## 1. Roadmap Principles & Verification Gates

The development of AXION is structured across six strictly sequential phases. Progress between phases is governed by formal **Verification Gates**: no phase may begin until the preceding phase satisfies 100% of its automated tests, architectural reviews, and acceptance criteria.

```
[ Phase 0: Planning & Design ] ---> [ Phase 1: Knowledge Foundation ] ---> [ Phase 2: Reasoning Foundation ]
              |                                     |                                    |
              v                                     v                                    v
[ Phase 5: Complete AXION ]   <--- [ Phase 4: Validation & Memory ]   <--- [ Phase 3: Core Research Engine ]
```

---

## 2. Detailed Six-Phase Implementation Specifications

### Phase 0 — Planning, Architecture & Research Design
- **Objectives:** Establish the complete theoretical, architectural, database, benchmark, and security foundations for AXION. Maintain a clean-slate repository without premature coding.
- **Components Involved:** All 10 Components (Design & Specification Level).
- **Milestones & Tasks:**
  - *M0.1:* Complete workspace audit & environment verification.
  - *M0.2:* Author all 10 core planning and specification documents.
  - *M0.3:* Formulate the 15 evaluation metrics and synthetic benchmark universes.
  - *M0.4:* Establish Architecture Decision Records (ADRs) and Risk Register.
- **Dependencies:** None (Initiating Phase).
- **Deliverables:** `AXION_PROJECT_UNDERSTANDING.md`, `PRODUCT_SPECIFICATION.md`, `SYSTEM_ARCHITECTURE.md`, `RESEARCH_PLAN.md`, `BENCHMARK_DESIGN.md`, `DATABASE_DESIGN.md`, `DEVELOPMENT_ROADMAP.md`, `ARCHITECTURE_DECISION_RECORDS.md`, `RISK_REGISTER.md`, `PHASE_0_COMPLETION_REPORT.md`.
- **Tests & Verification:** Cross-document consistency verification across all ten components.
- **Acceptance Criteria:** 100% of Phase 0 checklist approved by Project Owner.
- **Risks:** Ambiguity in cross-domain transfer algorithms (Mitigated via ADR-007).
- **Estimated Complexity:** Moderate (Conceptual & Architectural).
- **Completion Condition:** Formal sign-off and explicit user authorization to initiate Phase 1.

---

### Phase 1 — Knowledge Foundation
- **Objectives:** Implement high-speed document ingestion with bounding-box coordinate extraction, build the relational Knowledge Graph schema, and establish the conventional RAG baseline (Control System).
- **Components Involved:**
  - Component 1: Universal Knowledge Reader.
  - Component 2: Scientific & Cross-Domain Knowledge Graph.
  - Component 3: Research Assistant Baseline.
- **Milestones & Tasks:**
  - *M1.1 (Environment & Scaffolding):* Setup Python 3.14 environment (`pyproject.toml`, FastAPI, Pydantic, SQLAlchemy 2.0, Alembic, PyMuPDF, pgvector, pytest), Docker Compose for PostgreSQL 16 + `pgvector`.
  - *M1.2 (Component 1):* Implement PyMuPDF parser with text, table, equation, and coordinate extraction (`[x0, y0, x1, y1]`). Implement semantic heading-aware chunker.
  - *M1.3 (Component 2):* Apply Alembic migrations for `graph_nodes`, `graph_edges`, and `edge_provenance`. Implement Pydantic entity/relation extraction pipeline. Implement in-memory NetworkX serialization.
  - *M1.4 (Component 3):* Implement dense vector embedding generator and `pgvector` HNSW index. Expose `/api/v1/baseline/query` endpoint with raw citation formatting.
- **Dependencies:** Phase 0 completion.
- **Deliverables:** Working backend ingestion service, populated PostgreSQL database with vector indices, working `/api/v1/baseline/query` control endpoint.
- **Tests:** Pytest unit tests for PDF extraction, chunk coordinate accuracy, vector retrieval recall, and graph insertion.
- **Acceptance Criteria:**
  - PDF parser extracts 20-page document in $\le 2.0$ seconds with exact bounding boxes.
  - Baseline RAG achieves $\ge 85\%$ retrieval recall on standard factual benchmark queries.
  - Zero cross-talk between Baseline RAG and Knowledge Graph algorithms.
- **Risks:** PDF extraction noise on multi-column layouts (Mitigated via PyMuPDF structural block sorting).
- **Estimated Complexity:** High (Foundational Data Pipeline).

---

### Phase 2 — Reasoning Foundation
- **Objectives:** Implement deterministic symbolic equation parsing, physical dimensional analysis (SI units), and hierarchical goal decomposition DAGs.
- **Components Involved:**
  - Component 4: Simple Hypothesis Tester.
  - Component 5: Reasoning System.
- **Milestones & Tasks:**
  - *M2.1 (Component 4):* Implement `SymPy` formula parser and algebraic equivalence checker ($LHS - RHS \equiv 0$). Implement SI dimensional analysis engine verifying base unit homogeneity ($[M]^a [L]^b [T]^c [I]^d$).
  - *M2.2 (Component 5):* Implement goal decomposition into Directed Acyclic Graphs (DAGs) of sub-problems. Implement multi-hop pathfinding through the Knowledge Graph using recursive SQL CTEs and NetworkX. Implement contradiction detector between competing source edges.
- **Dependencies:** Phase 1 (requires working Knowledge Graph and ingested chunks).
- **Deliverables:** `/api/v1/validation/test-simple` endpoint, `/api/v1/reasoning/decompose` endpoint, reasoning DAG visualization data models.
- **Tests:** Unit tests verifying that unit mismatches (e.g. adding Joules to Watts) are 100% rejected; tests verifying DAG acyclicity and multi-hop premise traversal.
- **Acceptance Criteria:**
  - Simple Tester achieves 100% accuracy on detecting dimensional inconsistencies in test equations.
  - Reasoning System decomposes complex queries into valid DAGs with $\ge 85\%$ premise coverage.
- **Risks:** LaTeX-to-SymPy parsing syntax errors (Mitigated via pre-parser sanitization rules).
- **Estimated Complexity:** Moderate-to-High (Neuro-Symbolic Logic).

---

### Phase 3 — Core Research Engine (The Central Breakthrough)
- **Objectives:** Implement the Cross-Domain Knowledge Composition & Transfer Engine and the Hypothesis Generator. This is the central research milestone of AXION.
- **Components Involved:**
  - Component 6: Cross-Domain Knowledge Composition & Transfer Engine.
  - Component 7: Hypothesis Generator.
- **Milestones & Tasks:**
  - *M3.1 (Component 6.1 - Analogy Discovery):* Implement Weisfeiler-Lehman (WL) graph kernel isomorphism matching across disparate domain subgraphs.
  - *M3.2 (Component 6.2 - Composition Engine):* Implement multi-domain variable harmonization, unified variable registry, and joint equation coupling.
  - *M3.3 (Component 6.3 - Applicability Guard):* Implement formal invariant and assumption verification (Linearity, Conservation, Continuum scale, Boundary limits) with automated rejection filter.
  - *M3.4 (Component 7):* Implement structured hypothesis synthesis: `[Premise] -> [Mechanism] -> [Prediction] -> [Counter-Evidence] -> [Test Plan]`.
- **Dependencies:** Phase 2 (requires reasoning DAGs and unit testing engine).
- **Deliverables:** `/api/v1/transfer/find-analogies` endpoint, `/api/v1/transfer/check-applicability` endpoint, `/api/v1/hypothesis/generate` endpoint.
- **Tests:** Benchmark evaluation on Tier 1 Synthetic Universes (testing positive transfer and negative unsound transfer rejection).
- **Acceptance Criteria:**
  - Applicability Guard achieves $\ge 90\%$ rejection of invalid analogies in negative test sets.
  - Cross-domain composition successfully harmonizes multi-domain variables with 100% dimensional consistency.
- **Risks:** Unsound analogy hallucination (Mitigated via strict Applicability Guard).
- **Estimated Complexity:** Very High (Core Theoretical Research).

---

### Phase 4 — Empirical Validation & Memory
- **Objectives:** Implement the secure Docker container execution sandbox for numerical simulations/data tests, and the immutable validated knowledge memory tier.
- **Components Involved:**
  - Component 8: Full Hypothesis Tester.
  - Component 9: Validated Knowledge Memory.
- **Milestones & Tasks:**
  - *M4.1 (Component 8):* Implement Docker SDK container runner with dropped privileges, `--network none`, read-only root, 128 MB RAM tmpfs, and 15s watchdog timer. Pre-install scientific runtime (NumPy, SciPy, SymPy, Pandas, Matplotlib).
  - *M4.2 (Component 9):* Implement append-only PostgreSQL ledger (`validated_findings`) with SHA-256 content hashes. Implement operational boundary envelope storage (parameter intervals). Implement `check_applicability(finding_id, target_context)` re-use guard.
- **Dependencies:** Phase 3 (requires generated hypotheses).
- **Deliverables:** Containerized execution daemon, `/api/v1/validation/test-sandbox` endpoint, `/api/v1/memory/findings` endpoint.
- **Tests:** Security penetration tests (attempting network egress and host filesystem access from within sandbox); boundary envelope re-use unit tests.
- **Acceptance Criteria:**
  - Zero security escapes from container sandbox; 100% of network attempts blocked.
  - Validated findings correctly committed and blocked from re-use outside valid parameter envelopes.
- **Risks:** Container spin-up latency (Mitigated via pre-warmed container worker pool).
- **Estimated Complexity:** High (System Security & Container Orchestration).

---

### Phase 5 — Integrated Platform, Benchmarking & Launch
- **Objectives:** Integrate all ten components into the unified React research cockpit UI, execute the 3-way comparative benchmark (Zero-Shot vs. Baseline RAG vs. AXION) across all 15 metrics, and produce the final empirical research report.
- **Components Involved:**
  - Component 10: Complete AXION Intelligence Platform.
- **Milestones & Tasks:**
  - *M5.1 (Frontend UI):* Build all 11 workspace sections in React 19 + TypeScript + Tailwind CSS. Integrate Cytoscape.js for knowledge graph visualization, Monaco code editor, Plotly simulation plots, and PDF viewer with bounding-box highlights.
  - *M5.2 (Benchmarking Harness):* Ingest 100 benchmark problems (50 Synthetic, 50 Real-World). Execute automated 3-way evaluation across Condition A, Condition B, and Condition C. Compute all 15 evaluation metrics and statistical tests ($p$-value, Cohen's $d$).
  - *M5.3 (Final Research Report & Release):* Compile `BENCHMARK_RESULTS.md` and format research paper manuscript.
- **Dependencies:** Phases 1–4 complete.
- **Deliverables:** Complete, self-hosted Docker Compose application, automated benchmark suite, empirical research paper.
- **Tests:** Full end-to-end integration tests across all 11 UI views; automated benchmark test suite.
- **Acceptance Criteria:**
  - AXION achieves statistically significant higher problem-solving accuracy ($p < 0.01$) and lower hallucination rate ($\le 5\%$) compared to Baseline RAG on multi-domain tasks.
  - All 11 workspace sections operate seamlessly with responsive sub-second interactions.
- **Risks:** UI state management complexity across 11 views (Mitigated via decoupled Zustand stores).
- **Estimated Complexity:** High (Full-Stack Integration & Empirical Science).

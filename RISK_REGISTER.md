# AXION — Project Risk Register

**Document Version:** 1.0.0  
**Date:** November 18, 2026  
**Status:** Approved Phase 0 Baseline  
**Project:** AXION — Universal Knowledge and Cross-Domain Intelligence Platform  

---

## 1. Risk Management Framework

Risks in AXION are categorized across seven operational dimensions:
1. **Technical Architecture Risks (TR)**
2. **AI & Scientific Research Risks (RR)**
3. **Data Quality & Provenance Risks (DR)**
4. **Integration & Subsystem Risks (IR)**
5. **Performance & Scalability Risks (PR)**
6. **Security & Sandbox Isolation Risks (SR)**
7. **Resource, Cost & API Quota Risks (CR)**

### Scoring Criteria:
- **Probability:** Low (1), Medium (2), High (3)
- **Impact:** Low (1), Medium (2), High (3), Critical (4)
- **Risk Score:** $\text{Probability} \times \text{Impact}$ (Scale: 1 to 12)
  - **1–3:** Low Risk (Monitor)
  - **4–6:** Moderate Risk (Mitigate actively)
  - **7–12:** Critical Risk (Immediate architectural guardrails required)

---

## 2. Comprehensive Risk Matrix

```
+---------+----------------------------------------------+------+----+-------+-------------+
| RISK ID | TITLE                                        | PROB | IMP| SCORE | STATUS      |
+---------+----------------------------------------------+------+----+-------+-------------+
| TR-01   | Graph Extraction Noise & Entity Duplication  | High | High | 9   | ACTIVE      |
| TR-02   | Symbolic & Unit Dimensional Parser Brittleness| Med  | Med  | 4   | ACTIVE      |
| RR-01   | Unsound Analogy Hallucination (False Transfer)| High | Crit | 12  | MITIGATING  |
| RR-02   | Pretraining Data Contamination in Benchmarks | High | Crit | 12  | MITIGATED   |
| RR-03   | Baseline RAG Outperforming AXION on Simple Qs | Med  | Low  | 2   | ACCEPTED    |
| DR-01   | Ingesting Untrusted / Conflicting Data Sources| Med  | High | 6   | ACTIVE      |
| DR-02   | PDF Complex Table / Math Formula Extraction Loss| High | Med  | 6   | ACTIVE      |
| IR-01   | Docker Sandbox Latency Degrading User Experience| Med  | Med  | 4   | ACTIVE      |
| IR-02   | External LLM Provider API Downtime & Rate Limits| Med  | High | 6   | MITIGATED   |
| PR-01   | Multi-Hop Recursive SQL Graph Traversal Bottleneck| Low  | High | 3   | MONITORING  |
| PR-02   | Memory Bloat from In-Memory NetworkX Graphs   | Med  | Med  | 4   | MONITORING  |
| SR-01   | Arbitrary Code Execution / Host Escape in Sim | Low  | Crit | 4   | MITIGATING  |
| SR-02   | Prompt Injection via Ingested Untrusted Docs  | High | High | 9   | ACTIVE      |
| CR-01   | Excessive LLM Token Consumption in Graph Extr | High | Med  | 6   | ACTIVE      |
+---------+----------------------------------------------+------+----+-------+-------------+
```

---

## 3. Detailed Risk Profiles & Action Plans

### 3.1 Technical Architecture Risks

#### [TR-01] Graph Extraction Noise & Entity Duplication
- **Risk Score:** 9 (Probability: High, Impact: High)
- **Description:** Unconstrained LLM extraction from heterogeneous documents creates fragmented entity names (e.g., "Seebeck effect", "Seebeck coefficient", "thermoelectric voltage") and noisy relation labels ("is related to", "affects"), turning the Knowledge Graph into an un-traversable hairball.
- **Mitigation:**
  - Enforce a formal scientific entity ontology and typed relationship taxonomy (`EntityTypes`: `Concept`, `Principle`, `Parameter`, `Constraint`, `Equation`, `Material`; `RelationTypes`: `governed_by`, `proportional_to`, `requires`, `inhibits`).
  - Implement an entity normalization step utilizing string distance algorithms and embedding clustering to canonicalize names before node insertion.
- **Owner:** Data Engineer / Backend Architect.
- **Status:** Active (Guardrails designed in `SYSTEM_ARCHITECTURE.md`).

#### [TR-02] Symbolic & Unit Dimensional Parser Brittleness
- **Risk Score:** 4 (Probability: Medium, Impact: Medium)
- **Description:** Equations extracted from natural text or OCR may have syntax ambiguities (e.g., missing multiplication signs, conflicting variable notations), causing `SymPy` parsing exceptions in Component 4.
- **Mitigation:**
  - Build a sanitization pre-parser that standardizes LaTeX into SymPy-compatible symbolic strings.
  - Gracefully degrade: if symbolic parsing fails, flag the equation as unverified and fall back to numerical evaluation rather than halting the reasoning engine.
- **Status:** Active.

---

### 3.2 AI & Scientific Research Risks

#### [RR-01] Unsound Analogy Hallucination (False Cross-Domain Transfer)
- **Risk Score:** 12 (Probability: High, Impact: Critical)
- **Description:** LLMs are prone to drawing poetic or superficial analogies (e.g., equating electrical resistance to social resistance) that possess zero physical validity, resulting in absurd or dangerous cross-domain engineering recommendations.
- **Mitigation:**
  - Establish the **Formal Applicability Guard** in Component 6.
  - Transfer is strictly prohibited unless the source principle's underlying mathematical assumptions (conservation laws, linearity, continuum scale, boundary stability) are proven to be satisfied in the target domain.
  - Enforce that all transferred models must pass empirical validation in Component 4 or 8 before reaching Validated Memory.
- **Status:** Mitigating (Formalized in `RESEARCH_PLAN.md`).

#### [RR-02] Pretraining Data Contamination in Research Evaluation
- **Risk Score:** 12 (Probability: High, Impact: Critical)
- **Description:** If benchmarks use published scientific papers, frontier LLMs will succeed simply by recalling memorized text from their pretraining corpora, invalidating claims of novel cross-domain reasoning.
- **Mitigation:**
  - Author **Synthetic Scientific Universes** with novel, counterfactual physical laws and constants.
  - Guaranteed zero-contamination: the model cannot possess parametric memory of these synthetic laws, proving that any correct multi-hop deduction was synthesized from retrieved context.
- **Status:** Fully Mitigated (Designed in `BENCHMARK_DESIGN.md`).

#### [RR-03] Baseline RAG Outperforming AXION on Simple Single-Domain Queries
- **Risk Score:** 2 (Probability: Medium, Impact: Low)
- **Description:** On simple, single-document factual lookups (e.g., "What is the melting point of copper?"), the overhead of Knowledge Graph traversal and goal decomposition may result in higher latency without answering accuracy benefits.
- **Mitigation:**
  - Accepted by design. AXION's hypothesis is specifically that knowledge composition and transfer outperform RAG on *multi-hop, cross-disciplinary, unfamiliar problems*. Simple factual queries are handled directly by the Baseline RAG sub-module (Component 3).
- **Status:** Accepted architectural reality.

---

### 3.3 Data Quality & Provenance Risks

#### [DR-01] Ingesting Untrusted, Outdated, or Conflicting Data Sources
- **Risk Score:** 6 (Probability: Medium, Impact: High)
- **Description:** Ingesting blogs, preprint drafts, or conflicting papers could pollute the Knowledge Graph with erroneous or contradictory assertions.
- **Mitigation:**
  - Every source document is assigned a **Trust Tier** (`PEER_REVIEWED`, `TECHNICAL_DOC`, `PUBLIC_WEB`, `UNVERIFIED`).
  - Contradiction Detection Engine in Component 5 actively flags when two sources assert contradictory relations on identical nodes.
  - Citations must preserve source URI, publication year, and exact page bounding boxes.
- **Status:** Active.

#### [DR-02] Complex PDF Layout Loss (Tables, Vector Diagrams, Multi-Column)
- **Risk Score:** 6 (Probability: High, Impact: Medium)
- **Description:** Academic papers often use two-column layouts, embedded LaTeX equations, and dense parameter tables that standard text extractors mangle.
- **Mitigation:**
  - Utilize `PyMuPDF` with layout-aware block sorting (detecting column boundaries and reading order).
  - Explicitly classify equation blocks and table blocks as structured JSON rather than raw flattened strings.
- **Status:** Active (Specified in `SYSTEM_ARCHITECTURE.md`).

---

### 3.4 Security & Sandbox Isolation Risks

#### [SR-01] Arbitrary Code Execution / Host Escape in Simulation Sandbox
- **Risk Score:** 4 (Probability: Low, Impact: Critical)
- **Description:** Component 8 executes dynamically generated Python scripts to test hypotheses. If an untrusted script executes malicious system calls or opens network sockets, the host system could be compromised.
- **Mitigation:**
  - **Zero Host Execution Policy:** No generated code ever runs on the host OS.
  - Scripts execute exclusively in disposable Docker containers with:
    - Disabled networking: `--network none`
    - Read-only root filesystem
    - Dropped capabilities (`--cap-drop=ALL`)
    - Execution as unprivileged user `nobody`
    - In-memory ephemeral scratchpad (`--tmpfs /tmp:rw,size=128m`)
    - Hard process watchdog: 15-second wall-clock timeout with `SIGKILL`.
- **Status:** Mitigating (Detailed in ADR-002 and `SYSTEM_ARCHITECTURE.md`).

#### [SR-02] Indirect Prompt Injection via Ingested Documents
- **Risk Score:** 9 (Probability: High, Impact: High)
- **Description:** A malicious PDF or web page could contain adversarial text instructing the LLM to ignore system instructions or assert false scientific facts.
- **Mitigation:**
  - Strict separation of untrusted content channels: retrieved document text is fed into LLM prompts inside clearly delimited XML tags (`<source_evidence>`) with explicit instruction isolation.
  - The extraction pipeline uses constrained JSON decoding (Pydantic schemas) which rejects non-schema text.
  - The Sandbox Execution Worker only runs Python code vetted for syntax and execution safety, never raw shell strings.
- **Status:** Active.

---

### 3.5 Resource, Cost & Operational Risks

#### [CR-01] Excessive LLM Token Consumption During Knowledge Graph Extraction
- **Risk Score:** 6 (Probability: High, Impact: Medium)
- **Description:** Running dense entity and relation extraction over hundreds of document pages using expensive frontier models can rapidly exhaust API budgets.
- **Mitigation:**
  - Implement a two-tiered extraction pipeline: use faster, low-cost models (e.g., Gemini 1.5/2.0 Flash or local Mistral) for initial entity/relation extraction and filtering.
  - Reserve high-capacity frontier models (e.g., GPT-4o, Claude 3.5 Sonnet) exclusively for complex cross-domain transfer mapping and goal decomposition.
  - Aggressive caching: document chunks and extraction graphs are cached by SHA-256 hash in PostgreSQL to prevent duplicate processing.
- **Status:** Active.

---

## 4. Risk Review & Audit Schedule

- **Cadence:** The Risk Register is reviewed and updated at the completion of every development phase.
- **Phase 1 Audit Gate:** TR-01 (Entity Normalization) and DR-02 (PDF Layout Extraction) must be verified through automated unit tests before Phase 1 is closed.
- **Phase 3 Audit Gate:** RR-01 (Applicability Guard) must demonstrate $\ge 90\%$ rejection of unsound transfers before Phase 3 is closed.
- **Phase 4 Audit Gate:** SR-01 (Docker Sandbox Isolation) must pass automated penetration and egress-blocking tests before Phase 4 is closed.

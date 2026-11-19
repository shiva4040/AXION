# AXION — Five-Phase Development Roadmap, Security & Pilot Plan

**Document Version:** 1.0.0  
**Phase Target:** Master Phase Architecture & Implementation Lifecycle  
**Date:** November 19, 2026  

---

## 1. Five Development Phases: Entry, Deliverables, Acceptance & Stop Rules

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ PHASE 1: FOUNDATION AND WORKING PIPELINE                                               │
│ Minimal end-to-end working pipeline (Stages 01-08 minimal), Plain RAG baseline, logging│
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                            │
                                            ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ PHASE 2: EVIDENCE INTELLIGENCE AND KNOWLEDGE COMPOSITION                               │
│ Structured claim extraction, typed relations, conditions, multi-document graphs       │
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                            │
                                            ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ PHASE 3: REASONING ENGINE AND EARLY PRODUCT                                            │
│ Symbolic SymPy solver, Pint units, Python sandbox, minimal UI, 5-10 pilot users       │
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                            │
                                            ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ PHASE 4: INDEPENDENT VERIFICATION AND MEMORY                                           │
│ Verbatim quote audit, contradiction checks, Stage 07 memory read/write, Applicability  │
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                            │
                                            ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ PHASE 5: COMPLETE AXION AND TRANSFER EVALUATION                                        │
│ Full answer generation, locked benchmark evaluation, memory transfer experiment report│
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### Detailed Phase Specifications

#### PHASE 1 — Foundation and Working Pipeline
- **Target Timebox:** 2 weeks.
- **Entry Criteria:** Phase 0 approved by human owner; benchmark schema and dev dataset verified.
- **Core Deliverables:**
  1. Minimal implementations of Stages 01 through 08 wired into an executable pipeline.
  2. Minimal Stage 08 Answer Generator outputting direct answers, verbatim quotations, and abstention notices.
  3. Integrated Plain RAG Baseline operating under identical model/retrieval parameters.
  4. Automated logging of queries, chunk retrievals, citations, and execution latency.
- **Tests & Acceptance Criteria:**
  - Pipeline executes end-to-end on Category 1 (Retrieval) and Category 5 (Abstention) development questions.
  - Baseline comparison runner produces paired evaluation CSV logs without manual intervention.
  - Zero crashes on malformed queries.
- **Stop Rule:** If Stage 01/02 failure causes pipeline execution failure $> 15\%$, pause and refactor ingestion/retrieval interfaces before proceeding.

#### PHASE 2 — Evidence Intelligence and Knowledge Composition
- **Target Timebox:** 3 weeks.
- **Entry Criteria:** Phase 1 pipeline passing all baseline regression tests.
- **Core Deliverables:**
  1. Structured claim extraction preserving governing assumptions and boundary conditions.
  2. Fixed relation ontology (e.g. `PROPORTIONAL_TO`, `GOVERNED_BY`, `INVERSE_TO`, `BOUNDED_BY`).
  3. Multi-document knowledge composition engine linking premises across document boundaries.
  4. Variable harmonization resolving multi-author nomenclature to SI base dimensions.
- **Tests & Acceptance Criteria:**
  - Evaluated on Category 2 (Claim Extraction) and Category 3 (Composition) development questions.
  - Claim Extraction Precision $\ge 0.80$, Condition Extraction Recall $\ge 0.75$.
  - Multi-hop composition accuracy significantly exceeds baseline ($p < 0.05$).
- **Stop Rule:** If variable harmonization produces dimensional contradictions in $> 10\%$ of composed systems, halt and strengthen dimensional tagging.

#### PHASE 3 — Reasoning Engine and Early Product
- **Target Timebox:** 3 weeks.
- **Entry Criteria:** Phase 2 composition engine operational.
- **Core Deliverables:**
  1. Sandboxed Python calculation engine with SymPy for symbolic algebra and Pint for physical units.
  2. Causal inference DAG tracking every step from premise to derivation.
  3. Minimal web interface allowing users to upload documents and submit research questions.
  4. Recruitment of 5–10 academic/engineering pilot users.
- **Tests & Acceptance Criteria:**
  - Calculation Accuracy on Category 3 quantitative problems $\ge 0.90$.
  - Zero dimensionally inconsistent calculations pass Pint validation.
  - Pilot users successfully complete sample research investigations.
- **Stop Rule:** If sandbox security audit reveals any potential for shell escape or unauthorized OS access, immediately halt and lock down execution isolation.

#### PHASE 4 — Independent Verification and Memory
- **Target Timebox:** 3 weeks.
- **Entry Criteria:** Phase 3 reasoning engine and minimal UI functional.
- **Core Deliverables:**
  1. Stage 06 Independent Verifier: verbatim quotation checker, contradiction detector, and applicability guardrail.
  2. Stage 07 Verified Findings Memory: SQLite/PostgreSQL persistent store supporting reading and writing.
  3. Automated dependency tracking: revoking a premise automatically invalidates downstream findings.
  4. False-transfer protection algorithm.
- **Tests & Acceptance Criteria:**
  - Evaluated on Category 4 (Conflicting Sources) and Category 6 (Transfer/Memory).
  - False-Transfer Rate strictly equals $0.00\%$ on negative transfer test cases.
  - Contradiction Detection F1 $\ge 0.85$.
- **Stop Rule:** If memory reading introduces unverified claims into reasoning without passing through Stage 06 validation, stop and seal the memory retrieval path.

#### PHASE 5 — Complete AXION and Transfer Evaluation
- **Target Timebox:** 4 weeks.
- **Entry Criteria:** Phases 1–4 complete; all 180 development questions benchmarked.
- **Core Deliverables:**
  1. Complete Stage 08 Answer Generation System with interactive visualizations, mathematical breakdowns, and uncertainty bounds.
  2. Locked Benchmark Execution: Human owner runs the 180 locked test questions on an external air-gapped machine.
  3. Memory Transfer Experiment: Full comparison of AXION with vs. without memory.
  4. Comprehensive scientific research report documenting statistical findings, effect sizes, and limitations.
- **Tests & Acceptance Criteria:**
  - Complete locked benchmark executed across all 6 categories.
  - Paired analysis demonstrates statistically significant improvement over Plain RAG ($p < 0.01$).
  - Zero security violations across the entire evaluation run.
- **Stop Rule:** If locked test evaluation reveals $< 5\%$ differential improvement or non-significant paired differences ($p \ge 0.05$), state the exact negative finding without altering historical benchmarks or modifying test data.

---

## 2. Security Architecture, Untrusted Data Boundary & Document Rights

### 2.1 Untrusted Data Boundary & Prompt Injection Defense
- **Fundamental Principle:** All external text, user-uploaded PDFs, extracted document passages, acquired web content, and retrieved snippets must be treated strictly as **untrusted data**, never as executable instructions or trusted system directives.
- **Clarification on AST Parsing:** Python Abstract Syntax Tree (AST) parsing applies **exclusively to the static analysis of generated Python code scripts** in Stage 05 (Reasoning and Calculations) and Component 8 (Hypothesis Tester). AST parsing **cannot be used to parse or secure natural-language prose chunks**, as arbitrary human language does not conform to Python syntax trees.
- **Data Boundary & Injection Defense In Depth:**
  - *Instruction/Content Disjunction:* System instructions, cognitive stage goals, and operational guardrails are defined strictly at the system prompt level. External document text is quarantined within structured, typed payload fields.
  - *Structured Data Framing:* Document content is passed to LLMs inside explicit, typed JSON schemas or bounded data blocks.
  - *Defense In Depth Limitation Notice:* Boundary delimiters, XML tags, and heuristic keyword filters (e.g. flagging phrases like *"ignore previous instructions"*, *"override system"*, *"system prompt"*) provide defense-in-depth and logging signals, but **do not alone establish a mathematically complete security guarantee against prompt injection**. Extracted text must never be granted direct tool-execution permissions or administrative system capabilities.
  - *Safe Tool Triggering:* Tool invocations and mathematical solver scripts are generated exclusively by structured internal reasoning stages, never directly triggered by text found inside an external document chunk.

### 2.2 Calculation Execution Sandbox & OS-Level Process Isolation
- **Inadequacy of Restricted Built-ins:** Restricting Python `__builtins__` inside the same interpreter process (e.g., removing `open`, `__import__`, `eval`) **does not provide a secure sandbox**. In CPython, untrusted scripts can readily traverse the object inheritance tree (e.g. `().__class__.__base__.__subclasses__()`) to recover references to `os` or `sys` and execute arbitrary shell commands.
- **Mandatory OS-Level Sandbox Specification:** Untrusted code execution (such as SymPy mathematical evaluation, numerical calculation, and dynamic ODE simulation) must occur inside an **isolated operating-system process boundary** with hard resource limits:
  1. *Subprocess & Process Token Isolation:* The calculation worker must run as a separate, unprivileged subprocess.
     - **Windows Environments:** Run under a restricted Windows Token with `SeRestricted` privileges, encapsulated within a **Windows Job Object** that enforces hard limits on active process counts, virtual memory caps, and CPU time slices.
     - **Linux Environments:** Run inside an isolated namespace/container sandbox using **bubblewrap (`bwrap`)** or **seccomp-bpf** system call filtering, disallowing `execve`, `fork`, and socket creation syscalls.
  2. *Filesystem Restrictions:* The calculation process must operate with a read-only root filesystem. Temporary scratch file creation is restricted to an isolated, ephemeral RAM disk (`tmpfs`) or dedicated per-task directory that is securely wiped immediately upon process termination.
  3. *Network Isolation:* Complete prohibition of outbound network socket creation (`AF_INET`, `AF_INET6`). Untrusted calculation scripts cannot communicate over HTTP, DNS, or raw sockets.
  4. *Hard Resource Limits & Timeouts:*
     - Maximum CPU wall-clock timeout: $2000\text{ ms}$ (hard termination via OS kill signal, not catchable Python exceptions).
     - Maximum RAM allocation: $256\text{ MB}$ (exceeding memory triggers immediate OS process termination).
     - Controlled Standard I/O: Inter-process communication occurs strictly over unidirectional pipes exchanging serialized JSON inputs and outputs.
- **Empirical Security Rule:** AXION **shall not claim that its execution sandbox is secure** until the sandbox architecture has been fully implemented, integrated, and subjected to automated adversarial penetration and escape test suites.

### 2.3 Data Management, User Isolation & Retention
- **Storage Location:** Raw documents are stored in `storage/documents/<user_id>/` with restricted filesystem permissions.
- **Access Control & User Isolation:** Multi-tenant database schema enforces foreign-key partitioning on `user_id`. Queries, vector lookups, Knowledge Graph traversals, and memory reads are strictly scoped to the authenticated session.
- **Data Retention & Deletion:**
  - Users possess an explicit right to delete any uploaded document.
  - Deletion triggers an atomic cascade: raw file is purged from disk, vector embeddings in `document_chunks` are erased, and unverified graph nodes are pruned.
- **Encryption:** AES-256 encryption at rest for document storage; TLS 1.3 in transit.
- **Copyright & Fair Use:** Documents are processed strictly for local research text-and-data mining. Source attribution, original publisher DOIs, and license strings are permanently bound to every extracted chunk.

---

## 3. Pilot User Engagement Plan

### 3.1 Cohort Identification (Phase 1)
- Recruit **5 to 10 scientific researchers** across academic institutions and R&D labs:
  - 2 Materials Scientists / Solid-State Physicists
  - 2 Electrical / Power Electronics Engineers
  - 2 Mechanical / Fluid Dynamics Engineers
  - 2 Biomedical / Pharmacology Researchers

### 3.2 Structured Feedback Collection (Phase 3)
During Phase 3, pilot users are given access to the minimal web interface with their own domain research documents. Users evaluate the platform on a standardized 5-point instrument:
1. **Document Ingestion Ease:** Clarity and speed of PDF upload and parsing.
2. **Evidence Relevance:** Precision of retrieved chunks compared to their manual literature searches.
3. **Citation Trust:** Whether the cited page and paragraph accurately support the generated explanation.
4. **Answer Usefulness:** Practical utility of the derived equations and numerical solutions.
5. **Explanation Clarity:** Readability of the step-by-step reasoning steps.
6. **Perceived Latency:** Usability of turnaround time.

> **Epistemic Note:** Feedback from 5–10 pilot users will be reported as qualitative usability insights, **never as proof of product-market fit or commercial validation**.

# AXION — Phase 1 Known Limitations and Technical Debt
## Formal Limitations Catalogue for Phase 1 Foundation

**Project:** AXION  
**Document Version:** 1.0.0  
**Phase:** Phase 1 — Foundation & Working Pipeline  
**Date:** November 19, 2026  
**Status:** Authoritative Limitations Record  

---

## 1. Epistemic & Scientific Scope Limitations

1. **No Claim of General Scientific Discovery:**
   - Phase 1 implements a foundational eight-stage evidence and reasoning pipeline. It does **not** claim to have solved automated scientific discovery, proven general multi-disciplinary superiority, or demonstrated autonomous theory generation.
2. **Simplified Symbolic & Dimensional Solver:**
   - Stage 05 implements algebraic substitution and basic SI dimensional algebra using SymPy. It does not currently integrate high-order non-linear differential solvers, partial differential equation (PDE) integration, or tensor mechanics.
3. **Restricted Domain Ontologies:**
   - Harmonization in Stage 04 currently operates on standardized physical symbols and explicit aliases (`S` vs. `Seebeck_coeff`, `mu` vs. `dynamic_viscosity`). Broad semantic ontology mapping across uncurated vocabularies is deferred to Phase 2.

---

## 2. Benchmark & Dataset Limitations

1. **Pilot Benchmark Sample Size ($N = 180$):**
   - The Phase 1 development benchmark evaluates 180 queries across 6 categories (30 queries per category). While adequate for diagnostic and regression verification, a sample size of 30 items carries a 95% binomial confidence interval of approximately $\pm 8\%$.
   - Observed differences must be interpreted as directional and diagnostic, not statistically definitive large-scale proofs.
2. **Synthetic Scientific Worlds:**
   - Synthetic documents were engineered with planted formulas, constants, and distractors to eliminate parametric memorization by pretrained models. Performance on authentic, noisy, unstandardized scientific PDF scans with complex multi-page tables is addressed in future real-world evaluation phases.
3. **Locked Test Set Separation:**
   - The development agent has had access strictly to the 180 development queries and 30 development documents. The 180 locked evaluation problems remain isolated for owner-administered verification.

---

## 3. External API, Network & Credential Dependencies

1. **Scholarly Connectors in Offline / Mock Mode:**
   - Connectors for arXiv, Crossref, Semantic Scholar, and OpenAlex are fully implemented with rate-limiting, backoff, and schema parsing, but run with mock/sandbox providers during local test-suite execution to avoid external network flakes and API quota consumption.
   - Production deployment requires valid Semantic Scholar and Crossref API credentials configured in `.env`.
2. **LLM Provider Dependency:**
   - Evaluation tests utilize deterministic `MockProvider` instances with fixed random seeds to ensure reproducible continuous integration. Real LLM execution requires Gemini, OpenAI, or local Ollama endpoints.

---

## 4. Architectural & Performance Boundaries

1. **Top-K Chunk Window:**
   - The default retrieval window is configured to $k = 5$ chunks per query. While document diversification ensures multi-hop document coverage for 2 to 3 required premises, queries requiring 6 or more simultaneous documents would require larger retrieval windows or iterative multi-turn expansion.
2. **In-Memory Validated Knowledge Memory:**
   - Stage 07 operates on an in-memory `ValidatedKnowledgeMemory` instance during benchmark execution. Persistent storage via PostgreSQL / SQLite backing is fully supported by the schema but should be backed by distributed cache in multi-worker environments.
3. **Single-Pass Reasoning (No Iterative Backtracking):**
   - Stage 05 executes a single forward pass through the dependency DAG. If a variable cannot be resolved in one pass, Stage 06 triggers abstention rather than actively issuing follow-up retrieval queries to locate missing intermediate premises. Multi-turn reasoning loops are targeted for Phase 2.

---

## 5. Technical Debt & Planned Improvements

| Component | Current Implementation | Phase 2 Improvement Target |
| :--- | :--- | :--- |
| **Stage 01** | Rule-based intent & keyword domain mapping | Fine-tuned embedding/LLM intent parser |
| **Stage 03** | Regex clause & sentence segmentation | Learned scientific claim extraction model |
| **Stage 04** | Greedy variable harmonization | Formal SMT / Z3 constraint satisfaction |
| **Stage 05** | SymPy algebraic substitution | Mixed symbolic-numeric ODE / PDE reasoning |
| **Stage 06** | 4-pass verification guard | Formal verification ledger with SMT proofs |
| **Stage 07** | In-memory validated memory | Persistent distributed graph knowledge base |
| **Stage 08** | Template-driven response formatting | Dynamically generated natural prose with inline tooltips |

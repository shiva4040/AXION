# AXION — Source Integration Test Plan

**Document Version:** 1.0.0  
**Status:** Verification & Testing Specification  
**Coverage Target:** 100% of Implemented Source Connectors  
**Date:** November 18, 2026  

---

## 1. Testing Philosophy & Verification Strategy

To guarantee that AXION remains a stable, production-grade scientific platform as new sources are connected, all source integrations must adhere to a **three-tiered testing pyramid**:

```
                         ▲
                        / \
                       /   \  Tier 3: End-to-End Pipeline Verification
                      /=====\ (Acquisition -> DB -> Graph -> Solver)
                     /       \
                    /         \  Tier 2: Live Integration & Rate-Limit Smoke Tests
                   /===========\ (Real network calls to live public APIs)
                  /             \
                 /               \  Tier 1: Isolated Unit Tests with Mock Payloads
                /=================\ (Schema, normalization, error handling, retries)
```

1. **Tier 1 (Unit & Mock Tests):** Run in continuous integration without external network dependencies. Tests HTTP parsing, schema validation, XML/JSON parsing, deduplication, and error recovery using mocked responses.
2. **Tier 2 (Live Smoke Tests):** Verified against active public APIs (e.g. arXiv, Crossref, PubMed, OpenAlex) to confirm endpoint uptime, live schema stability, and proper HTTP 429 backoff handling.
3. **Tier 3 (End-to-End Ingestion Tests):** Verifies that acquired source documents successfully chunk into the vector database and generate nodes in the Scientific Knowledge Graph.

---

## 2. Test Suites & Verification Criteria

### Suite 1: Schema Compliance & Normalization (`test_source_document_schema.py`)
- **Objective:** Ensure every connector returns valid, normalized `SourceDocument` instances.
- **Assertions:**
  - `id` is a non-empty string starting with the canonical connector prefix.
  - `title` is stripped of raw XML/HTML tags and excessive whitespace.
  - `authors` is a list of strings (never raw nested dicts or unparsed XML).
  - `access_status` and `trust_tier` match the allowed enum definitions.
  - `relevance_score` is strictly bounded within $[0.0, 1.0]$.
  - `epistemic_tier` defaults to `EpistemicTier.FACT_DOCUMENTED`.

### Suite 2: Network Resilience & Fault Tolerance (`test_connector_resilience.py`)
- **Objective:** Confirm connectors fail gracefully under adverse network conditions without raising unhandled exceptions or blocking the event loop.
- **Scenarios Tested:**
  - **Connection Timeout:** Client raises `httpx.TimeoutException` $\implies$ connector logs warning and returns empty list `[]`.
  - **HTTP 429 (Rate Limit Exceeded):** Server responds with 429 Too Many Requests $\implies$ connector captures warning, reports in health check, and does not crash the search pipeline.
  - **HTTP 500 / 503 (Upstream Outage):** Upstream server error $\implies$ connector reports `is_available = False` in `check_health()`.
  - **Corrupt / Malformed XML/JSON:** Unparsable response body $\implies$ connector catches parse error and skips malformed records cleanly.

### Suite 3: Deduplication & Fingerprinting (`test_acquisition_deduplication.py`)
- **Objective:** Verify that multiple citations of the same paper or book across different sources collapse into a single master document.
- **Scenarios Tested:**
  - Identical DOI reported by Crossref and OpenAlex.
  - Pre-existing DOI already stored in AXION's SQLite database.
  - Non-DOI titles matching via title/author SHA-256 fingerprinting.

### Suite 4: End-to-End Cognitive Pipeline Integration (`test_acquisition_e2e_flow.py`)
- **Objective:** Confirm seamless flow from source query to reasoning solver.
- **Steps Verified:**
  1. User or solver issues research query.
  2. Acquisition engine fans out across active connectors.
  3. Results are deduplicated and ranked.
  4. Selected documents are committed to the relational database.
  5. Text is chunked and vector embeddings are generated.
  6. Graph extractor parses entities and inserts relations into the Knowledge Graph.
  7. Baseline controller and Cross-Domain solver query the newly ingested knowledge.

---

## 3. Regression Safeguards

- Every new connector implementation must execute against the existing test suite:
  ```powershell
  .venv\Scripts\python.exe -m pytest -q
  ```
- All **85 existing tests** spanning the core components (PDF Reader, Knowledge Graph, Baseline, Reasoning, Transfer Engine, Applicability Guard, Hypothesis Tester, and Validated Memory) must maintain $100\%$ green passing status before any branch merge.

---

## 4. Test Execution Matrix by Phase

| Phase | Target Connectors | Unit Test File | Live Smoke Test Method |
| :--- | :--- | :--- | :--- |
| **Phase A (Done)** | `arxiv`, `crossref`, `pubmed`, `openalex`, `huggingface`, `kaggle`, `web_search`, `local_upload` | `tests/test_acquisition_engine.py` | Verified in `evaluate_solar_ev.py` |
| **Phase B (Proposed)**| `wikipedia`, `semantic_scholar`, `doaj`, `project_gutenberg`, `open_library`, `eric`, `inspire_hep`, `nasa_ads` | `tests/test_connectors_phase_b.py` | `tests/live/test_smoke_phase_b.py` |
| **Phase C (Future)** | `mit_ocw`, `internet_archive`, `loc_wdl`, `core`, `base`, `nptel_swayam` | `tests/test_connectors_phase_c.py` | `tests/live/test_smoke_phase_c.py` |
| **Phase D (Future)** | `scopus`, `web_of_science`, `inspec`, `proquest`, `britannica` | `tests/test_connectors_licensed.py`| Token-gated mock verification |

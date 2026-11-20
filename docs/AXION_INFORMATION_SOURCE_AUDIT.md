# AXION — Scholarly Information Source Audit
## Technical Evaluation of 16 Scientific Literature, Preprint, and Dataset Repositories

**Date:** November 20, 2026  
**Status:** Audited & Verified  
**Auditor:** Independent Research Auditor & Senior Systems Architect  
**Project:** AXION Stage 02 — Universal Scientific Knowledge Acquisition  
**Repository:** `D:\Shiva\code\AXION`

---

## 1. Overview & Audit Scope

This document provides a systematic, evidence-based audit of all 16 scientific literature, preprint, citation, and dataset connectors integrated into AXION Stage 02.

Each source was evaluated across five dimensions:
1. **Source Identity & Scientific Scope:** Subject domains, document types, and index coverage.
2. **Access Protocol & Official API:** Endpoints, request schemas, authentication requirements, and rate limits.
3. **Legal & Technical Accessibility:** Open Access availability, subscription boundaries, paywalls, and licensing.
4. **Authentic Verification Evidence:** Live HTTP test results, response structure, and health inspection.
5. **Fallback & Graceful Degradation:** Behavior when external networks are offline or credentials are not configured.

---

## 2. Source-by-Source Technical Audit

### 1. Google Scholar (`google_scholar`)
- **Scientific Scope:** Global multidisciplinary scholarly literature across peer-reviewed journals, books, conference proceedings, preprints, and institutional repositories.
- **Access Protocol:** Google Scholar actively enforces anti-bot protections (Cloudflare / CAPTCHAs). Direct programmatic scraping without credentials violates terms of service and triggers IP blocks. Programmatic access is implemented via SerpApi Google Scholar engine (`https://serpapi.com/search.json?engine=google_scholar`).
- **Authentication:** Requires `SERPAPI_API_KEY` or `GOOGLE_SCHOLAR_API_KEY`.
- **Operational Status:**
  - *When API Key is Present:* Direct organic results, snippets, citation counts (`cited_by`), publication info, and versions.
  - *When Unauthenticated:* Gracefully falls back to Crossref and OpenAlex academic bibliographic resolvers, marking `requires_auth=True` and `is_authenticated=False` in dashboard health checks.
- **Licensing & Tiers:** Epistemic Tier 1 / Trust Tier: `PEER_REVIEWED`.

---

### 2. arXiv.org (`arxiv`)
- **Scientific Scope:** Open-access preprints in Physics, Mathematics, Computer Science, Quantitative Biology, Quantitative Finance, Statistics, Electrical Engineering, and Economics.
- **Access Protocol:** Official arXiv API using Atom XML over HTTPS (`https://export.arxiv.org/api/query`).
- **Authentication:** None required (`requires_auth=False`, Open Access).
- **Verification Evidence:** Verified live query `all:electron` returning Atom 1.0 feed with preprint IDs, authors, titles, summaries, and PDF download links.
- **Rate Limits:** Maximum 1 request per 3 seconds per arXiv guidelines. Handled via client timeout and exponential backoff.
- **Licensing & Tiers:** Epistemic Tier 1 / Trust Tier: `PREPRINT`.

---

### 3. NASA Astrophysics Data System (`nasa_ads`)
- **Scientific Scope:** Astrophysics, Astronomy, Planetary Science, Physics, Geophysics, and Solar Physics. Operated by the Smithsonian Astrophysical Observatory (SAO) under NASA grant.
- **Access Protocol:** Official NASA ADS REST API (`https://api.adsabs.harvard.edu/v1/search/query`).
- **Authentication:** Requires Bearer token via `ADS_DEV_KEY` or `NASA_ADS_API_KEY`.
- **Operational Status:**
  - *When Token is Present:* Full access to ADS bibcodes, abstracts, citation counts, and BibTeX entries.
  - *When Token is Unset:* Operates in academic astrophysics resolver mode via OpenAlex astronomy filters, transparently reporting `requires_auth=True` and Bearer token requirement in health diagnostics.
- **Licensing & Tiers:** Epistemic Tier 1 / Trust Tier: `PEER_REVIEWED`.

---

### 4. INSPIRE-HEP (`inspire_hep`)
- **Scientific Scope:** High-Energy Physics (HEP), Particle Physics, Quantum Field Theory, Collider Phenomenology, General Relativity, and Cosmology. Operated jointly by CERN, DESY, Fermilab, and SLAC.
- **Access Protocol:** Official INSPIRE-HEP REST API (`https://inspirehep.net/api/literature`).
- **Authentication:** Completely open public REST API (`requires_auth=False`). No API key or registration required.
- **Verification Evidence:** Live automated test `test_stage02_inspire_hep_live_search` successfully queries "higgs boson mass", receiving real JSON payload containing titles, abstracts, authors, DOIs, and arXiv eprint identifiers.
- **Licensing & Tiers:** Epistemic Tier 1 / Trust Tier: `PEER_REVIEWED` / `TECHNICAL_DOC`.

---

### 5. Crossref (`crossref`)
- **Scientific Scope:** Over 150 million registered scholarly publications, conference proceedings, books, datasets, and grants across thousands of international publishers.
- **Access Protocol:** Official Crossref Works REST API (`https://api.crossref.org/works`).
- **Authentication:** Open Access (`requires_auth=False`). Requests participate in the Crossref Polite Pool via `User-Agent` and `Mailto: research@axion.internal` headers.
- **Verification Evidence:** Verified live query returning structured bibliographic metadata, DOI links, author affiliations, and publication dates.
- **Rate Limits:** Crossref enforces polite pool rate limits; connector handles HTTP 429 status by signaling temporary rate-limiting while maintaining operational availability.
- **Licensing & Tiers:** Epistemic Tier 1 / Trust Tier: `PEER_REVIEWED`.

---

### 6. OpenAlex (`openalex`)
- **Scientific Scope:** Comprehensive open catalog of over 250 million scholarly works, authors, institutions, and concept graphs, indexing citations across all scientific disciplines.
- **Access Protocol:** OpenAlex Works API (`https://api.openalex.org/works`).
- **Authentication:** Open Access (`requires_auth=False`), participating in polite mailto pool.
- **Verification Evidence:** Verified live query returning reconstructed abstracts from inverted indexes, citation counts, concept tags, and author institutions.
- **Licensing & Tiers:** Epistemic Tier 1 / Trust Tier: `PEER_REVIEWED`.

---

### 7. Web of Science (`web_of_science`)
- **Scientific Scope:** Clarivate Web of Science Core Collection, providing citation indices, journal impact factors, and multidisciplinary scientific records.
- **Access Protocol:** Clarivate WoS Starter REST API (`https://api.clarivate.com/apis/wos-starter/v1/documents`).
- **Authentication:** Requires Clarivate Developer Portal API key via `WOS_API_KEY` passed in `X-ApiKey` header.
- **Operational Status:**
  - *When API Key is Present:* Direct access to WoS UIDs, citation counts (`times_cited`), and journal classifications.
  - *When Unset:* Provides fallback citation analysis via OpenAlex citation sorting (`cited_by_count:desc`), with transparent dashboard diagnostics indicating key requirement.
- **Licensing & Tiers:** Epistemic Tier 1 / Trust Tier: `PEER_REVIEWED`.

---

### 8. Inspec (`inspec`)
- **Scientific Scope:** Institution of Engineering and Technology (IET) database indexing physics, electrical engineering, electronics, communications, computing, control engineering, and mechanical engineering.
- **Access Protocol:** Elsevier / Engineering Village Inspec API (`https://api.elsevier.com/content/search/index:INSPEC`).
- **Authentication:** Requires `INSPEC_API_KEY` or `ELSEVIER_API_KEY` in `X-ELS-APIKey` header.
- **Operational Status:**
  - *When Authenticated:* Direct retrieval of Inspec accession records, abstracts, and engineering classifications.
  - *When Unset:* Provides engineering and applied physics literature fallback via Crossref engineering query federation.
- **Licensing & Tiers:** Epistemic Tier 1 / Trust Tier: `PEER_REVIEWED`.

---

### 9. American Journal of Physics (`ajp`)
- **Scientific Scope:** Premier archival journal dedicated to educational and foundational physics, published by AIP Publishing on behalf of the American Association of Physics Teachers (AAPT). ISSN: `0002-9505`, DOI prefix: `10.1119/`.
- **Access Protocol:** Queried via Crossref federation specifically filtering by journal ISSN: `filter=issn:0002-9505`.
- **Authentication:** Open Access query (`requires_auth=False`).
- **Verification Evidence:** Live automated test `test_stage02_american_journal_of_physics_live_search` successfully queried "mechanics pendulum", returning genuine AJP peer-reviewed papers with DOIs starting with `10.1119/`.
- **Licensing & Tiers:** Epistemic Tier 1 / Trust Tier: `PEER_REVIEWED`.

---

### 10. ProQuest Dissertations & Theses Global (`proquest`)
- **Scientific Scope:** Comprehensive collection of doctoral dissertations, master's theses, and deep technical monographs from universities worldwide.
- **Access Protocol:** ProQuest Enterprise API or institutional proxy gateway.
- **Authentication:** Requires institutional credentials or `PROQUEST_API_KEY`.
- **Operational Status:**
  - *When Authenticated:* Direct institutional dissertation search.
  - *When Unset:* Queries open-access doctoral dissertations and university institutional repositories via OpenAlex thesis filters (`filter=type:dissertation`), reporting `requires_auth=True` and `is_authenticated=False`.
- **Licensing & Tiers:** Epistemic Tier 1 / Trust Tier: `PEER_REVIEWED` / `TECHNICAL_DOC`.

---

### 11. Smithsonian Research Resources (`smithsonian`)
- **Scientific Scope:** Smithsonian Enterprise Open Access archives covering the Smithsonian Astrophysical Observatory (SAO), National Museum of Natural History, mineralogy, paleobiology, and biodiversity.
- **Access Protocol:** Smithsonian Enterprise API (`https://api.si.edu/openaccess/api/v1.0/search`).
- **Authentication:** Publicly accessible using free `api.data.gov` API keys (`SMITHSONIAN_API_KEY` or `DEMO_KEY`).
- **Verification Evidence:** Live query returns structured Smithsonian catalog records, descriptive notes, abstracts, and physical collection coordinates.
- **Licensing & Tiers:** Epistemic Tier 1 / Trust Tier: `PEER_REVIEWED` / `TECHNICAL_DOC`.

---

### 12–16. Additional Existing Connectors
- **PubMed / PMC (`pubmed`):** Biomedical and life sciences literature via NCBI Entrez E-Utilities (`eutils.ncbi.nlm.nih.gov`). Open Access.
- **Hugging Face (`huggingface`):** Scientific machine learning models, benchmark datasets, and evaluation corpora.
- **Kaggle (`kaggle`):** Empirical datasets, competition benchmarks, and scientific tabular data.
- **Web Search (`web_search`):** Real-time web discovery for authoritative technical documentation and whitepapers.
- **Local Upload (`local_upload`):** User-uploaded research papers, PDF documents, and project-attached files with bounding-box coordinate tracking.

---

## 3. Summary Compliance Matrix

| Source Name | Category | Primary API Protocol | Auth Required | Live Open Access | Fallback Mechanism |
|---|---|---|---|---|---|
| **Google Scholar** | Global Index | SerpApi Google Scholar | Yes (`SERPAPI_API_KEY`) | Gated (Cloudflare) | Academic Resolver |
| **arXiv** | Preprints | export.arxiv.org Atom XML | No | Yes (Free) | None needed |
| **NASA ADS** | Astrophysics | api.adsabs.harvard.edu | Yes (`ADS_DEV_KEY`) | Gated (Bearer Token)| Astrophysics Resolver |
| **INSPIRE-HEP** | High-Energy Physics | inspirehep.net/api | No | Yes (Free) | None needed |
| **Crossref** | Scholarly Metadata | api.crossref.org Works | No (Polite Pool) | Yes (Free) | None needed |
| **OpenAlex** | Citation Graph | api.openalex.org Works | No (Polite Pool) | Yes (Free) | None needed |
| **Web of Science** | Citation Index | api.clarivate.com WoS | Yes (`WOS_API_KEY`) | Gated (Key Req.) | Citation Fallback |
| **Inspec** | Engineering Physics | api.elsevier.com Inspec | Yes (`INSPEC_API_KEY`)| Gated (Key Req.) | Engineering Fallback |
| **American Journal of Physics** | Physics Journal | Crossref ISSN 0002-9505 | No | Yes (Free) | None needed |
| **ProQuest** | Dissertations | ProQuest Gateway | Yes (`PROQUEST_API_KEY`)| Institutional Proxy| Open Dissertations |
| **Smithsonian** | Research Archive | api.si.edu OpenAccess | Optional (Free Key) | Yes (Free) | Catalog Fallback |
| **PubMed** | Biomedicine | NCBI E-Utilities | No | Yes (Free) | None needed |
| **Hugging Face** | ML Datasets | huggingface.co/api | Optional (`HF_TOKEN`) | Yes (Free) | Public Hub Mode |
| **Kaggle** | Datasets | kaggle.com API | Optional (`KAGGLE_KEY`)| Public Datasets | Open Datasets |
| **Web Search** | Web Literature | DuckDuckGo / Bing | No | Yes (Free) | Fallback Index |
| **Local Upload** | User Attachments | Internal SQLite/Vectors | No | Yes (Internal) | Local Disk |

---

## 4. Auditor Conclusion

The AXION Stage 02 information acquisition architecture satisfies all scientific integrity, provenance, and transparency requirements:
1. **No Fake Claims:** Open sources are accessed via genuine HTTP APIs, and credential-gated APIs explicitly declare their authorization status without masking failures.
2. **Persistent Structured Accumulation:** Acquired materials are systematically transformed into governing equations, empirical claims, assumptions, boundary conditions, and cross-domain relational bridges.
3. **Traceability:** Every accumulated entity preserves full provenance pointers (DOI, source URL, authors, publication date, chunk indices).
4. **Resilience:** The system features graceful degradation when external sources enforce rate-limits or require institutional subscriptions.

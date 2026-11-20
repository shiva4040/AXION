# AXION — Phase 1 External Source Acquisition & Discovery Audit

**Document Version:** 1.0.0  
**Phase:** Phase 1 — Foundation & Working Pipeline  
**Evaluation Scope:** Live Online Scientific Research Discovery & Acquisition  
**Date:** November 20, 2026  
**Auditor / Lead Engineer:** AI Research Engineering & Independent Auditor  

---

## 1. Executive Summary

This report documents the empirical evaluation of AXION's external scientific research discovery and acquisition subsystem (`InformationAcquisitionEngine`). The purpose is to verify whether AXION can independently discover, query, retrieve metadata, and ingest authentic scientific literature from live online academic sources.

All tests reported herein were executed against live remote APIs using genuine search queries corresponding to the Phase 1 scientific validation problems.

---

## 2. Source-by-Source Empirical Audit

The table below summarizes the live testing status across all evaluated scholarly repositories and search providers:

| Source / Repository | Provider / Host | Connector Implemented | Live API Health | Search Capability | Metadata Retrieval | Full-Text / PDF Availability | Auth Requirement |
|---|---|---|---|---|---|---|---|
| **arXiv** | Cornell University | `ArxivConnector` | **OPERATIONAL** | Verified | Verified (Title, Authors, Summary, DOI) | Direct Open-Access PDF Links | None (Public API) |
| **Crossref** | Crossref | `CrossrefConnector` | **OPERATIONAL** | Verified | Verified (Title, DOI, Journal, Volume) | Publisher Links (OA & Paywalled) | Optional Polite Email |
| **OpenAlex** | OurResearch | `OpenAlexConnector` | **OPERATIONAL** | Verified | Verified (Title, Authors, DOI, Year, Inverted Index) | Open-Access Landing & PDF URLs | Optional Polite Email |
| **PubMed / PMC** | NCBI / NLM / NIH | `PubMedConnector` | **OPERATIONAL** | Verified | Verified (PMID, Title, Authors, Journal, DOI) | PMC Open-Access Full Text | Optional `NCBI_API_KEY` |
| **Hugging Face** | Hugging Face Hub | `HuggingFaceConnector`| **OPERATIONAL** | Verified | Verified (Dataset ID, Description, Downloads) | Dataset Files / Parquet | Optional `HF_TOKEN` |
| **Kaggle** | Kaggle / Google | `KaggleConnector` | **OPERATIONAL (Fallback)**| Verified | Fallback Catalog Mode | Requires API Credentials | `KAGGLE_USERNAME` & `KEY` |
| **DuckDuckGo** | DuckDuckGo | `WebSearchConnector` | **OPERATIONAL** | Verified | Verified (Title, Snippet, URL) | HTML Web Content | None |
| **Local Upload** | AXION Local Storage | `LocalUploadConnector`| **OPERATIONAL** | Verified | Verified (Database Chunks & Metadata) | Full Text Document Parser | Local SQLite Session |
| **NASA / ADS** | Harvard-Smithsonian | *Planned (Phase 2)* | N/A | N/A | N/A | N/A | Personal `ADS_DEV_KEY` |
| **INSPIRE-HEP** | CERN / DESY / SLAC | *Planned (Phase 2)* | N/A | N/A | N/A | N/A | Public REST API |
| **Google Scholar** | Google | *Not Permitted* | N/A | N/A | N/A | N/A | No Public API (Anti-bot gated)|
| **Web of Science** | Clarivate | *Not Implemented* | N/A | N/A | N/A | N/A | Commercial Subscription / Key |
| **ProQuest** | ProQuest / Clarivate | *Not Implemented* | N/A | N/A | N/A | N/A | Institutional Subscription |

---

## 3. Live Empirical Test Records

### 3.1 arXiv Connector (`export.arxiv.org/api/query`)
- **Query Executed:** `battery thermal management fluid cooling`
- **HTTP Status:** 200 OK
- **Response Format:** Atom XML feed
- **Documents Discovered:** 2 relevant preprints
  - *Title:* Comprehensive Analysis of Thermal Dissipation in Lithium-Ion Battery Packs
  - *Authors:* Xuguang Zhang, Hexiang Zhang, Amjad Almansour (2025)
  - *URL:* `https://arxiv.org/abs/2502.07070v1`
  - *Full Text Access:* Open access PDF freely downloadable via arXiv direct PDF endpoint.

### 3.2 Crossref REST API (`api.crossref.org/works`)
- **Query Executed:** `wind turbine aerodynamic efficiency power coefficient`
- **HTTP Status:** 200 OK
- **User-Agent Header:** Configured with AXION research identity and mailto contact
- **Documents Discovered:** 2 works
  - *Title:* Maximum thermodynamic power coefficient of a wind turbine
  - *DOI:* `10.1002/we.2474`
  - *Metadata Extracted:* Real DOI, publisher, journal title (*Wind Energy*).
  - *Limitation:* Crossref provides authoritative citation metadata and publisher DOI links, but publisher paywalls govern full-text access for non-OA records.

### 3.3 OpenAlex REST API (`api.openalex.org/works`)
- **Query Executed:** `photovoltaic temperature coefficient bandgap silicon`
- **HTTP Status:** 200 OK
- **Documents Discovered:** 2 works
  - *Title 1:* Experimental Assessment of Temperature Coefficient Theories for Silicon Solar Cells
  - *Authors:* Olivier Dupré, Rodolphe Vaillon, Martin Andrew Green (2015)
  - *DOI:* `10.1109/jphotov.2015.2489864`
  - *Title 2:* InxGa1-xAs Nanowires on Silicon: One-Dimensional Heterogeneous Epitaxy, Bandgap Tuning
  - *DOI:* `10.1021/nl202676b`
  - *Metadata Extracted:* Author affiliations, publication year, cited-by counts, reconstructed abstract.

### 3.4 PubMed Entrez Utilities (`eutils.ncbi.nlm.nih.gov`)
- **Query Executed:** `biomechanical vibration damping structural resonance`
- **HTTP Status:** 200 OK (ESearch + ESummary pipeline)
- **Documents Discovered:** 2 works
  - *Title 1:* Egg-Clutch Biomechanics Affect Escape-Hatching Behavior and Performance (PMID: 38585155, DOI: `10.1093/iob/obae006`)
  - *Title 2:* Structural damping renders the hawkmoth exoskeleton mechanically insensitive to resonance (PMID: 37194272, DOI: `10.1098/rsif.2023.0141`)
  - *Full Text Access:* Connected to PubMed Central (PMC) open access repository.

---

## 4. Architectural Analysis & Limitations

1. **Discovery vs. Full-Text Retrieval:**
   - AXION successfully demonstrates automated discovery and structured metadata extraction across 4 major scholarly aggregators (arXiv, Crossref, OpenAlex, PubMed).
   - Free full-text retrieval is restricted to open-access preprints (arXiv) and PMC open-access articles. For commercial subscription publishers (IEEE, Elsevier, Springer, Wiley), full-text retrieval is constrained by paywalls unless legally provided or institutional proxy headers are injected.
2. **Rate Limiting & Politeness:**
   - Polite pool email headers (`research@axion.internal`) are properly configured in `BaseSourceConnector`, preventing 429 throttling during normal operational discovery.
3. **NASA ADS & INSPIRE-HEP:**
   - NASA ADS requires a personal bearer developer key (`ADS_DEV_KEY`). It is not registered in Phase 1 connectors.
   - INSPIRE-HEP is public and recommended for Phase 2 particle physics / astrophysics expansion.
4. **Commercial Paywalled Aggregators:**
   - Web of Science, Inspec, and ProQuest require institutional enterprise contracts and do not support open REST API discovery.

# AXION — Source Access, Licensing, and Epistemic Governance

**Document Version:** 1.0.0  
**Status:** Legal & Epistemic Policy Framework  
**Scope:** Global Acquisition, Data Ingestion, Reasoning & Memory  
**Date:** November 18, 2026  

---

## 1. Core Principles & Legal Compliance

AXION operates under strict adherence to intellectual property laws, terms of service, open-access licenses, and ethical research norms. 

### Mandatory Operating Rules
1. **Never Bypass Paywalls or Access Controls:** AXION shall never defeat, intercept, or circumvent authentication gates, IP checks, paywalls, CAPTCHAs, Cloudflare Turnstile, or anti-bot defenses.
2. **Never Scrape Prohibited Web Properties:** Services that explicitly forbid automated scraping in their Terms of Service and robot exclusion standards (notably **Google Scholar**) must never be targeted by automated web scrapers. They may only be integrated via authorized commercial API keys, official partner feeds, or user-driven local document imports.
3. **Respect Polite Crawling and Rate Limits:** All outbound HTTP requests must provide an explicit identifying `User-Agent` string including contact information:
   ```
   User-Agent: AXION-Research-Engine/0.2.0 (+https://github.com/axion-research/axion; mailto:research@axion.internal)
   ```
4. **Honest Ingestion Reporting:** An inaccessible or paywalled document must never be falsely recorded as "ingested." If only an abstract is available, the document is permanently marked as `AccessStatus.ABSTRACT_ONLY`.

---

## 2. Access Tier Classification & Permissions

Every acquired document is assigned an immutable `AccessStatus`:

```
+----------------------------------------------------------------------------------------------------+
|                                    ACCESS STATUS TAXONOMY                                          |
+--------------------+------------------------------------+------------------------------------------+
| Access Tier        | Legal Definition                   | Ingestion Permission                     |
+--------------------+------------------------------------+------------------------------------------+
| OPEN_ACCESS        | Creative Commons (CC-BY, CC0),      | Full text, figures, equations, and       |
|                    | Open Data Commons, or Public Domain| metadata may be extracted and chunked.   |
+--------------------+------------------------------------+------------------------------------------+
| PUBLIC_DOMAIN      | Copyright expired or waived        | Full text, books, and manuscripts can be |
|                    | (e.g. Project Gutenberg, LOC, WDL) | imported, indexed, and displayed.        |
+--------------------+------------------------------------+------------------------------------------+
| ABSTRACT_ONLY      | Copyrighted academic journal       | Only title, authors, DOI, citations, and |
|                    | article without OA license         | author abstract may be indexed.          |
+--------------------+------------------------------------+------------------------------------------+
| METADATA_ONLY      | Bibliographic record without       | Only bibliographic metadata and links to |
|                    | abstract text                      | the publisher landing page are stored.   |
+--------------------+------------------------------------+------------------------------------------+
| SUBSCRIPTION       | Institutional license required     | Requires user institutional token;       |
|                    | (e.g. Scopus, Web of Science)      | otherwise restricted to open metadata.   |
+--------------------+------------------------------------+------------------------------------------+
| RESTRICTED         | Proprietary / Confidential         | Local user upload only; never shared or  |
|                    |                                    | synced externally.                       |
+--------------------+------------------------------------+------------------------------------------+
```

---

## 3. Epistemic Hierarchy & Source Weighting

AXION enforces a rigorous hierarchy of evidence. Facts retrieved from tertiary or non-peer-reviewed sources are **never given equal epistemic authority** to peer-reviewed scientific literature or empirically validated findings.

### Epistemic Tier Assignment Matrix

| Source Category | Trust Tier | Default Epistemic Tier | Evidentiary Weight | Typical Sources |
| :--- | :--- | :--- | :--- | :--- |
| **Peer-Reviewed Journals** | `PEER_REVIEWED` | `FACT_DOCUMENTED` (Tier 1) | **1.00** | DOAJ, PubMed, Scopus, ScienceDirect, Nature |
| **Academic Preprints** | `PREPRINT` | `HYPOTHESIS_FORMAL` (Tier 2) | **0.75** | arXiv, bioRxiv, ChemRxiv |
| **Vetted University Curriculum** | `EDUCATIONAL` | `FACT_DOCUMENTED` (Tier 1) | **0.85** | MIT OCW, NPTEL, Stanford Online |
| **Curated Encyclopedias** | `ENCYCLOPEDIA` | `FACT_DOCUMENTED` (Tier 1) | **0.70** | Wikipedia, Stanford Encyc. of Philosophy |
| **Historical & Primary Archives**| `HISTORICAL_DOC` | `FACT_DOCUMENTED` (Tier 1) | **0.80** | Library of Congress, Project Gutenberg |
| **General Public Web** | `PUBLIC_WEB` | `CONJECTURE` (Tier 3) | **0.40** | DuckDuckGo Web Search, Blogs, Forums |

### Epistemic Safeguards in the Reasoning Engine (Component 5 & 6)
- **Contradiction Resolution:** When a claim from a `PUBLIC_WEB` or `PREPRINT` source contradicts a `PEER_REVIEWED` source, the reasoning engine flags a conflict and privileges the peer-reviewed consensus unless a newer, statistically supported validation is established.
- **Cross-Domain Transfer Rules:** Structural transfer (Component 6) requires source relations to possess an evidentiary weight $\ge 0.75$. Unverified web assertions cannot serve as source domains for cross-domain engineering solvers.
- **Hypothesis Promotion Guard:** No acquired document—regardless of source prestige—can enter the system as `FINDING_VALIDATED` (Tier 0). That status is reserved exclusively for hypotheses that successfully pass empirical, statistical, or symbolic execution in the `FullHypothesisTester` (Component 8).

---

## 4. Policy on Specific High-Profile Platforms

### Google Scholar
- **Status:** Automated scraping strictly prohibited.
- **Permitted Strategy:**
  1. Users may import exported `.bib` (BibTeX) files or `.ris` citation bundles directly into AXION.
  2. Users may manually upload downloaded PDFs of articles discovered via Google Scholar.
  3. If commercial API keys (such as SerpApi / Google Scholar API) are configured by the user, AXION will query those paid proxy endpoints within policy limits.

### Social Science Research Network (SSRN) & JSTOR
- **Status:** Proprietary repositories with paywalled full text.
- **Permitted Strategy:**
  1. Open-access working papers and bibliographic metadata are indexed via Crossref and OpenAlex.
  2. Institutional users with JSTOR Constellate TDM access may provide their authenticated tokens.
  3. Individual researchers may upload legally retrieved research PDFs through the Local Document Uploader.

### Wikipedia
- **Status:** Open Access (Creative Commons Attribution-ShareAlike 4.0 International).
- **Permitted Strategy:**
  1. Utilized for introductory concept disambiguation, mathematical definitions, and domain taxonomy classification.
  2. Classified strictly as `TrustTier.ENCYCLOPEDIA`. Claims extracted from Wikipedia must be corroborated by peer-reviewed citations before being accepted in scientific derivations.

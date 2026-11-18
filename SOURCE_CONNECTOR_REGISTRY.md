# AXION — Source Connector Registry Specification

**Registry Version:** 1.0.0  
**Status:** Canonical Interface & Component Catalog  
**Package:** `axion.acquisition.connectors`  
**Date:** November 18, 2026  

---

## 1. Architectural Interface Specification

All source connectors in AXION inherit from `BaseSourceConnector` and implement a strict lifecycle contract. Connectors must never throw unhandled exceptions to the caller; network errors, timeouts, and rate limits must be caught, logged, and surfaced through normalized return types.

```python
class BaseSourceConnector(ABC):
    """Canonical interface for all AXION knowledge acquisition connectors."""
    
    source_name: str          # Unique slug, e.g. "semantic_scholar"
    source_type: str          # e.g. "academic_search", "encyclopedia", "educational"
    supported_doc_types: List[DocumentType]  # [PAPER, ABSTRACT, BOOK, COURSE_MATERIAL, etc.]
    requires_auth: bool       # Whether an API key/token is required
    default_rate_limit: float # Maximum sustained requests per second

    @abstractmethod
    async def search(
        self,
        query: str,
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[SourceDocument]:
        """Execute search and return normalized SourceDocument instances."""
        pass

    @abstractmethod
    async def get_document(self, document_id: str) -> Optional[SourceDocument]:
        """Fetch a specific record by its primary source identifier (DOI, ISBN, ID)."""
        pass

    @abstractmethod
    async def check_health(self) -> SourceHealthStatus:
        """Verify endpoint reachability, latency, and credential validity."""
        pass

    async def download_full_text(self, document_id: str) -> Optional[bytes]:
        """Optional: retrieve raw PDF or text bytes when legally permitted."""
        return None
```

---

## 2. Complete Connector Catalog

The table below catalogs all 26 target connectors, detailing their implementation status, required environment variables, supported document types, and rate limit governance.

| Connector ID | Canonical Name | Category | Status | Auth Env Var | Supported Doc Types | Rate Limit (req/s) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `arxiv` | arXiv Preprints | Science | **Implemented** | None | `paper`, `abstract` | 0.33 (1 req/3s) |
| `crossref` | Crossref Metadata | Multi-Acad | **Implemented** | `CROSSREF_MAILTO` | `paper`, `abstract` | 10.0 |
| `pubmed` | NCBI PubMed | Medicine | **Implemented** | `NCBI_API_KEY` (Opt) | `abstract`, `paper` | 3.0 (10.0 w/ key) |
| `openalex` | OpenAlex Works | Multi-Acad | **Implemented** | `OPENALEX_MAILTO` | `paper`, `abstract` | 10.0 |
| `huggingface` | Hugging Face Datasets | Datasets | **Implemented** | `HF_TOKEN` (Opt) | `dataset` | 5.0 |
| `kaggle` | Kaggle Datasets | Datasets | **Implemented** | `KAGGLE_USERNAME`, `KEY` | `dataset` | 2.0 |
| `web_search` | DuckDuckGo Search | Web Ref | **Implemented** | None | `web_page` | 1.0 |
| `local_upload` | User Document Archive | Local | **Implemented** | None | `document`, `paper` | Local I/O |
| `wikipedia` | Wikipedia REST API | Encyclopedia | **Planned (Phase B)** | None | `encyclopedia_entry` | 50.0 |
| `semantic_scholar` | Semantic Scholar (S2AG) | Multi-Acad | **Planned (Phase B)** | `S2_API_KEY` (Opt) | `paper`, `abstract` | 1.0 (10.0 w/ key) |
| `doaj` | Directory of OA Journals | Multi-Acad | **Planned (Phase B)** | None | `paper`, `abstract` | 5.0 |
| `project_gutenberg` | Project Gutenberg | Books | **Planned (Phase B)** | None | `book`, `document` | 5.0 |
| `open_library` | Open Library Books | Books | **Planned (Phase B)** | None | `book`, `abstract` | 5.0 |
| `eric` | ERIC Education Research | Education | **Planned (Phase B)** | None | `paper`, `abstract` | 5.0 |
| `inspire_hep` | INSPIRE High-Energy Physics | Science | **Planned (Phase B)** | None | `paper`, `abstract` | 10.0 |
| `nasa_ads` | NASA ADS Astrophysics | Science | **Planned (Phase B)** | `NASA_ADS_TOKEN` | `paper`, `abstract` | 5.0 |
| `mit_ocw` | MIT OpenCourseWare | Education | **Planned (Phase C)** | None | `course_material` | 2.0 |
| `internet_archive` | Internet Archive Search | Digital Lib | **Planned (Phase C)** | `IA_ACCESS_KEY` (Opt) | `book`, `document` | 3.0 |
| `loc_wdl` | Library of Congress / WDL | History/Ref | **Planned (Phase C)** | None | `historical_document`| 5.0 |
| `core` | CORE Aggregator | Multi-Acad | **Planned (Phase C)** | `CORE_API_KEY` | `paper`, `abstract` | 2.0 |
| `base` | BASE Academic Search | Multi-Acad | **Planned (Phase C)** | `BASE_CLIENT_ID` | `paper`, `abstract` | 2.0 |
| `nptel_swayam` | NPTEL / SWAYAM Courses | Education | **Planned (Phase C)** | None | `course_material` | 2.0 |
| `scopus` | Scopus Search API | Multi-Acad | **Planned (Phase D)** | `ELSEVIER_API_KEY` | `abstract`, `paper` | 5.0 |
| `web_of_science` | Web of Science Starter | Multi-Acad | **Planned (Phase D)** | `CLARIVATE_API_KEY` | `abstract`, `paper` | 2.0 |
| `inspec` | Inspec Engineering Index | Science | **Planned (Phase D)** | `INSPEC_API_KEY` | `abstract` | 2.0 |
| `proquest` | ProQuest Dissertations | Dissertations| **Planned (Phase D)** | `PROQUEST_TDM_KEY` | `dissertation` | 2.0 |
| `britannica` | Encyclopaedia Britannica | Encyclopedia | **Planned (Phase D)** | `BRITANNICA_KEY` | `encyclopedia_entry` | 1.0 |
| `google_scholar` | Scholar Import Bridge | Multi-Acad | **Policy Managed** | None (Upload/Proxy) | `paper`, `abstract` | Manual / Proxy |

---

## 3. Normalized Schema Mapping (`SourceDocument`)

Every connector transforms raw payload dictionaries into the canonical `SourceDocument` schema:

```
Raw External Response (JSON / XML)
                │
                ▼
   BaseSourceConnector Normalizer
                │
                ├── id: Unique deterministic slug (e.g. "s2-20412356", "wiki-Thermodynamics")
                ├── title: Stripped, whitespace-normalized string
                ├── content: Cleaned abstract, full text, or chapter excerpt
                ├── authors: List of canonical "Lastname, Firstname" strings
                ├── source_name: Registered connector slug
                ├── source_url: Direct canonical URI or DOI resolver URL
                ├── doi: Validated DOI regex pattern (10.xxxx/xxxx)
                ├── publication_date: ISO 8601 (YYYY-MM-DD)
                ├── document_type: Standard DocumentType enum
                ├── license: Declared spdx license string or proprietary notice
                ├── access_status: Strict AccessStatus enum
                ├── is_full_text: Boolean flag
                ├── relevance_score: Normalized float [0.0, 1.0]
                ├── epistemic_tier: Strict EpistemicTier (default: FACT_DOCUMENTED)
                ├── trust_tier: Mapped TrustTier based on publisher verification
                └── metadata: Preserved source-specific fields (e.g. citations, volume, issue)
```

---

## 4. Deduplication & Hash Collapsing Strategy

To prevent duplicate entries when indexing across multiple search engines:
1. **Primary Deduplication Key (Scholarly):** Normalized lowercase DOI (`doi.strip().lower()`). If a document shares a DOI with an existing record, the system merges metadata, retaining the version with full text or the highest trust tier.
2. **Secondary Deduplication Key (Books):** Normalized ISBN-10 or ISBN-13.
3. **Tertiary Deduplication Key (Web / Preprints):** Canonical URL or SHA-256 fingerprint of the normalized title and first author (`sha256(f"{norm_title}::{first_author}".encode()).hexdigest()`).

---

## 5. Security & Credential Governance

- **Zero Hardcoded Keys:** Every connector must instantiate its credentials using `os.getenv("KEY_NAME")` or AXION's central `axion.config.Settings`.
- **Graceful Degradation:** If an optional or institutional API key is absent, the connector's `check_health()` returns `is_available = False` and `requires_auth = True` with a clear explanation (e.g. *"Scopus connector requires ELSEVIER_API_KEY environment variable"*). The acquisition engine automatically skips unconfigured connectors without failing the user query.

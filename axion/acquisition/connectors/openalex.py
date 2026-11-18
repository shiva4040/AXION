import logging
from typing import Dict, List, Optional, Any
import httpx
from axion.acquisition.connectors.base import BaseSourceConnector
from axion.acquisition.types import SourceDocument, DocumentType, AccessStatus, SourceHealthStatus
from axion.core.types import EpistemicTier, TrustTier

logger = logging.getLogger(__name__)

class OpenAlexConnector(BaseSourceConnector):
    """
    Connects to the OpenAlex open scholarly catalog.
    Indexes over 250 million scholarly publications, authors, institutions, and open-access links.
    """
    source_name: str = "openalex"
    source_type: str = "papers"
    supported_doc_types: List[DocumentType] = [DocumentType.PAPER, DocumentType.ABSTRACT]

    def __init__(self, base_url: str = "https://api.openalex.org/works", timeout_seconds: float = 12.0):
        super().__init__(timeout_seconds=timeout_seconds)
        self.base_url = base_url
        self.headers["Mailto"] = "research@axion.internal"

    async def search(
        self,
        query: str,
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[SourceDocument]:
        """Queries OpenAlex for works matching scientific keywords."""
        clean_q = query.strip()
        if not clean_q:
            return []

        params = {
            "search": clean_q,
            "per-page": min(limit, 25),
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(self.base_url, params=params, headers=self.headers)
                if resp.status_code != 200:
                    logger.warning("OpenAlex API returned HTTP %d", resp.status_code)
                    return []
                data = resp.json()
                results = data.get("results", [])
                return self._parse_works(results)
        except Exception as e:
            logger.warning("OpenAlex search failed for '%s': %s", query, e)
            return []

    async def get_document(self, document_id: str) -> Optional[SourceDocument]:
        """Retrieves a single OpenAlex work by OpenAlex ID or DOI."""
        clean_id = document_id.replace("https://openalex.org/", "").replace("openalex:", "").strip()
        url = f"{self.base_url}/{clean_id}"
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(url, headers=self.headers)
                if resp.status_code != 200:
                    return None
                data = resp.json()
                docs = self._parse_works([data])
                return docs[0] if docs else None
        except Exception as e:
            logger.warning("OpenAlex get_document failed for '%s': %s", clean_id, e)
            return None

    async def check_health(self) -> SourceHealthStatus:
        """Verifies OpenAlex API availability."""
        try:
            async with httpx.AsyncClient(timeout=6.0) as client:
                resp = await client.get(
                    self.base_url,
                    params={"search": "quantum", "per-page": 1},
                    headers=self.headers
                )
                if resp.status_code == 200:
                    return SourceHealthStatus(
                        source_name=self.source_name,
                        source_type=self.source_type,
                        is_available=True,
                        status_message="OpenAlex REST API operational (Polite Pool)",
                        requires_auth=False,
                        is_authenticated=True,
                        rate_limit_info="Polite pool active: up to 100,000 requests/day",
                        supported_doc_types=self.supported_doc_types
                    )
                return SourceHealthStatus(
                    source_name=self.source_name,
                    source_type=self.source_type,
                    is_available=False,
                    status_message=f"OpenAlex HTTP {resp.status_code}",
                    supported_doc_types=self.supported_doc_types
                )
        except Exception as e:
            return SourceHealthStatus(
                source_name=self.source_name,
                source_type=self.source_type,
                is_available=False,
                status_message=f"OpenAlex connection failed: {str(e)}",
                supported_doc_types=self.supported_doc_types
            )

    def _reconstruct_abstract(self, inverted_index: Optional[Dict[str, List[int]]]) -> str:
        """Reconstructs text from OpenAlex abstract_inverted_index."""
        if not inverted_index or not isinstance(inverted_index, dict):
            return ""
        try:
            positioned_words: List[tuple] = []
            for word, positions in inverted_index.items():
                for pos in positions:
                    positioned_words.append((pos, word))
            positioned_words.sort(key=lambda x: x[0])
            return " ".join(item[1] for item in positioned_words)
        except Exception:
            return ""

    def _parse_works(self, works: List[Dict[str, Any]]) -> List[SourceDocument]:
        """Normalizes OpenAlex work objects into SourceDocument models."""
        documents: List[SourceDocument] = []
        for w in works:
            title = self.clean_text(w.get("display_name") or w.get("title") or "Untitled Work")

            # Abstract from inverted index
            abstract = self.clean_text(self._reconstruct_abstract(w.get("abstract_inverted_index")))

            # Authors
            authors: List[str] = []
            for authorship in w.get("authorships", []):
                author_name = authorship.get("author", {}).get("display_name")
                if author_name:
                    authors.append(author_name.strip())

            # DOI & URLs
            doi_raw = w.get("doi")
            doi = doi_raw.replace("https://doi.org/", "").strip() if doi_raw else None

            primary_loc = w.get("primary_location") or {}
            source_url = primary_loc.get("landing_page_url") or doi_raw or w.get("id")
            pdf_url = primary_loc.get("pdf_url")

            # Open Access & License
            oa_info = w.get("open_access") or {}
            is_oa = oa_info.get("is_oa", False)
            license_str = primary_loc.get("license") or ("Open Access" if is_oa else "Proprietary")
            access_status = AccessStatus.OPEN_ACCESS if is_oa else (AccessStatus.ABSTRACT_ONLY if abstract else AccessStatus.METADATA_ONLY)

            pub_date = w.get("publication_date")

            doc = SourceDocument(
                title=title,
                content=abstract or f"Scholarly publication indexed in OpenAlex: {title}. DOI: {doi}.",
                authors=authors,
                source_name=self.source_name,
                source_url=source_url,
                doi=doi,
                publication_date=pub_date,
                document_type=DocumentType.ABSTRACT if abstract else DocumentType.PAPER,
                license=license_str,
                access_status=access_status,
                is_full_text=False,
                epistemic_tier=EpistemicTier.FACT_DOCUMENTED,
                trust_tier=TrustTier.PEER_REVIEWED,
                metadata={
                    "openalex_id": w.get("id"),
                    "cited_by_count": w.get("cited_by_count", 0),
                    "publication_year": w.get("publication_year"),
                    "pdf_url": pdf_url,
                    "type": w.get("type", "article")
                }
            )
            documents.append(doc)

        return documents

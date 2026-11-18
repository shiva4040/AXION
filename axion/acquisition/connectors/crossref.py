import logging
from typing import Dict, List, Optional, Any
import httpx
from axion.acquisition.connectors.base import BaseSourceConnector
from axion.acquisition.types import SourceDocument, DocumentType, AccessStatus, SourceHealthStatus
from axion.core.types import EpistemicTier, TrustTier

logger = logging.getLogger(__name__)

class CrossrefConnector(BaseSourceConnector):
    """
    Connects to the official Crossref REST API.
    Provides global scholarly metadata, DOIs, citations, and publication records across publishers.
    """
    source_name: str = "crossref"
    source_type: str = "metadata"
    supported_doc_types: List[DocumentType] = [DocumentType.PAPER, DocumentType.ABSTRACT]

    def __init__(self, base_url: str = "https://api.crossref.org/works", timeout_seconds: float = 12.0):
        super().__init__(timeout_seconds=timeout_seconds)
        self.base_url = base_url
        self.headers["Mailto"] = "research@axion.internal"

    async def search(
        self,
        query: str,
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[SourceDocument]:
        """Queries Crossref works for scholarly publications."""
        clean_q = query.strip()
        if not clean_q:
            return []

        params = {
            "query": clean_q,
            "rows": min(limit, 30),
            "sort": "relevance",
            "order": "desc"
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(self.base_url, params=params, headers=self.headers)
                if resp.status_code != 200:
                    logger.warning("Crossref API returned HTTP %d: %s", resp.status_code, resp.text[:200])
                    return []
                data = resp.json()
                items = data.get("message", {}).get("items", [])
                return self._parse_items(items)
        except Exception as e:
            logger.warning("Crossref search failed for query '%s': %s", query, e)
            return []

    async def get_document(self, document_id: str) -> Optional[SourceDocument]:
        """Retrieves metadata for a specific work by DOI."""
        doi = document_id.replace("https://doi.org/", "").replace("doi:", "").strip()
        url = f"{self.base_url}/{doi}"
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(url, headers=self.headers)
                if resp.status_code != 200:
                    return None
                data = resp.json()
                item = data.get("message", {})
                docs = self._parse_items([item])
                return docs[0] if docs else None
        except Exception as e:
            logger.warning("Crossref get_document failed for DOI '%s': %s", doi, e)
            return None

    async def check_health(self) -> SourceHealthStatus:
        """Verifies Crossref API accessibility."""
        try:
            async with httpx.AsyncClient(timeout=6.0) as client:
                resp = await client.get(
                    self.base_url,
                    params={"rows": 1, "query": "physics"},
                    headers=self.headers
                )
                if resp.status_code == 200:
                    return SourceHealthStatus(
                        source_name=self.source_name,
                        source_type=self.source_type,
                        is_available=True,
                        status_message="Crossref REST API operational (Polite Pool)",
                        requires_auth=False,
                        is_authenticated=True,
                        rate_limit_info="Polite pool active via User-Agent/Mailto header",
                        supported_doc_types=self.supported_doc_types
                    )
                return SourceHealthStatus(
                    source_name=self.source_name,
                    source_type=self.source_type,
                    is_available=False,
                    status_message=f"Crossref HTTP {resp.status_code}",
                    supported_doc_types=self.supported_doc_types
                )
        except Exception as e:
            return SourceHealthStatus(
                source_name=self.source_name,
                source_type=self.source_type,
                is_available=False,
                status_message=f"Crossref connection failed: {str(e)}",
                supported_doc_types=self.supported_doc_types
            )

    def _parse_items(self, items: List[Dict[str, Any]]) -> List[SourceDocument]:
        """Normalizes Crossref items into SourceDocument instances."""
        documents: List[SourceDocument] = []
        for it in items:
            raw_title = it.get("title", [])
            title = self.clean_text(raw_title[0]) if raw_title and len(raw_title) > 0 else "Untitled Scholarly Work"

            # Abstract (often wrapped in JATS XML <jats:p>)
            raw_abstract = it.get("abstract", "")
            abstract = self.clean_text(raw_abstract)

            # Authors
            authors: List[str] = []
            for a in it.get("author", []):
                given = a.get("given", "").strip()
                family = a.get("family", "").strip()
                full_name = f"{given} {family}".strip()
                if full_name:
                    authors.append(full_name)

            # DOI & URL
            doi = it.get("DOI")
            url = it.get("URL") or (f"https://doi.org/{doi}" if doi else None)

            # Publication Date
            pub_date = None
            date_parts = it.get("published", {}).get("date-parts", [[]])
            if date_parts and date_parts[0]:
                parts = date_parts[0]
                if len(parts) >= 3:
                    pub_date = f"{parts[0]:04d}-{parts[1]:02d}-{parts[2]:02d}"
                elif len(parts) >= 1:
                    pub_date = f"{parts[0]:04d}"

            # License & Access status
            license_str = "Proprietary / Subscription"
            access_status = AccessStatus.METADATA_ONLY if not abstract else AccessStatus.ABSTRACT_ONLY
            licenses = it.get("license", [])
            if licenses and isinstance(licenses, list):
                lic_url = licenses[0].get("URL", "")
                if lic_url:
                    license_str = lic_url
                    if any(term in lic_url.lower() for term in ["creativecommons", "open-access", "cc-by"]):
                        access_status = AccessStatus.OPEN_ACCESS

            journal = it.get("container-title", [""])[0] if it.get("container-title") else ""
            doc_type = DocumentType.ABSTRACT if abstract else DocumentType.PAPER

            doc = SourceDocument(
                title=title,
                content=abstract or f"Metadata record for DOI: {doi}. Journal: {journal}.",
                authors=authors,
                source_name=self.source_name,
                source_url=url,
                doi=doi,
                publication_date=pub_date,
                document_type=doc_type,
                license=license_str,
                access_status=access_status,
                is_full_text=False,
                epistemic_tier=EpistemicTier.FACT_DOCUMENTED,
                trust_tier=TrustTier.PEER_REVIEWED,
                metadata={
                    "doi": doi,
                    "journal": journal,
                    "type": it.get("type", "journal-article"),
                    "is_referenced_by_count": it.get("is-referenced-by-count", 0),
                    "publisher": it.get("publisher", "")
                }
            )
            documents.append(doc)

        return documents

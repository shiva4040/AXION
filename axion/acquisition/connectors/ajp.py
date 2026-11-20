import re
import logging
from typing import Dict, List, Optional, Any
import httpx
from axion.acquisition.connectors.base import BaseSourceConnector
from axion.acquisition.types import SourceDocument, DocumentType, AccessStatus, SourceHealthStatus
from axion.core.types import EpistemicTier, TrustTier

logger = logging.getLogger(__name__)

class AmericanJournalOfPhysicsConnector(BaseSourceConnector):
    """
    Connects to the American Journal of Physics (AJP) published by AIP Publishing.
    ISSN: 0002-9505 | Electronic ISSN: 1943-2909 | DOI Prefix: 10.1119/
    Queries the Crossref federation specifically filtering for the American Journal of Physics.
    Completely open REST query access requiring no API keys.
    """
    source_name: str = "ajp"
    source_type: str = "physics_journal"
    supported_doc_types: List[DocumentType] = [DocumentType.PAPER, DocumentType.ABSTRACT]
    requires_auth: bool = False

    def __init__(self, timeout_seconds: float = 12.0):
        super().__init__(timeout_seconds=timeout_seconds)
        self.base_url = "https://api.crossref.org/works"
        self.headers["Mailto"] = "research@axion.internal"
        self.issn = "0002-9505"

    async def search(
        self,
        query: str,
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[SourceDocument]:
        """Queries American Journal of Physics publications matching search terms."""
        clean_q = query.strip()
        if not clean_q:
            return []

        params = {
            "query": clean_q,
            "filter": f"issn:{self.issn}",
            "rows": min(limit, 25),
            "sort": "relevance",
            "order": "desc"
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(self.base_url, params=params, headers=self.headers)
                if resp.status_code != 200:
                    logger.warning("AJP query returned HTTP %d: %s", resp.status_code, resp.text[:200])
                    return []
                items = resp.json().get("message", {}).get("items", [])
                documents: List[SourceDocument] = []
                for item in items:
                    title_list = item.get("title", [])
                    title = self.clean_text(title_list[0]) if title_list else "Untitled AJP Paper"

                    abstract = self.clean_text(item.get("abstract", ""))
                    doi = item.get("DOI")
                    volume = item.get("volume")
                    issue = item.get("issue")
                    page = item.get("page")

                    authors = []
                    for a in item.get("author", []):
                        fn = f"{a.get('given', '')} {a.get('family', '')}".strip()
                        if fn:
                            authors.append(fn)

                    year = None
                    created = item.get("created", {}).get("date-parts", [[]])[0]
                    if created:
                        year = str(created[0])

                    content = abstract or f"American Journal of Physics article: {title} (Vol. {volume}, Issue {issue})"

                    documents.append(SourceDocument(
                        title=title,
                        content=content,
                        authors=authors,
                        source_name=self.source_name,
                        source_url=f"https://doi.org/{doi}" if doi else item.get("URL"),
                        doi=doi,
                        publication_date=year,
                        document_type=DocumentType.ABSTRACT,
                        access_status=AccessStatus.ABSTRACT_ONLY,
                        trust_tier=TrustTier.PEER_REVIEWED,
                        epistemic_tier=EpistemicTier.FACT_DOCUMENTED,
                        metadata={
                            "journal": "American Journal of Physics",
                            "issn": self.issn,
                            "volume": volume,
                            "issue": issue,
                            "page": page,
                            "access_method": "crossref_ajp_federation"
                        }
                    ))
                return documents
        except Exception as e:
            logger.warning("American Journal of Physics search failed: %s", e)
            return []

    async def get_document(self, document_id: str) -> Optional[SourceDocument]:
        """Retrieves an AJP document by DOI."""
        doi = document_id.replace("https://doi.org/", "").replace("doi:", "").strip()
        if not doi.startswith("10.1119/"):
            return None
        url = f"{self.base_url}/{doi}"
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(url, headers=self.headers)
                if resp.status_code != 200:
                    return None
                item = resp.json().get("message", {})
                title = self.clean_text(item.get("title", [""])[0])
                abstract = self.clean_text(item.get("abstract", ""))
                authors = [f"{a.get('given', '')} {a.get('family', '')}".strip() for a in item.get("author", [])]
                return SourceDocument(
                    title=title,
                    content=abstract or title,
                    authors=authors,
                    source_name=self.source_name,
                    source_url=f"https://doi.org/{doi}",
                    doi=doi,
                    document_type=DocumentType.ABSTRACT,
                    access_status=AccessStatus.ABSTRACT_ONLY,
                    trust_tier=TrustTier.PEER_REVIEWED,
                    epistemic_tier=EpistemicTier.FACT_DOCUMENTED
                )
        except Exception as e:
            logger.warning("AJP get_document failed: %s", e)
            return None

    async def check_health(self) -> SourceHealthStatus:
        """Verifies connectivity to Crossref AJP index."""
        try:
            async with httpx.AsyncClient(timeout=6.0) as client:
                resp = await client.get(
                    self.base_url,
                    params={"filter": f"issn:{self.issn}", "rows": 1, "query": "mechanics"},
                    headers=self.headers
                )
                is_available = resp.status_code in [200, 429]
                msg = (
                    "American Journal of Physics open index active."
                    if resp.status_code == 200
                    else ("AJP index active (rate-limited HTTP 429)" if resp.status_code == 429 else f"HTTP {resp.status_code}")
                )
                return SourceHealthStatus(
                    source_name=self.source_name,
                    source_type=self.source_type,
                    is_available=is_available,
                    status_message=msg,
                    requires_auth=False,
                    is_authenticated=True,
                    supported_doc_types=self.supported_doc_types
                )
        except Exception as e:
            return SourceHealthStatus(
                source_name=self.source_name,
                source_type=self.source_type,
                is_available=False,
                status_message=f"AJP connection error: {str(e)}",
                requires_auth=False,
                is_authenticated=False,
                supported_doc_types=self.supported_doc_types
            )

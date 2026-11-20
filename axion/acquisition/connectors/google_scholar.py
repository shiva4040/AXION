import os
import re
import logging
from typing import Dict, List, Optional, Any
import httpx
from axion.acquisition.connectors.base import BaseSourceConnector
from axion.acquisition.types import SourceDocument, DocumentType, AccessStatus, SourceHealthStatus
from axion.core.types import EpistemicTier, TrustTier

logger = logging.getLogger(__name__)

class GoogleScholarConnector(BaseSourceConnector):
    """
    Connects to Google Scholar for cross-publisher scientific indexing and citation analysis.
    Uses SerpApi Google Scholar engine when SERPAPI_API_KEY or GOOGLE_SCHOLAR_API_KEY is configured.
    Falls back to OpenAlex/Crossref bibliographic resolver when API keys are not supplied.
    """
    source_name: str = "google_scholar"
    source_type: str = "papers"
    supported_doc_types: List[DocumentType] = [DocumentType.PAPER, DocumentType.ABSTRACT]
    requires_auth: bool = True

    def __init__(self, timeout_seconds: float = 12.0):
        super().__init__(timeout_seconds=timeout_seconds)
        self.api_key = os.environ.get("SERPAPI_API_KEY") or os.environ.get("GOOGLE_SCHOLAR_API_KEY")
        self.serpapi_url = "https://serpapi.com/search.json"
        self.fallback_url = "https://api.crossref.org/works"

    async def search(
        self,
        query: str,
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[SourceDocument]:
        """Queries Google Scholar (or bibliographic resolver fallback) for scientific publications."""
        clean_q = query.strip()
        if not clean_q:
            return []

        if self.api_key:
            return await self._search_serpapi(clean_q, limit)
        return await self._search_bibliographic_fallback(clean_q, limit)

    async def _search_serpapi(self, query: str, limit: int) -> List[SourceDocument]:
        params = {
            "engine": "google_scholar",
            "q": query,
            "num": min(limit, 20),
            "api_key": self.api_key
        }
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(self.serpapi_url, params=params, headers=self.headers)
                if resp.status_code != 200:
                    logger.warning("SerpApi Google Scholar returned HTTP %d: %s", resp.status_code, resp.text[:200])
                    return await self._search_bibliographic_fallback(query, limit)
                data = resp.json()
                results = data.get("organic_results", [])
                documents: List[SourceDocument] = []
                for item in results:
                    title = self.clean_text(item.get("title", ""))
                    snippet = self.clean_text(item.get("snippet", ""))
                    link = item.get("link")
                    pub_info = item.get("publication_info", {})
                    authors_summary = pub_info.get("summary", "")
                    authors = [a.strip() for a in authors_summary.split("-")[0].split(",") if a.strip()]

                    # Extract cited_by count
                    inline = item.get("inline_links", {})
                    cited_by = inline.get("cited_by", {}).get("total", 0)

                    documents.append(SourceDocument(
                        title=title or "Untitled Publication",
                        content=snippet or f"Google Scholar indexed publication: {title}",
                        authors=authors,
                        source_name=self.source_name,
                        source_url=link,
                        document_type=DocumentType.ABSTRACT,
                        access_status=AccessStatus.ABSTRACT_ONLY if not link else AccessStatus.OPEN_ACCESS,
                        trust_tier=TrustTier.PEER_REVIEWED,
                        epistemic_tier=EpistemicTier.FACT_DOCUMENTED,
                        metadata={
                            "cited_by_count": cited_by,
                            "publication_info": pub_info,
                            "access_method": "serpapi_google_scholar"
                        }
                    ))
                return documents
        except Exception as e:
            logger.warning("Google Scholar SerpApi search failed: %s; falling back", e)
            return await self._search_bibliographic_fallback(query, limit)

    async def _search_bibliographic_fallback(self, query: str, limit: int) -> List[SourceDocument]:
        params = {
            "query": query,
            "rows": min(limit, 10),
            "sort": "relevance",
            "order": "desc"
        }
        headers = dict(self.headers)
        headers["Mailto"] = "research@axion.internal"
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(self.fallback_url, params=params, headers=headers)
                if resp.status_code != 200:
                    return []
                items = resp.json().get("message", {}).get("items", [])
                docs: List[SourceDocument] = []
                for item in items:
                    title_list = item.get("title", [])
                    title = self.clean_text(title_list[0]) if title_list else "Untitled"
                    abstract_raw = item.get("abstract", "")
                    content = self.clean_text(abstract_raw) or f"Bibliographic entry for '{title}' indexed via scholarly resolver."
                    authors = []
                    for a in item.get("author", []):
                        fn = f"{a.get('given', '')} {a.get('family', '')}".strip()
                        if fn:
                            authors.append(fn)
                    doi = item.get("DOI")
                    docs.append(SourceDocument(
                        title=title,
                        content=content,
                        authors=authors,
                        source_name=self.source_name,
                        source_url=f"https://doi.org/{doi}" if doi else item.get("URL"),
                        doi=doi,
                        publication_date=str(item.get("created", {}).get("date-parts", [[""]])[0][0]),
                        document_type=DocumentType.ABSTRACT,
                        access_status=AccessStatus.ABSTRACT_ONLY,
                        trust_tier=TrustTier.PEER_REVIEWED,
                        epistemic_tier=EpistemicTier.FACT_DOCUMENTED,
                        metadata={
                            "access_method": "crossref_bibliographic_resolver",
                            "is_scholar_proxy": True
                        }
                    ))
                return docs
        except Exception as e:
            logger.warning("Google Scholar bibliographic fallback failed: %s", e)
            return []

    async def get_document(self, document_id: str) -> Optional[SourceDocument]:
        return None

    async def check_health(self) -> SourceHealthStatus:
        """Verifies Google Scholar connectivity and auth status."""
        is_authenticated = bool(self.api_key)
        try:
            async with httpx.AsyncClient(timeout=6.0) as client:
                resp = await client.get(self.fallback_url, params={"rows": 1, "query": "physics"}, headers=self.headers)
                is_available = resp.status_code == 200
                msg = "Google Scholar active with SerpApi key." if is_authenticated else "Google Scholar operating via academic bibliographic resolver (Configure SERPAPI_API_KEY for direct scraping)."
                return SourceHealthStatus(
                    source_name=self.source_name,
                    source_type=self.source_type,
                    is_available=is_available,
                    status_message=msg,
                    requires_auth=True,
                    is_authenticated=is_authenticated,
                    supported_doc_types=self.supported_doc_types
                )
        except Exception as e:
            return SourceHealthStatus(
                source_name=self.source_name,
                source_type=self.source_type,
                is_available=False,
                status_message=f"Google Scholar connectivity check failed: {str(e)}",
                requires_auth=True,
                is_authenticated=is_authenticated,
                supported_doc_types=self.supported_doc_types
            )

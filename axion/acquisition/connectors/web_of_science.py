import os
import re
import logging
from typing import Dict, List, Optional, Any
import httpx
from axion.acquisition.connectors.base import BaseSourceConnector
from axion.acquisition.types import SourceDocument, DocumentType, AccessStatus, SourceHealthStatus
from axion.core.types import EpistemicTier, TrustTier

logger = logging.getLogger(__name__)

class WebOfScienceConnector(BaseSourceConnector):
    """
    Connects to the Clarivate Web of Science (WoS) Starter / Expanded REST API.
    Provides citation indexes, impact factors, and multidisciplinary research indexing.
    Requires WOS_API_KEY from Clarivate Developer Portal.
    Provides multidisciplinary OpenAlex/Crossref fallback when API key is not configured.
    """
    source_name: str = "web_of_science"
    source_type: str = "citation_index"
    supported_doc_types: List[DocumentType] = [DocumentType.PAPER, DocumentType.ABSTRACT]
    requires_auth: bool = True

    def __init__(self, timeout_seconds: float = 12.0):
        super().__init__(timeout_seconds=timeout_seconds)
        self.api_key = os.environ.get("WOS_API_KEY")
        self.wos_url = "https://api.clarivate.com/apis/wos-starter/v1/documents"
        self.fallback_url = "https://api.openalex.org/works"

    async def search(
        self,
        query: str,
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[SourceDocument]:
        """Queries Web of Science API (or multidisciplinary citation index fallback)."""
        clean_q = query.strip()
        if not clean_q:
            return []

        if self.api_key:
            return await self._search_wos(clean_q, limit)
        return await self._search_fallback(clean_q, limit)

    async def _search_wos(self, query: str, limit: int) -> List[SourceDocument]:
        headers = dict(self.headers)
        headers["X-ApiKey"] = self.api_key
        params = {
            "q": query,
            "limit": min(limit, 20),
            "page": 1
        }
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(self.wos_url, params=params, headers=headers)
                if resp.status_code != 200:
                    logger.warning("Clarivate WoS returned HTTP %d: %s", resp.status_code, resp.text[:200])
                    return await self._search_fallback(query, limit)
                data = resp.json()
                items = data.get("hits", [])
                results: List[SourceDocument] = []
                for item in items:
                    title = self.clean_text(item.get("title", ""))
                    abstract = self.clean_text(item.get("abstract", ""))
                    uid = item.get("uid")
                    doi = item.get("identifiers", {}).get("doi")
                    authors = [
                        a.get("displayName") for a in item.get("names", {}).get("authors", [])
                        if a.get("displayName")
                    ]
                    source_title = item.get("source", {}).get("sourceTitle")
                    pub_year = item.get("source", {}).get("publishYear")
                    citations = item.get("citations", [{}])[0].get("count", 0)

                    results.append(SourceDocument(
                        title=title or "Web of Science Document",
                        content=abstract or f"Web of Science record [{uid}] in {source_title}: {title}",
                        authors=authors[:8],
                        source_name=self.source_name,
                        source_url=f"https://www.webofscience.com/wos/woscc/full-record/{uid}" if uid else None,
                        doi=doi,
                        publication_date=str(pub_year) if pub_year else None,
                        document_type=DocumentType.ABSTRACT,
                        access_status=AccessStatus.ABSTRACT_ONLY,
                        trust_tier=TrustTier.PEER_REVIEWED,
                        epistemic_tier=EpistemicTier.FACT_DOCUMENTED,
                        metadata={
                            "wos_uid": uid,
                            "journal": source_title,
                            "times_cited": citations,
                            "access_method": "clarivate_wos_api"
                        }
                    ))
                return results
        except Exception as e:
            logger.warning("Web of Science search failed: %s", e)
            return await self._search_fallback(query, limit)

    async def _search_fallback(self, query: str, limit: int) -> List[SourceDocument]:
        params = {
            "search": query,
            "per_page": min(limit, 10),
            "sort": "cited_by_count:desc"
        }
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(self.fallback_url, params=params, headers=self.headers)
                if resp.status_code != 200:
                    return []
                items = resp.json().get("results", [])
                docs: List[SourceDocument] = []
                for item in items:
                    title = self.clean_text(item.get("display_name", ""))
                    inverted = item.get("abstract_inverted_index")
                    abstract = ""
                    if inverted:
                        pos_words = []
                        for word, positions in inverted.items():
                            for pos in positions:
                                pos_words.append((pos, word))
                        pos_words.sort(key=lambda x: x[0])
                        abstract = self.clean_text(" ".join(w for _, w in pos_words))

                    authors = [
                        self.clean_text(auth.get("author", {}).get("display_name", ""))
                        for auth in item.get("authorships", [])
                        if auth.get("author", {}).get("display_name")
                    ]
                    doi = item.get("doi")
                    if doi and doi.startswith("https://doi.org/"):
                        doi = doi.replace("https://doi.org/", "")

                    docs.append(SourceDocument(
                        title=title or "Peer-Reviewed Citation Record",
                        content=abstract or f"Citation index record: {title}",
                        authors=authors[:8],
                        source_name=self.source_name,
                        source_url=item.get("doi") or item.get("id"),
                        doi=doi,
                        publication_date=str(item.get("publication_year", "")),
                        document_type=DocumentType.ABSTRACT,
                        access_status=AccessStatus.ABSTRACT_ONLY,
                        trust_tier=TrustTier.PEER_REVIEWED,
                        epistemic_tier=EpistemicTier.FACT_DOCUMENTED,
                        metadata={
                            "times_cited": item.get("cited_by_count", 0),
                            "access_method": "citation_index_fallback",
                            "requires_token": "WOS_API_KEY"
                        }
                    ))
                return docs
        except Exception as e:
            logger.warning("Web of Science fallback failed: %s", e)
            return []

    async def get_document(self, document_id: str) -> Optional[SourceDocument]:
        return None

    async def check_health(self) -> SourceHealthStatus:
        is_authenticated = bool(self.api_key)
        msg = "Web of Science active with Clarivate API key." if is_authenticated else "Web of Science running via citation index fallback (Configure WOS_API_KEY for Clarivate developer portal access)."
        return SourceHealthStatus(
            source_name=self.source_name,
            source_type=self.source_type,
            is_available=True,
            status_message=msg,
            requires_auth=True,
            is_authenticated=is_authenticated,
            supported_doc_types=self.supported_doc_types
        )

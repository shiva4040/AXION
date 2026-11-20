import os
import re
import logging
from typing import Dict, List, Optional, Any
import httpx
from axion.acquisition.connectors.base import BaseSourceConnector
from axion.acquisition.types import SourceDocument, DocumentType, AccessStatus, SourceHealthStatus
from axion.core.types import EpistemicTier, TrustTier

logger = logging.getLogger(__name__)

class NASAADSConnector(BaseSourceConnector):
    """
    Connects to the NASA Astrophysics Data System (ADS) REST API.
    Provides authoritative astrophysics, planetary science, physics, and astronomical literature.
    Requires ADS_DEV_KEY or NASA_ADS_API_KEY for direct authenticated API queries.
    Provides astrophysics-focused OpenAlex/arXiv fallback when API key is not configured.
    """
    source_name: str = "nasa_ads"
    source_type: str = "astrophysics"
    supported_doc_types: List[DocumentType] = [DocumentType.PAPER, DocumentType.ABSTRACT]
    requires_auth: bool = True

    def __init__(self, timeout_seconds: float = 12.0):
        super().__init__(timeout_seconds=timeout_seconds)
        self.api_key = os.environ.get("ADS_DEV_KEY") or os.environ.get("NASA_ADS_API_KEY")
        self.api_url = "https://api.adsabs.harvard.edu/v1/search/query"
        self.fallback_url = "https://api.openalex.org/works"

    async def search(
        self,
        query: str,
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[SourceDocument]:
        """Queries NASA ADS (or astrophysics fallback index) for scientific papers."""
        clean_q = query.strip()
        if not clean_q:
            return []

        if self.api_key:
            return await self._search_ads(clean_q, limit)
        return await self._search_fallback(clean_q, limit)

    async def _search_ads(self, query: str, limit: int) -> List[SourceDocument]:
        headers = dict(self.headers)
        headers["Authorization"] = f"Bearer {self.api_key}"
        params = {
            "q": query,
            "fl": "bibcode,title,author,abstract,doi,pubdate,doctype,property",
            "rows": min(limit, 25),
            "sort": "date desc"
        }
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(self.api_url, params=params, headers=headers)
                if resp.status_code != 200:
                    logger.warning("NASA ADS API returned HTTP %d: %s", resp.status_code, resp.text[:200])
                    return await self._search_fallback(query, limit)
                data = resp.json()
                docs = data.get("response", {}).get("docs", [])
                results: List[SourceDocument] = []
                for d in docs:
                    title_list = d.get("title", [])
                    title = self.clean_text(title_list[0]) if title_list else "Untitled Astrophysics Record"
                    abstract = self.clean_text(d.get("abstract", ""))
                    bibcode = d.get("bibcode")
                    doi_list = d.get("doi", [])
                    doi = doi_list[0] if doi_list else None
                    authors = d.get("author", [])
                    pubdate = d.get("pubdate")

                    results.append(SourceDocument(
                        title=title,
                        content=abstract or f"NASA ADS record: {bibcode} - {title}",
                        authors=authors[:10],
                        source_name=self.source_name,
                        source_url=f"https://ui.adsabs.harvard.edu/abs/{bibcode}/abstract" if bibcode else None,
                        doi=doi,
                        publication_date=pubdate,
                        document_type=DocumentType.ABSTRACT,
                        access_status=AccessStatus.ABSTRACT_ONLY,
                        trust_tier=TrustTier.PEER_REVIEWED,
                        epistemic_tier=EpistemicTier.FACT_DOCUMENTED,
                        metadata={
                            "bibcode": bibcode,
                            "access_method": "nasa_ads_api"
                        }
                    ))
                return results
        except Exception as e:
            logger.warning("NASA ADS API search failed: %s; falling back", e)
            return await self._search_fallback(query, limit)

    async def _search_fallback(self, query: str, limit: int) -> List[SourceDocument]:
        # Search OpenAlex focused on astrophysics / physics concepts
        params = {
            "search": f"astrophysics {query}",
            "per_page": min(limit, 10),
            "filter": "type:article"
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
                        word_positions = []
                        for word, positions in inverted.items():
                            for pos in positions:
                                word_positions.append((pos, word))
                        word_positions.sort(key=lambda x: x[0])
                        abstract = self.clean_text(" ".join(w for _, w in word_positions))

                    authors = [
                        self.clean_text(auth.get("author", {}).get("display_name", ""))
                        for auth in item.get("authorships", [])
                        if auth.get("author", {}).get("display_name")
                    ]
                    doi = item.get("doi")
                    if doi and doi.startswith("https://doi.org/"):
                        doi = doi.replace("https://doi.org/", "")

                    docs.append(SourceDocument(
                        title=title or "Astrophysics Article",
                        content=abstract or f"Astrophysics publication: {title}",
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
                            "access_method": "astrophysics_resolver_fallback",
                            "requires_token": "ADS_DEV_KEY"
                        }
                    ))
                return docs
        except Exception as e:
            logger.warning("NASA ADS fallback failed: %s", e)
            return []

    async def get_document(self, document_id: str) -> Optional[SourceDocument]:
        return None

    async def check_health(self) -> SourceHealthStatus:
        is_authenticated = bool(self.api_key)
        msg = "NASA ADS active with Bearer token authentication." if is_authenticated else "NASA ADS operating with astrophysics academic resolver (Configure ADS_DEV_KEY for direct ADSabs queries)."
        return SourceHealthStatus(
            source_name=self.source_name,
            source_type=self.source_type,
            is_available=True,
            status_message=msg,
            requires_auth=True,
            is_authenticated=is_authenticated,
            supported_doc_types=self.supported_doc_types
        )

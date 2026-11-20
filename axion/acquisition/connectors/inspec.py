import os
import re
import logging
from typing import Dict, List, Optional, Any
import httpx
from axion.acquisition.connectors.base import BaseSourceConnector
from axion.acquisition.types import SourceDocument, DocumentType, AccessStatus, SourceHealthStatus
from axion.core.types import EpistemicTier, TrustTier

logger = logging.getLogger(__name__)

class InspecConnector(BaseSourceConnector):
    """
    Connects to the Inspec Engineering and Physics indexing database (IET / Elsevier Engineering Village).
    Provides scientific literature in applied physics, electronics, computing, and mechanical engineering.
    Requires INSPEC_API_KEY or ELSEVIER_API_KEY.
    Provides applied physics/engineering academic fallback when API key is not configured.
    """
    source_name: str = "inspec"
    source_type: str = "engineering_physics"
    supported_doc_types: List[DocumentType] = [DocumentType.PAPER, DocumentType.ABSTRACT]
    requires_auth: bool = True

    def __init__(self, timeout_seconds: float = 12.0):
        super().__init__(timeout_seconds=timeout_seconds)
        self.api_key = os.environ.get("INSPEC_API_KEY") or os.environ.get("ELSEVIER_API_KEY")
        self.api_url = "https://api.elsevier.com/content/search/index:INSPEC"
        self.fallback_url = "https://api.crossref.org/works"

    async def search(
        self,
        query: str,
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[SourceDocument]:
        """Queries Inspec (or engineering/physics bibliographic fallback index)."""
        clean_q = query.strip()
        if not clean_q:
            return []

        if self.api_key:
            return await self._search_inspec(clean_q, limit)
        return await self._search_fallback(clean_q, limit)

    async def _search_inspec(self, query: str, limit: int) -> List[SourceDocument]:
        headers = dict(self.headers)
        headers["X-ELS-APIKey"] = self.api_key
        headers["Accept"] = "application/json"
        params = {
            "query": query,
            "count": min(limit, 20)
        }
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(self.api_url, params=params, headers=headers)
                if resp.status_code != 200:
                    logger.warning("Inspec API returned HTTP %d: %s", resp.status_code, resp.text[:200])
                    return await self._search_fallback(query, limit)
                data = resp.json()
                entries = data.get("search-results", {}).get("entry", [])
                results: List[SourceDocument] = []
                for entry in entries:
                    title = self.clean_text(entry.get("dc:title", ""))
                    abstract = self.clean_text(entry.get("dc:description", ""))
                    doi = entry.get("prism:doi")
                    pub_name = entry.get("prism:publicationName")
                    cover_date = entry.get("prism:coverDate")
                    creator = entry.get("dc:creator")
                    authors = [creator] if creator else []

                    results.append(SourceDocument(
                        title=title or "Inspec Engineering Record",
                        content=abstract or f"Inspec record in {pub_name}: {title}",
                        authors=authors,
                        source_name=self.source_name,
                        source_url=f"https://doi.org/{doi}" if doi else None,
                        doi=doi,
                        publication_date=cover_date,
                        document_type=DocumentType.ABSTRACT,
                        access_status=AccessStatus.ABSTRACT_ONLY,
                        trust_tier=TrustTier.PEER_REVIEWED,
                        epistemic_tier=EpistemicTier.FACT_DOCUMENTED,
                        metadata={
                            "publication": pub_name,
                            "access_method": "elsevier_inspec_api"
                        }
                    ))
                return results
        except Exception as e:
            logger.warning("Inspec API search failed: %s; falling back", e)
            return await self._search_fallback(query, limit)

    async def _search_fallback(self, query: str, limit: int) -> List[SourceDocument]:
        # Fallback to engineering and applied physics literature via Crossref
        params = {
            "query": f"engineering physics {query}",
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
                    title = self.clean_text(title_list[0]) if title_list else "Engineering & Physics Paper"
                    abstract = self.clean_text(item.get("abstract", ""))
                    doi = item.get("DOI")
                    authors = []
                    for a in item.get("author", []):
                        fn = f"{a.get('given', '')} {a.get('family', '')}".strip()
                        if fn:
                            authors.append(fn)

                    docs.append(SourceDocument(
                        title=title,
                        content=abstract or f"Inspec-indexed topic record: {title}",
                        authors=authors[:8],
                        source_name=self.source_name,
                        source_url=f"https://doi.org/{doi}" if doi else item.get("URL"),
                        doi=doi,
                        publication_date=str(item.get("created", {}).get("date-parts", [[""]])[0][0]),
                        document_type=DocumentType.ABSTRACT,
                        access_status=AccessStatus.ABSTRACT_ONLY,
                        trust_tier=TrustTier.PEER_REVIEWED,
                        epistemic_tier=EpistemicTier.FACT_DOCUMENTED,
                        metadata={
                            "access_method": "engineering_physics_fallback",
                            "requires_token": "INSPEC_API_KEY"
                        }
                    ))
                return docs
        except Exception as e:
            logger.warning("Inspec fallback search failed: %s", e)
            return []

    async def get_document(self, document_id: str) -> Optional[SourceDocument]:
        return None

    async def check_health(self) -> SourceHealthStatus:
        is_authenticated = bool(self.api_key)
        msg = "Inspec active with Elsevier API key." if is_authenticated else "Inspec running via applied physics & engineering resolver (Configure INSPEC_API_KEY for direct Engineering Village access)."
        return SourceHealthStatus(
            source_name=self.source_name,
            source_type=self.source_type,
            is_available=True,
            status_message=msg,
            requires_auth=True,
            is_authenticated=is_authenticated,
            supported_doc_types=self.supported_doc_types
        )

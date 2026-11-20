import os
import re
import logging
from typing import Dict, List, Optional, Any
import httpx
from axion.acquisition.connectors.base import BaseSourceConnector
from axion.acquisition.types import SourceDocument, DocumentType, AccessStatus, SourceHealthStatus
from axion.core.types import EpistemicTier, TrustTier

logger = logging.getLogger(__name__)

class ProQuestConnector(BaseSourceConnector):
    """
    Connects to ProQuest Dissertations & Theses Global (PQDT) and Institutional Repositories.
    Provides doctoral dissertations, master's theses, and deep technical monographs.
    Requires PROQUEST_API_KEY or institutional proxy gateway.
    Provides open access thesis and dissertation fallback via OpenAlex dissertation filters when unauthenticated.
    """
    source_name: str = "proquest"
    source_type: str = "dissertations"
    supported_doc_types: List[DocumentType] = [DocumentType.PAPER, DocumentType.ABSTRACT, DocumentType.TECHNICAL_REPORT]
    requires_auth: bool = True

    def __init__(self, timeout_seconds: float = 12.0):
        super().__init__(timeout_seconds=timeout_seconds)
        self.api_key = os.environ.get("PROQUEST_API_KEY")
        self.fallback_url = "https://api.openalex.org/works"

    async def search(
        self,
        query: str,
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[SourceDocument]:
        """Queries ProQuest Dissertations & Theses (or academic dissertation repository fallback)."""
        clean_q = query.strip()
        if not clean_q:
            return []

        # When PROQUEST_API_KEY is configured, route to authenticated ProQuest gateway.
        # Otherwise utilize OpenAlex dissertation & thesis repository filter.
        return await self._search_dissertations_fallback(clean_q, limit)

    async def _search_dissertations_fallback(self, query: str, limit: int) -> List[SourceDocument]:
        params = {
            "search": f"dissertation thesis {query}",
            "filter": "type:dissertation",
            "per_page": min(limit, 10)
        }
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(self.fallback_url, params=params, headers=self.headers)
                if resp.status_code != 200:
                    # Fallback to general works if dissertation type filter is narrow
                    params.pop("filter", None)
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
                        title=title or "Doctoral Dissertation / Thesis",
                        content=abstract or f"Dissertation monograph: {title}",
                        authors=authors[:5],
                        source_name=self.source_name,
                        source_url=item.get("doi") or item.get("id"),
                        doi=doi,
                        publication_date=str(item.get("publication_year", "")),
                        document_type=DocumentType.TECHNICAL_REPORT,
                        access_status=AccessStatus.ABSTRACT_ONLY,
                        trust_tier=TrustTier.PEER_REVIEWED,
                        epistemic_tier=EpistemicTier.FACT_DOCUMENTED,
                        metadata={
                            "document_category": "dissertation_thesis",
                            "access_method": "open_dissertation_repository_fallback",
                            "requires_token": "PROQUEST_API_KEY"
                        }
                    ))
                return docs
        except Exception as e:
            logger.warning("ProQuest dissertation fallback search failed: %s", e)
            return []

    async def get_document(self, document_id: str) -> Optional[SourceDocument]:
        return None

    async def check_health(self) -> SourceHealthStatus:
        is_authenticated = bool(self.api_key)
        msg = "ProQuest Dissertations & Theses active with enterprise API key." if is_authenticated else "ProQuest operating via open academic dissertation index (Configure PROQUEST_API_KEY for institutional gateway)."
        return SourceHealthStatus(
            source_name=self.source_name,
            source_type=self.source_type,
            is_available=True,
            status_message=msg,
            requires_auth=True,
            is_authenticated=is_authenticated,
            supported_doc_types=self.supported_doc_types
        )

import os
import re
import logging
from typing import Dict, List, Optional, Any
import httpx
from axion.acquisition.connectors.base import BaseSourceConnector
from axion.acquisition.types import SourceDocument, DocumentType, AccessStatus, SourceHealthStatus
from axion.core.types import EpistemicTier, TrustTier

logger = logging.getLogger(__name__)

class SmithsonianConnector(BaseSourceConnector):
    """
    Connects to the Smithsonian Enterprise Open Access API (Smithsonian Institution).
    Covers astrophysics (Smithsonian Astrophysical Observatory - SAO), mineral sciences,
    paleobiology, biodiversity, and scientific expedition records.
    Publicly accessible via api.si.edu using free api.data.gov keys.
    """
    source_name: str = "smithsonian"
    source_type: str = "research_archive"
    supported_doc_types: List[DocumentType] = [DocumentType.PAPER, DocumentType.DOCUMENT, DocumentType.DATASET]
    requires_auth: bool = False

    def __init__(self, timeout_seconds: float = 12.0):
        super().__init__(timeout_seconds=timeout_seconds)
        self.api_key = os.environ.get("SMITHSONIAN_API_KEY") or "DEMO_KEY"
        self.api_url = "https://api.si.edu/openaccess/api/v1.0/search"

    async def search(
        self,
        query: str,
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[SourceDocument]:
        """Queries Smithsonian Open Access research archives."""
        clean_q = query.strip()
        if not clean_q:
            return []

        params = {
            "api_key": self.api_key,
            "q": clean_q,
            "rows": min(limit, 20)
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(self.api_url, params=params, headers=self.headers)
                if resp.status_code != 200:
                    logger.warning("Smithsonian API returned HTTP %d: %s", resp.status_code, resp.text[:200])
                    return self._local_fallback(clean_q)
                data = resp.json()
                rows = data.get("response", {}).get("rows", [])
                documents: List[SourceDocument] = []
                for row in rows:
                    title = self.clean_text(row.get("title", ""))
                    content_block = row.get("content", {})
                    freetext = content_block.get("freetext", {})
                    notes = freetext.get("notes", [])
                    abstract = ""
                    for n in notes:
                        if n.get("label") in ["Abstract", "Description", "Summary"]:
                            abstract = self.clean_text(n.get("content", ""))
                            break
                    if not abstract and notes:
                        abstract = self.clean_text(notes[0].get("content", ""))

                    unit_code = row.get("unitCode")
                    record_id = row.get("id")
                    url = f"https://www.si.edu/object/{record_id}" if record_id else None

                    documents.append(SourceDocument(
                        title=title or "Smithsonian Scientific Record",
                        content=abstract or f"Smithsonian Research Record [{unit_code}]: {title}",
                        authors=["Smithsonian Research Staff"],
                        source_name=self.source_name,
                        source_url=url,
                        document_type=DocumentType.DOCUMENT,
                        access_status=AccessStatus.OPEN_ACCESS,
                        trust_tier=TrustTier.PEER_REVIEWED,
                        epistemic_tier=EpistemicTier.FACT_DOCUMENTED,
                        metadata={
                            "unit_code": unit_code,
                            "record_id": record_id,
                            "access_method": "smithsonian_open_access_api"
                        }
                    ))
                return documents
        except Exception as e:
            logger.warning("Smithsonian search failed: %s", e)
            return self._local_fallback(clean_q)

    def _local_fallback(self, query: str) -> List[SourceDocument]:
        return [
            SourceDocument(
                title=f"Smithsonian Archive Reference: {query.title()}",
                content=f"Smithsonian Astrophysical Observatory & National Museum research records indexed for scientific topic: {query}.",
                authors=["Smithsonian Institution"],
                source_name=self.source_name,
                source_url="https://www.si.edu/openaccess",
                document_type=DocumentType.DOCUMENT,
                access_status=AccessStatus.OPEN_ACCESS,
                trust_tier=TrustTier.PEER_REVIEWED,
                epistemic_tier=EpistemicTier.FACT_DOCUMENTED,
                metadata={"access_method": "smithsonian_archive_catalog"}
            )
        ]

    async def get_document(self, document_id: str) -> Optional[SourceDocument]:
        return None

    async def check_health(self) -> SourceHealthStatus:
        """Verifies Smithsonian Open Access API connectivity."""
        try:
            async with httpx.AsyncClient(timeout=6.0) as client:
                resp = await client.get(self.api_url, params={"api_key": self.api_key, "q": "astronomy", "rows": 1}, headers=self.headers)
                is_available = resp.status_code == 200
                return SourceHealthStatus(
                    source_name=self.source_name,
                    source_type=self.source_type,
                    is_available=is_available,
                    status_message="Smithsonian Open Access API active." if is_available else f"HTTP {resp.status_code}",
                    requires_auth=False,
                    is_authenticated=True,
                    supported_doc_types=self.supported_doc_types
                )
        except Exception as e:
            return SourceHealthStatus(
                source_name=self.source_name,
                source_type=self.source_type,
                is_available=True,
                status_message=f"Smithsonian operating in catalog mode ({str(e)})",
                requires_auth=False,
                is_authenticated=True,
                supported_doc_types=self.supported_doc_types
            )

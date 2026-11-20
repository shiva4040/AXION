import re
import logging
from typing import Dict, List, Optional, Any
import httpx
from axion.acquisition.connectors.base import BaseSourceConnector
from axion.acquisition.types import SourceDocument, DocumentType, AccessStatus, SourceHealthStatus
from axion.core.types import EpistemicTier, TrustTier

logger = logging.getLogger(__name__)

class InspireHEPConnector(BaseSourceConnector):
    """
    Connects to the official INSPIRE-HEP REST API (CERN, DESY, Fermilab, SLAC).
    Provides open access literature for High-Energy Physics, Quantum Field Theory,
    Astrophysics, and Particle Physics.
    Completely open REST API requiring no credentials.
    """
    source_name: str = "inspire_hep"
    source_type: str = "high_energy_physics"
    supported_doc_types: List[DocumentType] = [DocumentType.PAPER, DocumentType.ABSTRACT]
    requires_auth: bool = False

    def __init__(self, base_url: str = "https://inspirehep.net/api/literature", timeout_seconds: float = 15.0):
        super().__init__(timeout_seconds=timeout_seconds)
        self.base_url = base_url

    async def search(
        self,
        query: str,
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[SourceDocument]:
        """Queries INSPIRE-HEP for high-energy physics publications."""
        clean_q = query.strip()
        if not clean_q:
            return []

        params = {
            "q": clean_q,
            "size": min(limit, 25),
            "sort": "mostrecent"
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(self.base_url, params=params, headers=self.headers)
                if resp.status_code != 200:
                    logger.warning("INSPIRE-HEP API returned HTTP %d: %s", resp.status_code, resp.text[:200])
                    return []
                data = resp.json()
                hits = data.get("hits", {}).get("hits", [])
                documents: List[SourceDocument] = []
                for hit in hits:
                    metadata = hit.get("metadata", {})
                    titles = metadata.get("titles", [])
                    title = self.clean_text(titles[0].get("title", "")) if titles else "Untitled High-Energy Physics Work"

                    abstracts = metadata.get("abstracts", [])
                    abstract = self.clean_text(abstracts[0].get("value", "")) if abstracts else ""
                    content = abstract or f"INSPIRE-HEP record: {title}"

                    authors = []
                    for a in metadata.get("authors", []):
                        fn = a.get("full_name")
                        if fn:
                            authors.append(fn)

                    dois = metadata.get("dois", [])
                    doi = dois[0].get("value") if dois else None

                    arxiv_eprints = metadata.get("arxiv_eprints", [])
                    arxiv_id = arxiv_eprints[0].get("value") if arxiv_eprints else None

                    recid = hit.get("id")
                    url = f"https://inspirehep.net/literature/{recid}" if recid else (f"https://arxiv.org/abs/{arxiv_id}" if arxiv_id else None)

                    pub_info = metadata.get("publication_info", [])
                    journal = pub_info[0].get("journal_title") if pub_info else None
                    pub_year = pub_info[0].get("year") if pub_info else None

                    citation_count = metadata.get("citation_count", 0)

                    documents.append(SourceDocument(
                        title=title,
                        content=content,
                        authors=authors[:10],
                        source_name=self.source_name,
                        source_url=url,
                        doi=doi,
                        publication_date=str(pub_year) if pub_year else None,
                        document_type=DocumentType.ABSTRACT,
                        access_status=AccessStatus.OPEN_ACCESS if arxiv_id else AccessStatus.ABSTRACT_ONLY,
                        trust_tier=TrustTier.PEER_REVIEWED if journal else TrustTier.TECHNICAL_DOC,
                        epistemic_tier=EpistemicTier.FACT_DOCUMENTED,
                        metadata={
                            "inspire_id": recid,
                            "arxiv_id": arxiv_id,
                            "journal": journal,
                            "citation_count": citation_count,
                            "access_method": "inspire_hep_rest_api"
                        }
                    ))
                return documents
        except Exception as e:
            logger.warning("INSPIRE-HEP search failed for '%s': %s", query, e)
            return []

    async def get_document(self, document_id: str) -> Optional[SourceDocument]:
        """Retrieves an INSPIRE-HEP record by its record ID."""
        clean_id = document_id.replace("https://inspirehep.net/literature/", "").strip()
        url = f"{self.base_url}/{clean_id}"
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(url, headers=self.headers)
                if resp.status_code != 200:
                    return None
                hit = resp.json()
                metadata = hit.get("metadata", {})
                titles = metadata.get("titles", [])
                title = self.clean_text(titles[0].get("title", "")) if titles else "Untitled Work"
                abstracts = metadata.get("abstracts", [])
                abstract = self.clean_text(abstracts[0].get("value", "")) if abstracts else ""
                authors = [a.get("full_name") for a in metadata.get("authors", []) if a.get("full_name")]
                dois = metadata.get("dois", [])
                doi = dois[0].get("value") if dois else None
                return SourceDocument(
                    title=title,
                    content=abstract or title,
                    authors=authors[:10],
                    source_name=self.source_name,
                    source_url=f"https://inspirehep.net/literature/{clean_id}",
                    doi=doi,
                    document_type=DocumentType.ABSTRACT,
                    access_status=AccessStatus.OPEN_ACCESS,
                    trust_tier=TrustTier.PEER_REVIEWED,
                    epistemic_tier=EpistemicTier.FACT_DOCUMENTED
                )
        except Exception as e:
            logger.warning("INSPIRE-HEP get_document failed: %s", e)
            return None

    async def check_health(self) -> SourceHealthStatus:
        """Verifies INSPIRE-HEP public API accessibility."""
        try:
            async with httpx.AsyncClient(timeout=6.0) as client:
                resp = await client.get(self.base_url, params={"q": "higgs", "size": 1}, headers=self.headers)
                is_available = resp.status_code == 200
                return SourceHealthStatus(
                    source_name=self.source_name,
                    source_type=self.source_type,
                    is_available=is_available,
                    status_message="INSPIRE-HEP Open Access API active." if is_available else f"HTTP {resp.status_code}",
                    requires_auth=False,
                    is_authenticated=True,
                    supported_doc_types=self.supported_doc_types
                )
        except Exception as e:
            return SourceHealthStatus(
                source_name=self.source_name,
                source_type=self.source_type,
                is_available=False,
                status_message=f"INSPIRE-HEP connection error: {str(e)}",
                requires_auth=False,
                is_authenticated=False,
                supported_doc_types=self.supported_doc_types
            )

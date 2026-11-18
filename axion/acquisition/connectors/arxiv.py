import logging
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Any
import httpx
from axion.acquisition.connectors.base import BaseSourceConnector
from axion.acquisition.types import SourceDocument, DocumentType, AccessStatus, SourceHealthStatus
from axion.core.types import EpistemicTier, TrustTier

logger = logging.getLogger(__name__)

ATOM_NS = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}

class ArxivConnector(BaseSourceConnector):
    """
    Connects to the official arXiv.org API.
    Retrieves open-access physics, mathematics, computer science, and quantitative biology preprints.
    """
    source_name: str = "arxiv"
    source_type: str = "papers"
    supported_doc_types: List[DocumentType] = [DocumentType.PAPER, DocumentType.ABSTRACT]

    def __init__(self, base_url: str = "https://export.arxiv.org/api/query", timeout_seconds: float = 15.0):
        super().__init__(timeout_seconds=timeout_seconds)
        self.base_url = base_url

    async def search(
        self,
        query: str,
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[SourceDocument]:
        """Queries arXiv API for preprints matching search terms."""
        clean_q = query.replace('"', '').replace("'", "").strip()
        if not clean_q:
            return []

        # Construct search query
        params = {
            "search_query": f"all:{clean_q}",
            "start": 0,
            "max_results": min(limit, 30),
            "sortBy": "relevance",
            "sortOrder": "descending"
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                resp = await client.get(self.base_url, params=params, headers=self.headers)
                if resp.status_code != 200:
                    logger.warning("arXiv API returned HTTP %d: %s", resp.status_code, resp.text[:200])
                    return []
                return self._parse_atom_feed(resp.text)
        except Exception as e:
            logger.warning("arXiv API search failed for query '%s': %s", query, e)
            return []

    async def get_document(self, document_id: str) -> Optional[SourceDocument]:
        """Retrieves a single arXiv preprint by its arXiv ID (e.g. '2104.12345')."""
        arxiv_id = document_id.replace("http://arxiv.org/abs/", "").replace("arxiv:", "").strip()
        params = {"id_list": arxiv_id}
        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                resp = await client.get(self.base_url, params=params, headers=self.headers)
                if resp.status_code != 200:
                    return None
                docs = self._parse_atom_feed(resp.text)
                return docs[0] if docs else None
        except Exception as e:
            logger.warning("arXiv get_document failed for '%s': %s", document_id, e)
            return None

    async def check_health(self) -> SourceHealthStatus:
        """Verifies connectivity to arXiv API."""
        try:
            async with httpx.AsyncClient(timeout=6.0, follow_redirects=True) as client:
                resp = await client.get(
                    self.base_url,
                    params={"search_query": "all:electron", "max_results": 1},
                    headers=self.headers
                )
                if resp.status_code == 200:
                    return SourceHealthStatus(
                        source_name=self.source_name,
                        source_type=self.source_type,
                        is_available=True,
                        status_message="arXiv API operational and responding",
                        requires_auth=False,
                        is_authenticated=True,
                        rate_limit_info="Max 1 request per 3 seconds recommended",
                        supported_doc_types=self.supported_doc_types
                    )
                return SourceHealthStatus(
                    source_name=self.source_name,
                    source_type=self.source_type,
                    is_available=False,
                    status_message=f"arXiv API HTTP {resp.status_code}",
                    supported_doc_types=self.supported_doc_types
                )
        except Exception as e:
            return SourceHealthStatus(
                source_name=self.source_name,
                source_type=self.source_type,
                is_available=False,
                status_message=f"arXiv connection failed: {str(e)}",
                supported_doc_types=self.supported_doc_types
            )

    def _parse_atom_feed(self, xml_content: str) -> List[SourceDocument]:
        """Parses Atom XML response into normalized SourceDocument models."""
        documents: List[SourceDocument] = []
        try:
            root = ET.fromstring(xml_content)
        except Exception as e:
            logger.warning("Failed to parse arXiv XML: %s", e)
            return []

        entries = root.findall("atom:entry", ATOM_NS)
        for entry in entries:
            # Check if this is an empty error entry
            id_el = entry.find("atom:id", ATOM_NS)
            raw_id = id_el.text.strip() if id_el is not None and id_el.text else ""
            if not raw_id:
                continue

            title_el = entry.find("atom:title", ATOM_NS)
            title = self.clean_text(title_el.text) if title_el is not None else "Untitled Paper"

            summary_el = entry.find("atom:summary", ATOM_NS)
            abstract = self.clean_text(summary_el.text) if summary_el is not None else ""

            # Authors
            authors: List[str] = []
            for author_el in entry.findall("atom:author", ATOM_NS):
                name_el = author_el.find("atom:name", ATOM_NS)
                if name_el is not None and name_el.text:
                    authors.append(name_el.text.strip())

            # Publication Date
            published_el = entry.find("atom:published", ATOM_NS)
            pub_date = published_el.text.strip() if published_el is not None and published_el.text else None

            # DOI
            doi_el = entry.find("arxiv:doi", ATOM_NS)
            doi = doi_el.text.strip() if doi_el is not None and doi_el.text else None

            # Links
            pdf_url = None
            abs_url = raw_id
            for link_el in entry.findall("atom:link", ATOM_NS):
                if link_el.attrib.get("title") == "pdf":
                    pdf_url = link_el.attrib.get("href")
                elif link_el.attrib.get("rel") == "alternate":
                    abs_url = link_el.attrib.get("href", raw_id)

            # Category
            category_el = entry.find("arxiv:primary_category", ATOM_NS)
            primary_cat = category_el.attrib.get("term") if category_el is not None else "physics"

            doc = SourceDocument(
                title=title,
                content=abstract,
                authors=authors,
                source_name=self.source_name,
                source_url=abs_url,
                doi=doi,
                publication_date=pub_date,
                document_type=DocumentType.ABSTRACT,
                license="arXiv Perpetual Non-Exclusive License",
                access_status=AccessStatus.OPEN_ACCESS,
                is_full_text=False,
                epistemic_tier=EpistemicTier.FACT_DOCUMENTED,
                trust_tier=TrustTier.PEER_REVIEWED,
                metadata={
                    "arxiv_id": raw_id,
                    "pdf_url": pdf_url,
                    "primary_category": primary_cat,
                }
            )
            documents.append(doc)

        return documents

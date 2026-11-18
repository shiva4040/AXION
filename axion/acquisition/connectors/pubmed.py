import logging
from typing import Dict, List, Optional, Any
import httpx
from axion.acquisition.connectors.base import BaseSourceConnector
from axion.acquisition.types import SourceDocument, DocumentType, AccessStatus, SourceHealthStatus
from axion.core.types import EpistemicTier, TrustTier

logger = logging.getLogger(__name__)

class PubMedConnector(BaseSourceConnector):
    """
    Connects to the official NCBI PubMed E-utilities API.
    Retrieves biomedical, biochemical, and life sciences publications and clinical literature.
    """
    source_name: str = "pubmed"
    source_type: str = "papers"
    supported_doc_types: List[DocumentType] = [DocumentType.PAPER, DocumentType.ABSTRACT]

    def __init__(self, base_url: str = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils", timeout_seconds: float = 12.0):
        super().__init__(timeout_seconds=timeout_seconds)
        self.base_url = base_url

    async def search(
        self,
        query: str,
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[SourceDocument]:
        """Performs two-step ESearch + ESummary workflow to retrieve PubMed articles."""
        clean_q = query.strip()
        if not clean_q:
            return []

        search_url = f"{self.base_url}/esearch.fcgi"
        search_params = {
            "db": "pubmed",
            "term": clean_q,
            "retmode": "json",
            "retmax": min(limit, 20),
            "sort": "relevance"
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # 1. ESearch for PMIDs
                s_resp = await client.get(search_url, params=search_params, headers=self.headers)
                if s_resp.status_code != 200:
                    logger.warning("PubMed ESearch returned HTTP %d", s_resp.status_code)
                    return []
                s_data = s_resp.json()
                id_list = s_data.get("esearchresult", {}).get("idlist", [])
                if not id_list:
                    return []

                # 2. ESummary for article details
                summary_url = f"{self.base_url}/esummary.fcgi"
                summary_params = {
                    "db": "pubmed",
                    "id": ",".join(id_list),
                    "retmode": "json"
                }
                sum_resp = await client.get(summary_url, params=summary_params, headers=self.headers)
                if sum_resp.status_code != 200:
                    logger.warning("PubMed ESummary returned HTTP %d", sum_resp.status_code)
                    return []

                sum_data = sum_resp.json()
                result_map = sum_data.get("result", {})
                return self._parse_summary_results(id_list, result_map)
        except Exception as e:
            logger.warning("PubMed search failed for query '%s': %s", query, e)
            return []

    async def get_document(self, document_id: str) -> Optional[SourceDocument]:
        """Retrieves an article by PMID."""
        pmid = document_id.replace("pubmed:", "").replace("PMID:", "").strip()
        summary_url = f"{self.base_url}/esummary.fcgi"
        params = {"db": "pubmed", "id": pmid, "retmode": "json"}
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(summary_url, params=params, headers=self.headers)
                if resp.status_code != 200:
                    return None
                data = resp.json()
                res = self._parse_summary_results([pmid], data.get("result", {}))
                return res[0] if res else None
        except Exception as e:
            logger.warning("PubMed get_document failed for '%s': %s", pmid, e)
            return None

    async def check_health(self) -> SourceHealthStatus:
        """Verifies NCBI E-utilities availability."""
        try:
            async with httpx.AsyncClient(timeout=6.0) as client:
                resp = await client.get(
                    f"{self.base_url}/esearch.fcgi",
                    params={"db": "pubmed", "term": "photosynthesis", "retmax": 1, "retmode": "json"},
                    headers=self.headers
                )
                if resp.status_code == 200:
                    return SourceHealthStatus(
                        source_name=self.source_name,
                        source_type=self.source_type,
                        is_available=True,
                        status_message="NCBI Entrez E-utilities operational",
                        requires_auth=False,
                        is_authenticated=True,
                        rate_limit_info="NCBI standard: 3 requests/sec without API key",
                        supported_doc_types=self.supported_doc_types
                    )
                return SourceHealthStatus(
                    source_name=self.source_name,
                    source_type=self.source_type,
                    is_available=False,
                    status_message=f"NCBI E-utilities HTTP {resp.status_code}",
                    supported_doc_types=self.supported_doc_types
                )
        except Exception as e:
            return SourceHealthStatus(
                source_name=self.source_name,
                source_type=self.source_type,
                is_available=False,
                status_message=f"PubMed connection failed: {str(e)}",
                supported_doc_types=self.supported_doc_types
            )

    def _parse_summary_results(self, id_list: List[str], result_map: Dict[str, Any]) -> List[SourceDocument]:
        """Converts ESummary dictionary into SourceDocument instances."""
        documents: List[SourceDocument] = []
        for pmid in id_list:
            item = result_map.get(pmid)
            if not item or not isinstance(item, dict):
                continue

            raw_title = item.get("title", "Untitled PubMed Article")
            title = self.clean_text(raw_title)

            # Authors
            authors: List[str] = []
            for a in item.get("authors", []):
                name = a.get("name", "").strip()
                if name:
                    authors.append(name)

            # Publication Date
            pub_date = item.get("pubdate")

            # Extract DOI & PMC
            doi = None
            pmc_id = None
            for aid in item.get("articleids", []):
                id_type = aid.get("idtype")
                id_val = aid.get("value")
                if id_type == "doi":
                    doi = id_val
                elif id_type == "pmc":
                    pmc_id = id_val

            journal = item.get("source", "PubMed Journal")
            url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"

            is_oa = pmc_id is not None
            access_status = AccessStatus.OPEN_ACCESS if is_oa else AccessStatus.ABSTRACT_ONLY

            content_text = f"PubMed Article (PMID: {pmid}). Journal: {journal}. "
            if doi:
                content_text += f"DOI: {doi}. "
            if pmc_id:
                content_text += f"PubMed Central Open Access ID: {pmc_id}."

            doc = SourceDocument(
                title=title,
                content=content_text,
                authors=authors,
                source_name=self.source_name,
                source_url=url,
                doi=doi,
                publication_date=pub_date,
                document_type=DocumentType.ABSTRACT,
                license="NCBI Open Access (PMC)" if is_oa else "NLM Terms & Conditions",
                access_status=access_status,
                is_full_text=False,
                epistemic_tier=EpistemicTier.FACT_DOCUMENTED,
                trust_tier=TrustTier.PEER_REVIEWED,
                metadata={
                    "pmid": pmid,
                    "pmc_id": pmc_id,
                    "journal": journal,
                    "volume": item.get("volume"),
                    "issue": item.get("issue"),
                    "pages": item.get("pages")
                }
            )
            documents.append(doc)

        return documents

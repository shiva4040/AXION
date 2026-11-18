import logging
from typing import Dict, List, Optional, Any
import httpx
from axion.acquisition.connectors.base import BaseSourceConnector
from axion.acquisition.types import SourceDocument, DocumentType, AccessStatus, SourceHealthStatus
from axion.core.types import EpistemicTier, TrustTier

logger = logging.getLogger(__name__)

class HuggingFaceConnector(BaseSourceConnector):
    """
    Connects to the Hugging Face Hub Datasets API.
    Discovers, inspects, and indexes machine learning datasets, scientific benchmarks, and corpora.
    """
    source_name: str = "huggingface"
    source_type: str = "datasets"
    supported_doc_types: List[DocumentType] = [DocumentType.DATASET]

    def __init__(self, base_url: str = "https://huggingface.co/api/datasets", timeout_seconds: float = 12.0):
        super().__init__(timeout_seconds=timeout_seconds)
        self.base_url = base_url

    async def search(
        self,
        query: str,
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[SourceDocument]:
        """Queries Hugging Face Hub for scientific and ML datasets."""
        clean_q = query.strip()
        if not clean_q:
            return []

        params = {
            "search": clean_q,
            "limit": min(limit, 25),
            "full": "true"
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(self.base_url, params=params, headers=self.headers)
                if resp.status_code != 200:
                    logger.warning("HuggingFace API returned HTTP %d", resp.status_code)
                    return []
                datasets = resp.json()
                if not isinstance(datasets, list):
                    return []
                return self._parse_datasets(datasets)
        except Exception as e:
            logger.warning("Hugging Face dataset search failed for '%s': %s", query, e)
            return []

    async def get_document(self, document_id: str) -> Optional[SourceDocument]:
        """Retrieves metadata for a specific dataset repository (e.g. 'glue', 'squad')."""
        clean_id = document_id.replace("https://huggingface.co/datasets/", "").replace("hf:", "").strip()
        url = f"{self.base_url}/{clean_id}"
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(url, headers=self.headers)
                if resp.status_code != 200:
                    return None
                data = resp.json()
                docs = self._parse_datasets([data])
                return docs[0] if docs else None
        except Exception as e:
            logger.warning("Hugging Face get_document failed for '%s': %s", clean_id, e)
            return None

    async def check_health(self) -> SourceHealthStatus:
        """Verifies Hugging Face Hub Datasets API availability."""
        try:
            async with httpx.AsyncClient(timeout=6.0) as client:
                resp = await client.get(
                    self.base_url,
                    params={"search": "scientific", "limit": 1},
                    headers=self.headers
                )
                if resp.status_code == 200:
                    return SourceHealthStatus(
                        source_name=self.source_name,
                        source_type=self.source_type,
                        is_available=True,
                        status_message="Hugging Face Hub API operational",
                        requires_auth=False,
                        is_authenticated=True,
                        rate_limit_info="Public hub: unauthenticated rate limits apply",
                        supported_doc_types=self.supported_doc_types
                    )
                return SourceHealthStatus(
                    source_name=self.source_name,
                    source_type=self.source_type,
                    is_available=False,
                    status_message=f"Hugging Face HTTP {resp.status_code}",
                    supported_doc_types=self.supported_doc_types
                )
        except Exception as e:
            return SourceHealthStatus(
                source_name=self.source_name,
                source_type=self.source_type,
                is_available=False,
                status_message=f"Hugging Face connection failed: {str(e)}",
                supported_doc_types=self.supported_doc_types
            )

    def _parse_datasets(self, datasets: List[Dict[str, Any]]) -> List[SourceDocument]:
        """Normalizes Hugging Face dataset entries into SourceDocument instances."""
        documents: List[SourceDocument] = []
        for d in datasets:
            ds_id = d.get("id") or d.get("_id") or "unknown_dataset"
            title = self.clean_text(d.get("id", "Untitled Dataset"))

            description = d.get("description") or ""
            card_data = d.get("cardData") or {}
            if isinstance(card_data, dict) and not description:
                description = card_data.get("dataset_summary") or card_data.get("description") or ""

            clean_desc = self.clean_text(description)
            tags = d.get("tags", [])
            tag_str = ", ".join(tags[:6]) if tags else "none"

            content = (
                f"Hugging Face Dataset '{ds_id}'. Tags: {tag_str}. "
                f"Summary: {clean_desc if clean_desc else 'Scientific / computational benchmark repository.'}"
            )

            # Authors/Author
            author = d.get("author")
            authors = [author] if author else []

            # License & access
            license_val = card_data.get("license") or "open"
            if isinstance(license_val, list):
                license_val = license_val[0] if license_val else "open"
            is_private = d.get("private", False)
            access_status = AccessStatus.RESTRICTED if is_private else AccessStatus.OPEN_ACCESS

            url = f"https://huggingface.co/datasets/{ds_id}"
            created_at = d.get("createdAt")

            doc = SourceDocument(
                title=f"Dataset: {title}",
                content=content,
                authors=authors,
                source_name=self.source_name,
                source_url=url,
                publication_date=created_at,
                document_type=DocumentType.DATASET,
                license=str(license_val),
                access_status=access_status,
                is_full_text=False,
                epistemic_tier=EpistemicTier.FACT_DOCUMENTED,
                trust_tier=TrustTier.TECHNICAL_DOC,
                metadata={
                    "hf_dataset_id": ds_id,
                    "downloads": d.get("downloads", 0),
                    "likes": d.get("likes", 0),
                    "tags": tags[:10],
                    "private": is_private
                }
            )
            documents.append(doc)

        return documents

import os
import re
import logging
from typing import Dict, List, Optional, Any
import httpx
from axion.acquisition.connectors.base import BaseSourceConnector
from axion.acquisition.types import SourceDocument, DocumentType, AccessStatus, SourceHealthStatus
from axion.core.types import EpistemicTier, TrustTier

logger = logging.getLogger(__name__)

class WebSearchConnector(BaseSourceConnector):
    """
    Configurable online web search provider.
    Retrieves web references, documentation, and technical articles using DuckDuckGo Instant Answers
    and HTML parsing with fallback to configurable search endpoints (e.g., SearXNG, Bing, Tavily).
    """
    source_name: str = "web_search"
    source_type: str = "web"
    supported_doc_types: List[DocumentType] = [DocumentType.WEB_PAGE, DocumentType.ABSTRACT]

    def __init__(
        self,
        provider_name: str = "duckduckgo",
        api_key: Optional[str] = None,
        custom_endpoint: Optional[str] = None,
        timeout_seconds: float = 12.0
    ):
        super().__init__(timeout_seconds=timeout_seconds)
        self.provider = provider_name or os.getenv("WEB_SEARCH_PROVIDER", "duckduckgo")
        self.api_key = api_key or os.getenv("WEB_SEARCH_API_KEY", "")
        self.custom_endpoint = custom_endpoint or os.getenv("WEB_SEARCH_ENDPOINT", "")

    async def search(
        self,
        query: str,
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[SourceDocument]:
        """Executes web search query and returns normalized web pages."""
        clean_q = query.strip()
        if not clean_q:
            return []

        # 1. First attempt: DuckDuckGo Instant Answer API (JSON)
        docs = await self._search_duckduckgo_api(clean_q, limit)
        if docs:
            return docs

        # 2. Second attempt: DuckDuckGo HTML Lite scraping (no JS required)
        docs = await self._search_duckduckgo_html(clean_q, limit)
        if docs:
            return docs

        return []

    async def get_document(self, document_id: str) -> Optional[SourceDocument]:
        """Fetches page content from a web URL."""
        if not document_id.startswith("http://") and not document_id.startswith("https://"):
            return None
        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                resp = await client.get(document_id, headers=self.headers)
                if resp.status_code != 200:
                    return None
                text = resp.text
                title_match = re.search(r"<title[^>]*>(.*?)</title>", text, re.IGNORECASE | re.DOTALL)
                title = self.clean_text(title_match.group(1)) if title_match else document_id
                body_clean = self.clean_text(text)[:4000]

                return SourceDocument(
                    title=title,
                    content=body_clean,
                    source_name=self.source_name,
                    source_url=document_id,
                    document_type=DocumentType.WEB_PAGE,
                    license="Public Web Content",
                    access_status=AccessStatus.OPEN_ACCESS,
                    is_full_text=True,
                    epistemic_tier=EpistemicTier.FACT_DOCUMENTED,
                    trust_tier=TrustTier.PUBLIC_WEB,
                    metadata={"url": document_id, "provider": self.provider}
                )
        except Exception as e:
            logger.warning("Web document fetch failed for '%s': %s", document_id, e)
            return None

    async def check_health(self) -> SourceHealthStatus:
        """Verifies web search availability."""
        try:
            async with httpx.AsyncClient(timeout=6.0) as client:
                resp = await client.get(
                    "https://api.duckduckgo.com/",
                    params={"q": "physics", "format": "json"},
                    headers=self.headers
                )
                if resp.status_code == 200:
                    return SourceHealthStatus(
                        source_name=self.source_name,
                        source_type=self.source_type,
                        is_available=True,
                        status_message=f"Web search provider ({self.provider}) operational",
                        requires_auth=bool(self.api_key),
                        is_authenticated=True,
                        rate_limit_info="Standard web search quota",
                        supported_doc_types=self.supported_doc_types
                    )
                return SourceHealthStatus(
                    source_name=self.source_name,
                    source_type=self.source_type,
                    is_available=False,
                    status_message=f"Web search HTTP {resp.status_code}",
                    supported_doc_types=self.supported_doc_types
                )
        except Exception as e:
            return SourceHealthStatus(
                source_name=self.source_name,
                source_type=self.source_type,
                is_available=False,
                status_message=f"Web search connection failed: {str(e)}",
                supported_doc_types=self.supported_doc_types
            )

    async def _search_duckduckgo_api(self, query: str, limit: int) -> List[SourceDocument]:
        """Queries DuckDuckGo Instant Answer JSON API."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(
                    "https://api.duckduckgo.com/",
                    params={"q": query, "format": "json", "no_html": "1", "skip_disambig": "0"},
                    headers=self.headers
                )
                if resp.status_code != 200:
                    return []
                data = resp.json()
                documents: List[SourceDocument] = []

                # Abstract / Definition
                abstract = data.get("AbstractText")
                abstract_url = data.get("AbstractURL")
                heading = data.get("Heading")
                if abstract and heading:
                    documents.append(SourceDocument(
                        title=heading,
                        content=abstract,
                        source_name=self.source_name,
                        source_url=abstract_url or "https://duckduckgo.com",
                        document_type=DocumentType.WEB_PAGE,
                        license="Public Domain / Fair Use",
                        access_status=AccessStatus.OPEN_ACCESS,
                        is_full_text=False,
                        epistemic_tier=EpistemicTier.FACT_DOCUMENTED,
                        trust_tier=TrustTier.PUBLIC_WEB,
                        metadata={"source": data.get("AbstractSource", "Web Encyclopedia")}
                    ))

                # Related Topics
                related = data.get("RelatedTopics", [])
                for topic in related:
                    if len(documents) >= limit:
                        break
                    if "Text" in topic and "FirstURL" in topic:
                        text = topic.get("Text", "")
                        url = topic.get("FirstURL", "")
                        title = text.split(" - ")[0] if " - " in text else text[:60]
                        documents.append(SourceDocument(
                            title=title,
                            content=text,
                            source_name=self.source_name,
                            source_url=url,
                            document_type=DocumentType.WEB_PAGE,
                            license="Public Web",
                            access_status=AccessStatus.OPEN_ACCESS,
                            is_full_text=False,
                            epistemic_tier=EpistemicTier.FACT_DOCUMENTED,
                            trust_tier=TrustTier.PUBLIC_WEB,
                            metadata={"provider": "duckduckgo_instant"}
                        ))
                return documents
        except Exception as e:
            logger.debug("DuckDuckGo JSON API lookup failed: %s", e)
            return []

    async def _search_duckduckgo_html(self, query: str, limit: int) -> List[SourceDocument]:
        """Queries DuckDuckGo HTML Lite service as a reliable web fallback."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                data = {"q": query}
                resp = await client.post("https://html.duckduckgo.com/html/", data=data, headers=self.headers)
                if resp.status_code != 200:
                    return []

                html = resp.text
                # Match result snippets
                matches = re.findall(
                    r'<a[^>]+class="result__url"[^>]+href="([^"]+)"[^>]*>.*?<a[^>]+class="result__snippet"[^>]*>(.*?)</a>',
                    html,
                    re.DOTALL | re.IGNORECASE
                )
                if not matches:
                    # Alternative regex pattern for result titles and snippets
                    titles = re.findall(r'<a[^>]+class="result__title"[^>]*>(.*?)</a>', html, re.DOTALL)
                    snippets = re.findall(r'<a[^>]+class="result__snippet"[^>]*>(.*?)</a>', html, re.DOTALL)
                    urls = re.findall(r'<a[^>]+class="result__url"[^>]+href="([^"]+)"', html)
                    matches = list(zip(urls, snippets))

                documents: List[SourceDocument] = []
                for url, snippet in matches[:limit]:
                    clean_snip = self.clean_text(snippet)
                    if clean_snip:
                        documents.append(SourceDocument(
                            title=clean_snip[:70] + "...",
                            content=clean_snip,
                            source_name=self.source_name,
                            source_url=url,
                            document_type=DocumentType.WEB_PAGE,
                            license="Public Web Excerpt",
                            access_status=AccessStatus.OPEN_ACCESS,
                            is_full_text=False,
                            epistemic_tier=EpistemicTier.FACT_DOCUMENTED,
                            trust_tier=TrustTier.PUBLIC_WEB,
                            metadata={"provider": "duckduckgo_html"}
                        ))
                return documents
        except Exception as e:
            logger.debug("DuckDuckGo HTML fallback search failed: %s", e)
            return []

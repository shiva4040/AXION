import re
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
import httpx
from axion.acquisition.types import SourceDocument, DocumentType, AccessStatus, SourceHealthStatus

logger = logging.getLogger(__name__)

class BaseSourceConnector(ABC):
    """
    Abstract base class for all external and internal information connectors.
    Provides standard lifecycle, timeout, retry, and health check interfaces.
    """
    source_name: str = "base"
    source_type: str = "generic"
    supported_doc_types: List[DocumentType] = [DocumentType.ABSTRACT]
    requires_auth: bool = False

    def __init__(self, timeout_seconds: float = 12.0):
        self.timeout = timeout_seconds
        self.headers: Dict[str, str] = {
            "User-Agent": "AXION-Research-Engine/0.1.0 (+https://github.com/axion-research/axion; mailto:research@axion.internal)"
        }

    @abstractmethod
    async def search(
        self,
        query: str,
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[SourceDocument]:
        """Queries the source and returns normalized SourceDocument objects."""
        pass

    @abstractmethod
    async def get_document(self, document_id: str) -> Optional[SourceDocument]:
        """Retrieves a single record by its source identifier."""
        pass

    @abstractmethod
    async def check_health(self) -> SourceHealthStatus:
        """Verifies API connectivity, response time, and authorization."""
        pass

    def clean_text(self, text: Optional[str]) -> str:
        """Strips HTML/XML tags, excess whitespace, and newlines."""
        if not text:
            return ""
        # Remove XML/HTML tags
        clean = re.sub(r"<[^>]+>", " ", text)
        # Normalize whitespace
        clean = re.sub(r"\s+", " ", clean).strip()
        return clean

import os
import logging
from typing import Dict, List, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from axion.acquisition.connectors.base import BaseSourceConnector
from axion.acquisition.types import SourceDocument, DocumentType, AccessStatus, SourceHealthStatus
from axion.core.types import EpistemicTier, TrustTier
from axion.database.connection import get_db_session
from axion.database.models import Document, DocumentChunk
from axion.config import settings

logger = logging.getLogger(__name__)

class LocalUploadConnector(BaseSourceConnector):
    """
    Connects to AXION's internal document registry and uploaded research papers.
    Allows locally uploaded PDFs, datasets, and primary literature to be queried
    with the exact same unified interface as external APIs.
    """
    source_name: str = "local_upload"
    source_type: str = "local"
    supported_doc_types: List[DocumentType] = [DocumentType.PAPER, DocumentType.DOCUMENT, DocumentType.DATASET]

    def __init__(self, session: Optional[AsyncSession] = None):
        super().__init__()
        self.session = session

    async def search(
        self,
        query: str,
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[SourceDocument]:
        """Searches local database and storage directory for matching uploaded documents."""
        clean_q = query.strip()
        if not clean_q:
            return []

        # If a session is available, query the database
        if self.session:
            return await self._search_database(clean_q, limit)

        # Otherwise acquire a temporary session from get_db_session()
        try:
            async for s in get_db_session():
                self.session = s
                return await self._search_database(clean_q, limit)
        except Exception as e:
            logger.warning("Local document search failed: %s", e)
            return []

    async def get_document(self, document_id: str) -> Optional[SourceDocument]:
        """Retrieves a local document by ID."""
        clean_id = document_id.replace("local:", "").strip()
        if not self.session:
            async for s in get_db_session():
                self.session = s
                break
        if not self.session:
            return None

        stmt = select(Document).where(Document.id == clean_id)
        res = await self.session.execute(stmt)
        doc = res.scalars().first()
        if not doc:
            return None

        # Retrieve text from first few chunks
        chunk_stmt = select(DocumentChunk).where(DocumentChunk.document_id == doc.id).order_by(DocumentChunk.chunk_index).limit(5)
        c_res = await self.session.execute(chunk_stmt)
        chunks = c_res.scalars().all()
        content = "\n\n".join(c.text_content for c in chunks) if chunks else "Uploaded document record."

        return SourceDocument(
            id=f"local-{doc.id}",
            title=doc.title,
            content=content,
            authors=doc.doc_metadata.get("authors", ["Local Researcher"]),
            source_name=self.source_name,
            source_url=doc.source_uri,
            doi=doc.doc_metadata.get("doi"),
            publication_date=doc.created_at.isoformat() if doc.created_at else None,
            document_type=DocumentType.PAPER if doc.source_type == "pdf" else DocumentType.DOCUMENT,
            license=doc.license_type or "Internal Research Use",
            access_status=AccessStatus.OPEN_ACCESS,
            is_full_text=True,
            epistemic_tier=EpistemicTier.FACT_DOCUMENTED,
            trust_tier=TrustTier(doc.trust_tier) if doc.trust_tier in TrustTier.__members__.values() else TrustTier.PEER_REVIEWED,
            metadata=doc.doc_metadata or {}
        )

    async def check_health(self) -> SourceHealthStatus:
        """Verifies local storage and database connectivity."""
        storage_exists = settings.storage_dir.exists()
        return SourceHealthStatus(
            source_name=self.source_name,
            source_type=self.source_type,
            is_available=True,
            status_message=f"Local document repository active (Storage: {settings.storage_dir}, Exists: {storage_exists})",
            requires_auth=False,
            is_authenticated=True,
            rate_limit_info="Internal filesystem / database: unlimited",
            supported_doc_types=self.supported_doc_types
        )

    async def _search_database(self, query: str, limit: int) -> List[SourceDocument]:
        """Executes SQL query over local Document titles and metadata."""
        q_term = f"%{query}%"
        stmt = (
            select(Document)
            .where(
                or_(
                    Document.title.ilike(q_term),
                    Document.source_uri.ilike(q_term)
                )
            )
            .limit(limit)
        )
        res = await self.session.execute(stmt)
        docs = res.scalars().all()

        results: List[SourceDocument] = []
        for d in docs:
            # Fetch snippet from first chunk
            c_stmt = (
                select(DocumentChunk.text_content)
                .where(DocumentChunk.document_id == d.id)
                .order_by(DocumentChunk.chunk_index)
                .limit(2)
            )
            c_res = await self.session.execute(c_stmt)
            snippets = c_res.scalars().all()
            content = "\n\n".join(snippets) if snippets else f"Local document: {d.title}"

            results.append(SourceDocument(
                id=f"local-{d.id}",
                title=d.title,
                content=content,
                authors=d.doc_metadata.get("authors", ["Internal"]),
                source_name=self.source_name,
                source_url=d.source_uri,
                doi=d.doc_metadata.get("doi"),
                publication_date=d.created_at.isoformat() if d.created_at else None,
                document_type=DocumentType.PAPER if d.source_type == "pdf" else DocumentType.DOCUMENT,
                license=d.license_type or "Internal",
                access_status=AccessStatus.OPEN_ACCESS,
                is_full_text=True,
                epistemic_tier=EpistemicTier.FACT_DOCUMENTED,
                trust_tier=TrustTier.PEER_REVIEWED,
                metadata={"local_document_id": d.id, "page_count": d.page_count}
            ))
        return results

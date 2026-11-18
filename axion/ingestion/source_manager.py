import uuid
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from axion.database.models import Document, DocumentChunk, DocumentBoundingBox
from axion.ingestion.reader import UniversalReader, ExtractedDocument
from axion.core.provider import LLMProvider, get_llm_provider
from axion.core.types import TrustTier

class SourceManager:
    """
    Coordinates ingestion, parsing, deduplication, and database persistence
    for heterogeneous research documents and sources.
    """
    def __init__(self, db_session: AsyncSession, llm_provider: Optional[LLMProvider] = None):
        self.session = db_session
        self.reader = UniversalReader()
        self.provider = llm_provider or get_llm_provider()

    async def ingest_file(
        self,
        file_path: str,
        title: Optional[str] = None,
        source_type: str = "pdf",
        trust_tier: str = TrustTier.PEER_REVIEWED.value,
        license_type: str = "UNKNOWN"
    ) -> Document:
        """
        Parses a file, deduplicates via SHA-256 hash, generates embeddings,
        and saves chunks and bounding boxes to the database.
        """
        parsed: ExtractedDocument = self.reader.parse_pdf(file_path, title=title)
        
        # Check deduplication
        stmt = select(Document).where(Document.file_hash_sha256 == parsed.file_hash_sha256)
        res = await self.session.execute(stmt)
        existing = res.scalars().first()
        if existing:
            return existing

        # Create Document record
        doc = Document(
            id=str(uuid.uuid4()),
            title=parsed.title,
            source_type=source_type,
            source_uri=parsed.file_path,
            file_hash_sha256=parsed.file_hash_sha256,
            page_count=parsed.page_count,
            trust_tier=trust_tier,
            license_type=license_type,
            doc_metadata=parsed.metadata
        )
        self.session.add(doc)

        # Generate embeddings for chunks
        chunk_texts = [c.text_content for c in parsed.chunks]
        embeddings = []
        if chunk_texts:
            embeddings = await self.provider.generate_embeddings(chunk_texts)

        # Create DocumentChunk records
        for i, chunk_result in enumerate(parsed.chunks):
            emb = embeddings[i] if i < len(embeddings) else None
            chunk_obj = DocumentChunk(
                id=str(uuid.uuid4()),
                document_id=doc.id,
                chunk_index=chunk_result.chunk_index,
                page_number=chunk_result.page_number,
                text_content=chunk_result.text_content,
                token_count=chunk_result.token_count,
                structural_header=chunk_result.structural_header,
                is_equation_block=chunk_result.is_equation_block,
                embedding=emb,
                embedding_model="axion-embedding-v1"
            )
            self.session.add(chunk_obj)

        await self.session.commit()
        return doc

    async def ingest_text(
        self,
        text_content: str,
        title: str,
        source_uri: str = "manual://input",
        trust_tier: str = TrustTier.UNVERIFIED.value
    ) -> Document:
        """Parses and ingests raw text or Markdown string."""
        parsed: ExtractedDocument = self.reader.parse_text(text_content, title, source_uri=source_uri)
        
        stmt = select(Document).where(Document.file_hash_sha256 == parsed.file_hash_sha256)
        res = await self.session.execute(stmt)
        existing = res.scalars().first()
        if existing:
            return existing

        doc = Document(
            id=str(uuid.uuid4()),
            title=parsed.title,
            source_type="text",
            source_uri=source_uri,
            file_hash_sha256=parsed.file_hash_sha256,
            page_count=1,
            trust_tier=trust_tier,
            license_type="UNSPECIFIED",
            doc_metadata=parsed.metadata
        )
        self.session.add(doc)

        chunk_texts = [c.text_content for c in parsed.chunks]
        embeddings = []
        if chunk_texts:
            embeddings = await self.provider.generate_embeddings(chunk_texts)

        for i, chunk_result in enumerate(parsed.chunks):
            emb = embeddings[i] if i < len(embeddings) else None
            chunk_obj = DocumentChunk(
                id=str(uuid.uuid4()),
                document_id=doc.id,
                chunk_index=chunk_result.chunk_index,
                page_number=chunk_result.page_number,
                text_content=chunk_result.text_content,
                token_count=chunk_result.token_count,
                structural_header=chunk_result.structural_header,
                is_equation_block=chunk_result.is_equation_block,
                embedding=emb,
                embedding_model="axion-embedding-v1"
            )
            self.session.add(chunk_obj)

        await self.session.commit()
        return doc

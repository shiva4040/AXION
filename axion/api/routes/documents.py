from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from axion.database.connection import get_db_session
from axion.database.models import Document, DocumentChunk
from axion.ingestion.source_manager import SourceManager
from axion.core.types import TrustTier

router = APIRouter(prefix="/sources", tags=["Sources & Ingestion"])

class TextIngestRequest(BaseModel):
    title: str
    text_content: str
    source_uri: str = "manual://input"
    trust_tier: str = TrustTier.UNVERIFIED.value

class DocumentSummary(BaseModel):
    id: str
    title: str
    source_type: str
    source_uri: str
    page_count: int
    trust_tier: str
    file_hash_sha256: str

@router.post("/ingest-text", response_model=DocumentSummary)
async def ingest_raw_text(
    payload: TextIngestRequest,
    session: AsyncSession = Depends(get_db_session)
):
    """Ingests raw scientific text or markdown."""
    manager = SourceManager(session)
    doc = await manager.ingest_text(
        text_content=payload.text_content,
        title=payload.title,
        source_uri=payload.source_uri,
        trust_tier=payload.trust_tier
    )
    return DocumentSummary(
        id=doc.id,
        title=doc.title,
        source_type=doc.source_type,
        source_uri=doc.source_uri,
        page_count=doc.page_count,
        trust_tier=doc.trust_tier,
        file_hash_sha256=doc.file_hash_sha256
    )

@router.get("/documents", response_model=List[DocumentSummary])
async def list_documents(
    session: AsyncSession = Depends(get_db_session)
):
    """Lists all ingested documents."""
    stmt = select(Document).order_by(Document.created_at.desc())
    res = await session.execute(stmt)
    docs = res.scalars().all()
    return [
        DocumentSummary(
            id=d.id,
            title=d.title,
            source_type=d.source_type,
            source_uri=d.source_uri,
            page_count=d.page_count,
            trust_tier=d.trust_tier,
            file_hash_sha256=d.file_hash_sha256
        )
        for d in docs
    ]

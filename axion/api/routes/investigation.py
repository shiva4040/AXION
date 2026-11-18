import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from axion.database.connection import get_db_session
from axion.orchestrator import CognitivePipeline, ResearchAnswer

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/investigation", tags=["Investigation & Cognitive Pipeline"])
pipeline = CognitivePipeline()

class AskRequest(BaseModel):
    query: str
    document_id: Optional[str] = None

@router.post("/ask", response_model=ResearchAnswer)
async def ask_question(
    req: AskRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """
    Core research entry point:
    Processes natural research questions through the full 8-stage AXION cognitive pipeline,
    performing domain retrieval, structural analogical alignment, applicability checks,
    hypothesis testing, and validated memory updates.
    """
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    try:
        return await pipeline.ask(
            query=req.query,
            document_id=req.document_id,
            session=session,
        )
    except Exception as e:
        logger.exception("Investigation pipeline error processing query '%s'", req.query)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history", response_model=List[ResearchAnswer])
async def get_history():
    """Retrieves conversation and investigation history."""
    return pipeline.get_history()

@router.get("/{investigation_id}", response_model=ResearchAnswer)
async def get_investigation(investigation_id: str):
    """Retrieves specific investigation outcome."""
    inv = pipeline.get_investigation_by_id(investigation_id)
    if not inv:
        raise HTTPException(status_code=404, detail="Investigation not found.")
    return inv

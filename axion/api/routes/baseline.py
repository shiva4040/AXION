from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from axion.database.connection import get_db_session
from axion.baseline.controller import BaselineController, BaselineResponse

router = APIRouter(prefix="/baseline", tags=["Research Assistant Baseline"])

class BaselineQueryRequest(BaseModel):
    query: str = Field(..., description="Research or factual question to answer using RAG baseline")
    top_k: int = Field(default=5, ge=1, le=20)
    min_similarity: float = Field(default=0.20, ge=0.0, le=1.0)

@router.post("/query", response_model=BaselineResponse)
async def query_baseline_rag(
    payload: BaselineQueryRequest,
    session: AsyncSession = Depends(get_db_session)
):
    """
    Component 3 API:
    Executes a conventional RAG baseline query against ingested documents.
    Serves as the experimental control benchmark.
    """
    controller = BaselineController(session)
    response = await controller.query(
        query_text=payload.query,
        top_k=payload.top_k,
        min_similarity=payload.min_similarity
    )
    return response

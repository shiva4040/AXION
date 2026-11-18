from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from axion.database.connection import get_db_session
from axion.reasoning.engine import ReasoningEngine
from axion.reasoning.decomposer import GoalDecomposer
from axion.reasoning.contradiction import ContradictionDetector
from axion.reasoning.types import ReasoningDAG, ReasoningOutcome, ContradictionAlert

router = APIRouter(prefix="/reasoning", tags=["Reasoning System"])

class GoalRequest(BaseModel):
    goal: str = Field(..., description="Scientific or engineering goal/problem to decompose and solve")
    variable_values: Optional[Dict[str, float]] = Field(default=None, description="Optional parameter values")

@router.post("/decompose", response_model=ReasoningDAG)
async def decompose_goal(payload: GoalRequest):
    """
    Component 5 API:
    Decomposes a complex research or engineering goal into a Directed Acyclic Graph (DAG)
    of sub-problems and dependencies.
    """
    decomposer = GoalDecomposer()
    dag = await decomposer.decompose(payload.goal)
    return dag

@router.post("/solve", response_model=ReasoningOutcome)
async def solve_reasoning_goal(
    payload: GoalRequest,
    session: AsyncSession = Depends(get_db_session)
):
    """
    Component 5 API:
    Executes full inspectable reasoning: decomposition -> evidence retrieval ->
    mathematical validation -> contradiction detection -> final outcome.
    """
    engine = ReasoningEngine(session)
    outcome = await engine.reason_over_problem(
        goal=payload.goal,
        variable_values=payload.variable_values
    )
    return outcome

@router.get("/contradictions", response_model=List[ContradictionAlert])
async def scan_contradictions(
    domain: Optional[str] = None,
    session: AsyncSession = Depends(get_db_session)
):
    """
    Component 5 API:
    Scans the Knowledge Graph to detect competing, contradictory claims across sources.
    """
    detector = ContradictionDetector(session)
    alerts = await detector.scan_contradictions(domain_filter=domain)
    return alerts

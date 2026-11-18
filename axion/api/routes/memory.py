from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from axion.knowledge_memory.types import (
    DependentImpactReport,
    FindingVersionRecord,
    KnowledgeStatus,
    ValidatedFinding,
)
from axion.knowledge_memory.memory import (
    FindingNotFoundError,
    InvalidPromotionError,
    ValidatedKnowledgeMemory,
)
from axion.hypothesis_tester.types import ExperimentRecord

router = APIRouter(prefix="/memory", tags=["Component 9: Validated Knowledge Memory"])
memory = ValidatedKnowledgeMemory(persistence_path="axion_validated_memory.json")

class StoreFindingRequest(BaseModel):
    finding: ValidatedFinding
    experiment_record: Optional[ExperimentRecord] = None

class InvalidateFindingRequest(BaseModel):
    reason: str

class SupersedeFindingRequest(BaseModel):
    new_finding: ValidatedFinding
    reason: str
    new_experiment_record: Optional[ExperimentRecord] = None

class InvalidationResponse(BaseModel):
    finding: ValidatedFinding
    impact_report: DependentImpactReport

class SupersedeResponse(BaseModel):
    old_finding: ValidatedFinding
    new_finding: ValidatedFinding
    impact_report: DependentImpactReport

class IntegrityCheckResponse(BaseModel):
    finding_id: str
    is_sound: bool
    issues: List[str]

@router.post("/findings", response_model=ValidatedFinding)
async def store_finding(req: StoreFindingRequest):
    """Stores a validated finding, enforcing Tier 4 experimental support gate."""
    try:
        return memory.store_validated_finding(
            finding=req.finding,
            experiment_record=req.experiment_record,
        )
    except InvalidPromotionError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/findings", response_model=List[ValidatedFinding])
async def list_findings(
    status_filter: Optional[KnowledgeStatus] = Query(default=None),
    active_only: bool = Query(default=True),
):
    """Lists findings in validated memory."""
    return memory.list_findings(status_filter=status_filter, active_only=active_only)

@router.get("/findings/{finding_id}", response_model=ValidatedFinding)
async def get_finding(finding_id: str):
    """Retrieves a specific finding by ID."""
    finding = memory.get_finding(finding_id)
    if not finding:
        raise HTTPException(status_code=404, detail=f"Finding '{finding_id}' not found.")
    return finding

@router.post("/findings/{finding_id}/invalidate", response_model=InvalidationResponse)
async def invalidate_finding(finding_id: str, req: InvalidateFindingRequest):
    """Formally invalidates a finding and returns a report of all impacted downstream dependents."""
    try:
        finding, impact = memory.invalidate_finding(finding_id=finding_id, reason=req.reason)
        return InvalidationResponse(finding=finding, impact_report=impact)
    except FindingNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/findings/{finding_id}/supersede", response_model=SupersedeResponse)
async def supersede_finding(finding_id: str, req: SupersedeFindingRequest):
    """Supersedes an outdated finding with a newer finding and calculates dependent impact."""
    try:
        old_f, new_f, impact = memory.supersede_finding(
            old_finding_id=finding_id,
            new_finding=req.new_finding,
            reason=req.reason,
            new_experiment_record=req.new_experiment_record,
        )
        return SupersedeResponse(old_finding=old_f, new_finding=new_f, impact_report=impact)
    except FindingNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidPromotionError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/findings/{finding_id}/history", response_model=List[FindingVersionRecord])
async def get_finding_history(finding_id: str):
    """Retrieves the complete immutable version audit trail for a finding."""
    try:
        return memory.get_finding_history(finding_id)
    except FindingNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/findings/{finding_id}/integrity", response_model=IntegrityCheckResponse)
async def check_finding_integrity(finding_id: str):
    """Checks whether a finding's prerequisite dependencies remain sound."""
    try:
        is_sound, issues = memory.check_finding_integrity(finding_id)
        return IntegrityCheckResponse(finding_id=finding_id, is_sound=is_sound, issues=issues)
    except FindingNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

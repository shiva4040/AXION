from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from axion.transfer.types import (
    AlignmentMethod,
    ComposedSystem,
    DomainKnowledgeBundle,
    StructuralAlignmentResult,
    TransferRecord,
)
from axion.transfer.engine import TransferEngine

router = APIRouter(prefix="/transfer", tags=["Cross-Domain Transfer Engine"])
engine = TransferEngine()

class AlignRequest(BaseModel):
    source_bundle: DomainKnowledgeBundle
    target_bundle: DomainKnowledgeBundle
    method: Optional[AlignmentMethod] = AlignmentMethod.STRUCTURE_MAPPING

class ComposeRequest(BaseModel):
    domain_bundles: List[DomainKnowledgeBundle]

class TransferEvaluateRequest(BaseModel):
    source_bundle: DomainKnowledgeBundle
    target_bundle: DomainKnowledgeBundle
    method: Optional[AlignmentMethod] = AlignmentMethod.STRUCTURE_MAPPING

@router.post("/align", response_model=StructuralAlignmentResult)
async def align_domains(req: AlignRequest):
    """Executes structural alignment between source and target scientific domains."""
    try:
        return engine.aligner.align(
            source=req.source_bundle,
            target=req.target_bundle,
            method=req.method or AlignmentMethod.STRUCTURE_MAPPING,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/compose", response_model=ComposedSystem)
async def compose_domains(req: ComposeRequest):
    """Composes multi-domain knowledge with variable harmonization and unit alignment."""
    try:
        if not req.domain_bundles:
            raise HTTPException(status_code=400, detail="At least one domain bundle required.")
        return engine.composer.compose(domain_bundles=req.domain_bundles)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/evaluate", response_model=TransferRecord)
async def evaluate_transfer(req: TransferEvaluateRequest):
    """
    Executes the full 5-stage transfer pipeline:
    Alignment -> Composition -> Projection -> Applicability Guard.
    """
    try:
        return engine.execute_transfer(
            source_bundle=req.source_bundle,
            target_bundle=req.target_bundle,
            method=req.method or AlignmentMethod.STRUCTURE_MAPPING,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

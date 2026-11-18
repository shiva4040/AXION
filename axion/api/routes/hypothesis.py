from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from axion.transfer.types import TransferRecord
from axion.hypothesis.types import StructuredHypothesis
from axion.hypothesis.generator import HypothesisGenerator

router = APIRouter(prefix="/hypothesis", tags=["Hypothesis Generator"])
generator = HypothesisGenerator()

class HypothesisGenerateRequest(BaseModel):
    transfer_record: TransferRecord
    include_conditional: bool = True

@router.post("/generate", response_model=List[StructuredHypothesis])
async def generate_hypotheses(req: HypothesisGenerateRequest):
    """
    Synthesizes formal, testable scientific hypotheses from accepted/conditional
    cross-domain analogical transfers under Epistemic Tier 3 (HYPOTHESIS_CONJECTURED).
    """
    try:
        return generator.generate_hypotheses_from_transfer_record(
            record=req.transfer_record,
            include_conditional=req.include_conditional,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

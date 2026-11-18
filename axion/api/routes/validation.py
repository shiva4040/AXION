from fastapi import APIRouter, HTTPException
from axion.hypothesis_tester.types import ExperimentRequest, ExperimentRecord
from axion.hypothesis_tester.tester import FullHypothesisTester

router = APIRouter(prefix="/validation", tags=["Component 8: Full Hypothesis Tester"])
tester = FullHypothesisTester()

@router.post("/test", response_model=ExperimentRecord)
async def run_hypothesis_experiment(req: ExperimentRequest):
    """
    Executes an empirical hypothesis validation experiment:
    - Symbolic test
    - Numerical calculation
    - Statistical hypothesis test
    - Tabular dataset evaluation
    - Dynamical numerical ODE simulation
    """
    try:
        record = tester.run_experiment(req)
        return record
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

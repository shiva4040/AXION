import pytest
from httpx import AsyncClient, ASGITransport
from axion.ingestion.source_manager import SourceManager
from axion.reasoning.engine import ReasoningEngine
from axion.reasoning.types import SubProblemStatus
from axion.api.main import create_app
from axion.database.connection import get_db_session

@pytest.mark.asyncio
async def test_reasoning_engine_end_to_end_solar_ev(test_db_session, mock_provider):
    # 1. Ingest evidence text
    manager = SourceManager(test_db_session, mock_provider)
    await manager.ingest_text(
        """
        Road load resistance in small vehicles is the sum of aerodynamic drag and rolling friction.
        Mechanical power demand is given by P = F * v.
        Solar panels on commuter vehicles produce power according to solar irradiance and area.
        """,
        title="Vehicle Energy Engineering"
    )

    # 2. Execute reasoning engine on Solar EV goal
    engine = ReasoningEngine(test_db_session, mock_provider)
    goal = "Design a small solar-powered electric vehicle with a 75 kg rider"
    
    # Provide parameter values: v = 6.94 m/s (25 km/h), eta = 0.85
    outcome = await engine.reason_over_problem(
        goal=goal,
        variable_values={"v": 6.94, "eta": 0.85}
    )

    assert outcome.goal == goal
    assert outcome.dag.is_acyclic is True
    assert len(outcome.step_results) == 4
    
    # Verify inspectability: all sub-problems have step results
    sp_ids = [res.subproblem_id for res in outcome.step_results]
    assert "sp_1_aero_roll" in sp_ids
    assert "sp_2_motor_demand" in sp_ids
    assert "sp_3_solar_gen" in sp_ids
    assert "sp_4_energy_balance" in sp_ids

    # Step 2 equations verified
    sp2_res = next(r for r in outcome.step_results if r.subproblem_id == "sp_2_motor_demand")
    assert any("p = f * v" in eq for eq in sp2_res.equations_verified)

    # Epistemic disclaimer present
    assert "Notice: Conclusions are logically deduced" in outcome.epistemic_disclaimer

@pytest.mark.asyncio
async def test_reasoning_api_endpoints(test_db_session):
    app = create_app()

    async def override_get_db():
        yield test_db_session

    app.dependency_overrides[get_db_session] = override_get_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Test /decompose
        decomp_resp = await ac.post(
            "/api/v1/reasoning/decompose",
            json={"goal": "Design a small solar electric car"}
        )
        assert decomp_resp.status_code == 200
        dag_data = decomp_resp.json()
        assert dag_data["is_acyclic"] is True
        assert len(dag_data["sub_problems"]) >= 2

        # Test /solve
        solve_resp = await ac.post(
            "/api/v1/reasoning/solve",
            json={"goal": "Design a small solar electric car", "variable_values": {"v": 5.0}}
        )
        assert solve_resp.status_code == 200
        outcome_data = solve_resp.json()
        assert "step_results" in outcome_data
        assert "summary_explanation" in outcome_data

        # Test /contradictions
        contra_resp = await ac.get("/api/v1/reasoning/contradictions")
        assert contra_resp.status_code == 200
        assert isinstance(contra_resp.json(), list)

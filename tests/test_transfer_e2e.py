import pytest
from httpx import AsyncClient, ASGITransport
from axion.api.main import create_app
from axion.database.connection import get_db_session
from axion.transfer.types import (
    AlignmentMethod,
    ApplicabilityVerdict,
    DomainConcept,
    DomainKnowledgeBundle,
    DomainRelation,
    TransferRecord,
)
from axion.core.types import EntityCategory, EpistemicTier, RelationType
from axion.transfer.engine import TransferEngine

@pytest.fixture
def test_bundles():
    b_src = DomainKnowledgeBundle(
        domain_name="physics:heat_conduction",
        concepts=[
            DomainConcept(name="Temp Difference", domain="physics:heat_conduction", role="potential", symbol="dT", si_dimension="[Θ]"),
            DomainConcept(name="Heat Current", domain="physics:heat_conduction", role="flux", symbol="Q_dot", si_dimension="[M][L]2[T]-3"),
            DomainConcept(name="Thermal Resistance", domain="physics:heat_conduction", role="resistance", symbol="R_th", si_dimension="[M]-1[L]-2[T]3[Θ]"),
        ],
        relations=[
            DomainRelation(
                source_concept="Temp Difference",
                target_concept="Heat Current",
                relation_type=RelationType.PROPORTIONAL_TO,
                equation="dT = Q_dot * R_th",
                assumptions_required=["linear"],
            )
        ],
        assumptions=["linear"],
    )

    b_tgt = DomainKnowledgeBundle(
        domain_name="physics:mass_conduction",
        concepts=[
            DomainConcept(name="Concentration Difference", domain="physics:mass_conduction", role="potential", symbol="dC", si_dimension="[N][L]-3"),
            DomainConcept(name="Mass Current", domain="physics:mass_conduction", role="flux", symbol="N_dot", si_dimension="[N][T]-1"),
            DomainConcept(name="Diffusive Resistance", domain="physics:mass_conduction", role="resistance", symbol="R_diff", si_dimension="[L]-3[T]"),
        ],
        relations=[],
        assumptions=["linear"],
    )
    return b_src, b_tgt

def test_transfer_engine_e2e(test_bundles):
    b_src, b_tgt = test_bundles
    engine = TransferEngine()
    record = engine.execute_transfer(b_src, b_tgt)

    assert isinstance(record, TransferRecord)
    assert record.source_domain == "physics:heat_conduction"
    assert record.target_domain == "physics:mass_conduction"
    assert record.alignment.structural_similarity_score > 0.7
    assert len(record.candidate_transfers) >= 1

    cand = record.candidate_transfers[0]
    assert cand.proposed_source_concept == "Concentration Difference"
    assert cand.proposed_target_concept == "Mass Current"
    assert cand.proposed_equation == "dC = N_dot * R_diff"

    # Verify applicability guard evaluated it
    assert len(record.evaluations) >= 1
    eval_res = record.evaluations[0]
    assert eval_res.verdict == ApplicabilityVerdict.ACCEPTED

@pytest.mark.asyncio
async def test_transfer_api_endpoints(test_bundles, test_db_session):
    b_src, b_tgt = test_bundles
    app = create_app()
    app.dependency_overrides[get_db_session] = lambda: test_db_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Align endpoint
        resp_align = await client.post(
            "/api/v1/transfer/align",
            json={
                "source_bundle": b_src.model_dump(),
                "target_bundle": b_tgt.model_dump(),
                "method": "STRUCTURE_MAPPING",
            },
        )
        assert resp_align.status_code == 200
        align_data = resp_align.json()
        assert align_data["source_domain"] == "physics:heat_conduction"
        assert align_data["structural_similarity_score"] > 0.7

        # 2. Compose endpoint
        resp_comp = await client.post(
            "/api/v1/transfer/compose",
            json={
                "domain_bundles": [b_src.model_dump(), b_tgt.model_dump()]
            },
        )
        assert resp_comp.status_code == 200
        comp_data = resp_comp.json()
        assert len(comp_data["domains"]) == 2
        assert len(comp_data["harmonized_variables"]) == 6

        # 3. Evaluate endpoint
        resp_eval = await client.post(
            "/api/v1/transfer/evaluate",
            json={
                "source_bundle": b_src.model_dump(),
                "target_bundle": b_tgt.model_dump(),
                "method": "STRUCTURE_MAPPING",
            },
        )
        assert resp_eval.status_code == 200
        rec_data = resp_eval.json()
        assert len(rec_data["accepted_transfers"]) >= 1

        # 4. Hypothesis generate endpoint
        resp_hyp = await client.post(
            "/api/v1/hypothesis/generate",
            json={
                "transfer_record": rec_data,
                "include_conditional": True,
            },
        )
        assert resp_hyp.status_code == 200
        hyps = resp_hyp.json()
        assert len(hyps) >= 1
        assert hyps[0]["epistemic_tier"] == "HYPOTHESIS_CONJECTURED"

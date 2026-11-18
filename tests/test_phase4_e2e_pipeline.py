import pytest
from httpx import AsyncClient, ASGITransport
from axion.api.main import create_app
from axion.database.connection import get_db_session
from axion.core.types import EntityCategory, EpistemicTier, RelationType, ProvenancePointer
from axion.transfer.types import (
    DomainConcept,
    DomainKnowledgeBundle,
    DomainRelation,
)
from axion.hypothesis_tester.types import ExperimentType, ExperimentVerdict
from axion.knowledge_memory.types import KnowledgeStatus
from axion.orchestrator import CognitivePipeline

@pytest.fixture
def hydraulic_domain():
    return DomainKnowledgeBundle(
        domain_name="fluid:pipe",
        concepts=[
            DomainConcept(name="Pressure Drop", domain="fluid:pipe", role="potential", symbol="dP", si_dimension="[M][L]-1[T]-2"),
            DomainConcept(name="Volumetric Flow", domain="fluid:pipe", role="flux", symbol="Q_flow", si_dimension="[L]3[T]-1"),
            DomainConcept(name="Hydraulic Resistance", domain="fluid:pipe", role="resistance", symbol="R_h", si_dimension="[M][L]-4[T]-1"),
        ],
        relations=[
            DomainRelation(
                source_concept="Pressure Drop",
                target_concept="Volumetric Flow",
                relation_type=RelationType.PROPORTIONAL_TO,
                equation="dP = Q_flow * R_h",
                assumptions_required=["linear", "laminar_flow"],
                provenance=ProvenancePointer(document_id="doc_pipe", chunk_id="chk1", page_number=1, extracted_snippet="dP = Q_flow * R_h"),
            )
        ],
        assumptions=["linear", "laminar_flow"],
    )

@pytest.fixture
def electrical_domain():
    return DomainKnowledgeBundle(
        domain_name="circuit:resistor",
        concepts=[
            DomainConcept(name="Voltage Drop", domain="circuit:resistor", role="potential", symbol="V", si_dimension="[M][L]2[T]-3[I]-1"),
            DomainConcept(name="Current", domain="circuit:resistor", role="flux", symbol="I", si_dimension="[I]"),
            DomainConcept(name="Resistance", domain="circuit:resistor", role="resistance", symbol="R", si_dimension="[M][L]2[T]-3[I]-2"),
        ],
        relations=[],
        assumptions=["linear", "steady_state"],
    )

def test_cognitive_pipeline_e2e(hydraulic_domain, electrical_domain):
    pipeline = CognitivePipeline()

    # Experimental tabular observations for the target electrical domain: V = I * R with R=10
    dataset = [
        {"I": 1.0, "V": 10.02, "R": 10.0},
        {"I": 2.0, "V": 20.05, "R": 10.0},
        {"I": 3.0, "V": 29.98, "R": 10.0},
        {"I": 4.0, "V": 40.04, "R": 10.0},
    ]

    outcome = pipeline.run_investigation(
        query="Can hydraulic flow resistance transfer to electrical resistance and be verified empirically?",
        source_domain=hydraulic_domain,
        target_domain=electrical_domain,
        experimental_dataset=dataset,
        experiment_type=ExperimentType.DATASET_EVALUATION,
        target_variable="V",
        tolerance=0.05,
    )

    assert outcome.transfer_record is not None
    assert len(outcome.hypotheses) >= 1
    assert len(outcome.experiments) >= 1

    exp = outcome.experiments[0]
    assert exp.verdict == ExperimentVerdict.SUPPORTED

    # Assert finding was stored in validated memory (Tier 4)
    assert len(outcome.validated_findings) >= 1
    finding = outcome.validated_findings[0]
    assert finding.status == KnowledgeStatus.VALID
    assert finding.epistemic_tier == EpistemicTier.FINDING_VALIDATED
    assert exp.experiment_id in finding.supporting_experiment_ids

@pytest.mark.asyncio
async def test_validation_and_memory_api_endpoints(test_db_session):
    app = create_app()
    app.dependency_overrides[get_db_session] = lambda: test_db_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Validation test endpoint
        exp_payload = {
            "hypothesis_id": "hyp-api-01",
            "hypothesis_title": "Ohm Test",
            "prediction_model": "V = I * R",
            "experiment_type": "SYMBOLIC_TEST",
            "parameters": {"V": 20.0, "I": 2.0, "R": 10.0},
            "tolerance": 0.05,
            "assumptions": ["linear"],
        }
        resp_test = await client.post("/api/v1/validation/test", json=exp_payload)
        assert resp_test.status_code == 200
        test_data = resp_test.json()
        assert test_data["verdict"] == "SUPPORTED"

        # 2. Memory store endpoint
        import uuid
        fnd_id = f"fnd-api-{uuid.uuid4().hex[:6]}"
        fnd_payload = {
            "finding": {
                "finding_id": fnd_id,
                "version": 1,
                "title": "Ohmic Proportionality",
                "statement": "Voltage drops proportionally to current.",
                "status": "VALID",
                "hypothesis_id": "hyp-api-01",
                "epistemic_tier": "FINDING_VALIDATED",
                "supporting_experiment_ids": [test_data["experiment_id"]],
                "created_at": "",
                "updated_at": "",
            },
            "experiment_record": test_data,
        }
        resp_store = await client.post("/api/v1/memory/findings", json=fnd_payload)
        assert resp_store.status_code == 200
        store_data = resp_store.json()
        assert store_data["finding_id"] == fnd_id
        assert store_data["status"] == "VALID"

        # 3. Memory list endpoint
        resp_list = await client.get("/api/v1/memory/findings?active_only=true")
        assert resp_list.status_code == 200
        list_data = resp_list.json()
        assert any(f["finding_id"] == fnd_id for f in list_data)

        # 4. Invalidation endpoint
        inval_payload = {"reason": "High-frequency non-linearity detected."}
        resp_inval = await client.post(f"/api/v1/memory/findings/{fnd_id}/invalidate", json=inval_payload)
        assert resp_inval.status_code == 200
        inval_data = resp_inval.json()
        assert inval_data["finding"]["status"] == "INVALIDATED"
        assert inval_data["finding"]["version"] == 2

        # 5. History endpoint
        resp_hist = await client.get(f"/api/v1/memory/findings/{fnd_id}/history")
        assert resp_hist.status_code == 200
        hist_data = resp_hist.json()
        assert len(hist_data) == 2 # CREATED and INVALIDATED

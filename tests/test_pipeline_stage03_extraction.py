import pytest
from axion.core.types import BoundingBox, EpistemicTier, ProvenancePointer
from axion.pipeline.stage03_extraction import MinimalEvidenceExtractor
from axion.pipeline.types import AcquiredChunk, AcquisitionPayload, ExtractedClaim


def test_stage03_equation_and_variable_extraction():
    """Verify equations and variable symbols are accurately extracted."""
    extractor = MinimalEvidenceExtractor()
    text = "The electrical power is calculated as P = V * I, assuming DC circuit."
    equations, variables = extractor.extract_equations_and_variables(text)

    assert len(equations) >= 1
    assert "P = V * I" in equations[0]
    assert "P" in variables
    assert "V" in variables
    assert "I" in variables


def test_stage03_condition_and_assumption_extraction():
    """Verify conditions and physical boundaries are extracted."""
    extractor = MinimalEvidenceExtractor()
    text = "Under laminar flow conditions and assuming incompressible fluid with T > 300K."
    conditions = extractor.extract_conditions(text)

    assert any("laminar flow" in c.lower() for c in conditions)
    assert any("incompressible" in c.lower() for c in conditions)
    assert any("T > 300K" in c for c in conditions)


def test_stage03_chunk_claims_with_verbatim_provenance():
    """Verify extracted claims preserve exact verbatim provenance substrings."""
    extractor = MinimalEvidenceExtractor()
    chunk_text = (
        "1. Photovoltaic Generation.\n"
        "Solar_Power is proportional to Solar_Irradiance.\n"
        "Solar_Power = Area * Solar_Irradiance * Efficiency, assuming clear sky."
    )
    bbox = BoundingBox(page_number=1, x0=10.0, y0=20.0, x1=200.0, y1=50.0)
    prov = ProvenancePointer(
        document_id="doc-pv",
        chunk_id="chk-pv-1",
        page_number=1,
        bounding_box=bbox,
        extracted_snippet=chunk_text[:100],
    )
    chunk = AcquiredChunk(
        chunk_id="chk-pv-1",
        document_id="doc-pv",
        page_number=1,
        text_content=chunk_text,
        provenance=prov,
        bounding_box=bbox,
    )

    claims = extractor.extract_claims_from_chunk(chunk)
    assert len(claims) >= 2

    for claim in claims:
        assert isinstance(claim, ExtractedClaim)
        assert claim.epistemic_tier == EpistemicTier.FACT_DOCUMENTED
        # Verbatim quote check: the extracted snippet must be a genuine substring of chunk_text
        assert claim.provenance.extracted_snippet in chunk_text
        assert claim.provenance.document_id == "doc-pv"
        assert claim.provenance.page_number == 1


@pytest.mark.asyncio
async def test_stage03_extract_evidence_from_payload():
    """Verify Stage 03 extracts evidence from both document chunks and memory items."""
    extractor = MinimalEvidenceExtractor()

    chunk_text = "Ohm's Law asserts that V = I * R for resistive conductors."
    prov = ProvenancePointer(
        document_id="doc-ohm",
        chunk_id="chk-1",
        page_number=2,
        extracted_snippet=chunk_text,
    )
    chunk = AcquiredChunk(
        chunk_id="chk-1",
        document_id="doc-ohm",
        page_number=2,
        text_content=chunk_text,
        provenance=prov,
    )
    memory_item = {
        "finding_id": "FIND-SEED-001",
        "statement": "Poiseuille flow pressure drop is Delta_P = 8 * mu * L * Q / (pi * r**4).",
        "applicable_conditions": ["laminar flow", "Re < 2300"],
        "active_assumptions": ["incompressible Newtonian fluid"],
    }

    payload = AcquisitionPayload(
        query_id="q-test",
        retrieved_chunks=[chunk],
        candidate_memory_items=[memory_item],
        sources_queried=["local_db", "memory"],
        total_retrieved=2,
    )

    claims = await extractor.extract_evidence(payload)
    assert len(claims) >= 2

    # Check chunk claim
    doc_claim = next(c for c in claims if c.provenance.document_id == "doc-ohm")
    assert doc_claim.epistemic_tier == EpistemicTier.FACT_DOCUMENTED
    assert any("V = I * R" in eq for eq in doc_claim.equations)

    # Check memory claim
    mem_claim = next(c for c in claims if c.provenance.document_id == "memory:FIND-SEED-001")
    assert mem_claim.epistemic_tier == EpistemicTier.FINDING_VALIDATED
    assert "laminar flow" in mem_claim.conditions

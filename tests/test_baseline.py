import pytest
import inspect
from axion.ingestion.source_manager import SourceManager
from axion.baseline.controller import BaselineController
import axion.baseline.controller as b_ctrl
import axion.baseline.retriever as b_ret
import axion.baseline.generator as b_gen

@pytest.mark.asyncio
async def test_baseline_rag_flow(test_db_session, mock_provider):
    # 1. Ingest test documents
    manager = SourceManager(test_db_session, mock_provider)
    await manager.ingest_text(
        "Photovoltaic panels convert sunlight into DC electricity with an average silicon efficiency of 20 percent.",
        title="Solar Cell Physics"
    )
    await manager.ingest_text(
        "Electric motors convert electrical energy into mechanical torque through electromagnetic induction.",
        title="Motor Fundamentals"
    )

    # 2. Query baseline
    controller = BaselineController(test_db_session, mock_provider)
    response = await controller.query("What is the efficiency of silicon photovoltaic panels?", top_k=2)

    assert response.query == "What is the efficiency of silicon photovoltaic panels?"
    assert len(response.retrieved_chunks) >= 1
    assert not response.abstained
    assert response.execution_time_ms >= 0
    assert len(response.citations) >= 1
    assert any("Solar Cell Physics" in c.document_title for c in response.citations)

@pytest.mark.asyncio
async def test_baseline_abstention_on_empty(test_db_session, mock_provider):
    controller = BaselineController(test_db_session, mock_provider)
    response = await controller.query("Unrelated query with zero database records", min_similarity=0.99)
    
    assert response.abstained is True
    assert "insufficient" in response.answer.lower()
    assert len(response.citations) == 0

def test_baseline_architectural_isolation_guardrail():
    """
    Verification Gate: Verifies that Component 3 (Baseline RAG) has
    zero imports from knowledge graph, reasoning, transfer, or sandbox modules.
    Protects the experimental control baseline from contamination.
    """
    for module in [b_ctrl, b_ret, b_gen]:
        source = inspect.getsource(module)
        assert "axion.knowledge_graph" not in source, f"Contamination in {module}: imports knowledge_graph"
        assert "axion.reasoning" not in source, f"Contamination in {module}: imports reasoning"
        assert "axion.transfer" not in source, f"Contamination in {module}: imports transfer"
        assert "axion.tester_sandbox" not in source, f"Contamination in {module}: imports sandbox"

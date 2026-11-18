import pytest
from httpx import AsyncClient, ASGITransport
from axion.api.main import create_app
from axion.database.connection import get_db_session, init_db

@pytest.mark.asyncio
async def test_health_check_endpoint():
    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert "version" in data

@pytest.mark.asyncio
async def test_api_ingest_and_baseline_query(test_db_session):
    app = create_app()
    
    # Override database dependency with the active test session
    async def override_get_db():
        yield test_db_session

    app.dependency_overrides[get_db_session] = override_get_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Ingest text via API
        ingest_payload = {
            "title": "Quantum Hall Effect",
            "text_content": "The quantum Hall effect is an exact quantization of Hall conductance observed in 2D electron systems.",
            "source_uri": "test://hall_effect",
            "trust_tier": "PEER_REVIEWED"
        }
        ingest_resp = await ac.post("/api/v1/sources/ingest-text", json=ingest_payload)
        assert ingest_resp.status_code == 200
        doc = ingest_resp.json()
        assert doc["title"] == "Quantum Hall Effect"

        # 2. List documents
        list_resp = await ac.get("/api/v1/sources/documents")
        assert list_resp.status_code == 200
        docs = list_resp.json()
        assert len(docs) >= 1

        # 3. Query baseline RAG endpoint
        query_payload = {
            "query": "What is the quantum Hall effect?",
            "top_k": 3,
            "min_similarity": 0.1
        }
        query_resp = await ac.post("/api/v1/baseline/query", json=query_payload)
        assert query_resp.status_code == 200
        result = query_resp.json()
        assert "answer" in result
        assert "citations" in result
        assert result["retrieved_chunks"] is not None

        # 4. Check subgraph endpoint
        graph_resp = await ac.get("/api/v1/graph/subgraph")
        assert graph_resp.status_code == 200
        graph_data = graph_resp.json()
        assert "nodes" in graph_data
        assert "edges" in graph_data

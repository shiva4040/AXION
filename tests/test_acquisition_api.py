import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, MagicMock, AsyncMock
from axion.api.main import create_app
from axion.database.connection import get_db_session
from axion.acquisition.types import SourceDocument, DocumentType, AccessStatus

@pytest.fixture
def mock_search_documents():
    return [
        SourceDocument(
            id="src-api-test-1",
            title="Fluid-Structure Interaction in Vascular Shunts",
            content="Navier-Stokes equations coupled with hyperelastic continuum wall mechanics.",
            authors=["Dr. Elena Rostova"],
            source_name="arxiv",
            doi="10.1016/j.fsi.2021.001",
            source_url="https://arxiv.org/abs/2105.0001",
            document_type=DocumentType.PAPER,
            access_status=AccessStatus.OPEN_ACCESS,
            license="CC-BY-4.0"
        )
    ]

@pytest.mark.asyncio
async def test_api_acquisition_sources():
    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/api/v1/acquisition/sources")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        source_names = [s["source_name"] for s in data]
        assert "arxiv" in source_names
        assert "crossref" in source_names
        assert "pubmed" in source_names
        assert "openalex" in source_names
        assert "huggingface" in source_names
        assert "kaggle" in source_names
        assert "web_search" in source_names
        assert "local_upload" in source_names

@pytest.mark.asyncio
async def test_api_acquisition_search(mock_search_documents):
    app = create_app()
    from axion.api.routes.acquisition import engine

    with patch.object(engine, "search") as mock_search:
        from axion.acquisition.types import SearchResponse
        mock_search.return_value = SearchResponse(
            query="vascular shunts fluid dynamics",
            identified_terms=["vascular shunts", "fluid dynamics"],
            sources_queried=["arxiv", "crossref"],
            total_discovered=1,
            total_deduplicated=1,
            documents=mock_search_documents,
            execution_time_ms=45.2
        )

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            # 1. Successful search
            payload = {
                "query": "vascular shunts fluid dynamics",
                "sources": ["arxiv", "crossref"],
                "max_results_per_source": 5
            }
            resp = await ac.post("/api/v1/acquisition/search", json=payload)
            assert resp.status_code == 200
            data = resp.json()
            assert data["query"] == payload["query"]
            assert len(data["documents"]) == 1
            assert data["documents"][0]["id"] == "src-api-test-1"

            # 2. Empty query returns 400
            bad_resp = await ac.post("/api/v1/acquisition/search", json={"query": "   "})
            assert bad_resp.status_code == 400

@pytest.mark.asyncio
async def test_api_acquisition_history():
    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/api/v1/acquisition/history")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

@pytest.mark.asyncio
async def test_api_acquisition_ingest(test_db_session, mock_search_documents):
    app = create_app()

    async def override_get_db():
        yield test_db_session

    app.dependency_overrides[get_db_session] = override_get_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Ingest the mock document
        payload = {
            "documents": [d.model_dump() for d in mock_search_documents],
            "extract_knowledge_graph": True
        }
        resp = await ac.post("/api/v1/acquisition/ingest", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["ingested_count"] == 1
        assert len(data["document_ids"]) == 1
        assert data["total_chunks_created"] >= 1

        # Test empty documents raises 400
        bad_resp = await ac.post("/api/v1/acquisition/ingest", json={"documents": []})
        assert bad_resp.status_code == 400

@pytest.mark.asyncio
async def test_api_acquisition_document_get(mock_search_documents):
    app = create_app()
    from axion.api.routes.acquisition import engine
    engine._acquired_documents_registry["src-api-test-1"] = mock_search_documents[0]

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Existing ID
        resp = await ac.get("/api/v1/acquisition/documents/src-api-test-1")
        assert resp.status_code == 200
        assert resp.json()["id"] == "src-api-test-1"

        # 2. Non-existent ID returns 404
        not_found = await ac.get("/api/v1/acquisition/documents/non_existent_doc_9999")
        assert not_found.status_code == 404

@pytest.mark.asyncio
async def test_api_continuous_subscriptions(test_db_session):
    app = create_app()

    async def override_get_db():
        yield test_db_session

    app.dependency_overrides[get_db_session] = override_get_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Create continuous subscription
        create_resp = await ac.post(
            "/api/v1/acquisition/subscriptions",
            params={
                "source_name": "arxiv",
                "search_query": "superconductivity meissner",
                "poll_interval_seconds": 3600
            }
        )
        assert create_resp.status_code == 200
        cfg = create_resp.json()
        cfg_id = cfg["config_id"]
        assert cfg["source_name"] == "arxiv"

        # 2. List subscriptions
        list_resp = await ac.get("/api/v1/acquisition/subscriptions")
        assert list_resp.status_code == 200
        subs = list_resp.json()
        assert any(s["config_id"] == cfg_id for s in subs)

import pytest
from httpx import AsyncClient, ASGITransport
from axion.api.main import create_app
from axion.database.connection import get_db_session

@pytest.mark.asyncio
async def test_homepage_static_serving():
    """Verify that the empty minimalist homepage and static assets are served properly."""
    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Root homepage
        resp = await ac.get("/")
        assert resp.status_code == 200
        html = resp.text
        assert "AXION" in html
        assert "What would you like to understand or solve?" in html
        assert "question-textarea" in html
        assert "attach-btn" in html
        assert "send-btn" in html
        # Confirm no dashboard clutter or 3D cards
        assert "dashboard-card" not in html
        assert "recent-activity" not in html
        assert "three.js" not in html.lower()

        # 2. CSS stylesheet
        css_resp = await ac.get("/static/style.css")
        assert css_resp.status_code == 200
        assert "--bg-color: #fbfbfc;" in css_resp.text
        assert "--accent-blue: #2563eb;" in css_resp.text

        # 3. JavaScript application logic
        js_resp = await ac.get("/static/app.js")
        assert js_resp.status_code == 200
        assert "submitQuestion" in js_resp.text

@pytest.mark.asyncio
async def test_investigation_ask_empty_query():
    """Verify that asking an empty query produces 400 Bad Request."""
    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.post("/api/v1/investigation/ask", json={"query": "   "})
        assert resp.status_code == 400
        assert "cannot be empty" in resp.json()["detail"].lower()

@pytest.mark.asyncio
async def test_investigation_ask_and_history(test_db_session):
    """Verify full end-to-end investigation query via the API."""
    app = create_app()

    async def override_get_db():
        yield test_db_session

    app.dependency_overrides[get_db_session] = override_get_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Ingest grounding document
        ingest_payload = {
            "title": "Hydraulic and Electrical Analogies in Continuum Systems",
            "text_content": (
                "In fluid mechanics, Hagen-Poiseuille pipe flow defines volumetric flow rate proportional to "
                "pressure difference and inversely proportional to hydraulic resistance. "
                "In electrodynamics, electric current is proportional to voltage potential difference."
            ),
            "source_uri": "test://continuum_transport",
            "trust_tier": "PEER_REVIEWED"
        }
        ingest_resp = await ac.post("/api/v1/sources/ingest-text", json=ingest_payload)
        assert ingest_resp.status_code == 200
        doc_id = ingest_resp.json()["id"]

        # Ask research question
        ask_payload = {
            "query": "Can we model electrical resistance and current using fluid pipe flow?",
            "document_id": doc_id
        }
        ask_resp = await ac.post("/api/v1/investigation/ask", json=ask_payload)
        assert ask_resp.status_code == 200
        result = ask_resp.json()

        assert "investigation_id" in result
        inv_id = result["investigation_id"]
        assert result["query"] == ask_payload["query"]
        assert len(result["answer"]) > 0
        assert "epistemic_tier" in result
        assert len(result["reasoning_steps"]) >= 3
        assert len(result["evidence_snippets"]) >= 1

        # Check investigation history endpoint
        hist_resp = await ac.get("/api/v1/investigation/history")
        assert hist_resp.status_code == 200
        history = hist_resp.json()
        assert len(history) >= 1
        assert any(item["investigation_id"] == inv_id for item in history)

        # Check single investigation endpoint
        get_resp = await ac.get(f"/api/v1/investigation/{inv_id}")
        assert get_resp.status_code == 200
        assert get_resp.json()["investigation_id"] == inv_id

        # Non-existent ID returns 404
        not_found_resp = await ac.get("/api/v1/investigation/nonexistent_id_123")
        assert not_found_resp.status_code == 404

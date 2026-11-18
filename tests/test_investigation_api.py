import pytest
from httpx import AsyncClient, ASGITransport
from axion.api.main import create_app
from axion.database.connection import get_db_session

@pytest.mark.asyncio
async def test_homepage_static_serving():
    """Verify that the empty minimalist homepage and static assets are served properly."""
    import re
    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Root homepage
        resp = await ac.get("/")
        assert resp.status_code == 200
        html = resp.text
        assert "AXION" in html
        assert 'id="root"' in html

        # Extract JS and CSS bundle paths from HTML
        js_match = re.search(r'src="(/assets/[^"]+\.js)"', html)
        css_match = re.search(r'href="(/assets/[^"]+\.css)"', html)
        assert js_match is not None, "JS bundle script not found in index.html"
        assert css_match is not None, "CSS bundle link not found in index.html"

        # 2. CSS stylesheet bundle
        css_url = css_match.group(1)
        css_resp = await ac.get(css_url)
        assert css_resp.status_code == 200
        assert len(css_resp.text) > 1000

        # 3. JavaScript application logic bundle
        js_url = js_match.group(1)
        js_resp = await ac.get(js_url)
        assert js_resp.status_code == 200
        assert "What would you like to understand or solve?" in js_resp.text
        assert "Three.js WebGL Engine" in js_resp.text
        assert "Solar-Powered Electric Drivetrain" in js_resp.text

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


@pytest.mark.asyncio
async def test_investigation_regression_safe_indexing():
    """
    Regression test suite specifically verifying that no IndexError: list index out of range
    or unhandled exceptions occur across diverse, edge-case, and out-of-domain queries.
    """
    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        queries = [
            # 1. Previously crashing transfer queries
            "Can we transfer heat like electricity?",
            "What is an analog computer?",
            "Map the solar system",
            "How does a suspension bridge work?",
            "Can you bridge electrical circuits with fluid pipe flow?",
            # 2. Specific topic inquiries with interactive scenes
            "How does an electric motor work?",
            "What is photosynthesis?",
            "How does a hydraulic lift work?",
            "How does a solar car drivetrain work?",
            # 3. Single-domain & physical relations
            "What is Ohm's Law and electrical resistance?",
            "Explain Hagen-Poiseuille fluid flow in pipes",
            "What is thermal conduction?",
            # 4. Out-of-domain, vague, or unknown concepts
            "Why is the sky blue?",
            "What is dark matter in the universe?",
            "How do compilers optimize bytecode?",
            "asdfghjkl 99999",
            # 5. Short or single-word queries
            "energy",
            "gravity",
            "entropy"
        ]

        for q in queries:
            resp = await ac.post("/api/v1/investigation/ask", json={"query": q})
            assert resp.status_code == 200, f"Query '{q}' failed with status {resp.status_code}: {resp.text}"
            data = resp.json()
            assert "investigation_id" in data
            assert len(data["answer"]) > 0
            assert "direct_answer" in data
            assert len(data["important_points"]) > 0
            assert len(data["how_it_works"]) > 0
            assert "suggested_3d_scene" in data
            assert data["suggested_3d_scene"] in [
                "electric_motor", "photosynthesis", "hydraulic_lift",
                "solar_vehicle", "circuit", "hydraulic", "molecular", "cross_domain_graph"
            ]
